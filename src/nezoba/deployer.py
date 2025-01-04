"""Install and deploy the Nez-Oba board's software using the Arduino CLI."""

import logging
import pathlib
import os
import re
import shutil
import subprocess
import tempfile
from typing import Callable, Optional, Union
import zipfile
from importlib import resources as impresources
import yaml

import libs as nezoba_libs
_patch_file = impresources.files(nezoba_libs) / "HID-Project.h.patch"



class Runner:
    """
    Run command line commands and capture their output.

    Attributes:
        wait: Prompt the user to press Enter before running the command?
    """

    wait: bool

    def __init__(self, wait: bool = True):
        self.wait = wait

    def is_cmd_available(self, cmd: str, fail_on_false: bool=True) -> bool:
        """If `cmd` is a command that is reachable within the OS's path and executable,
        return True. Otherwise, log an error message and return False. If `fail_on_false`,
        raise an exception with the error message if `cmd` is not available.
        """
        if shutil.which(cmd) is None:
            msg = f"Command {cmd} is not available."
            logging.error(msg)
            if fail_on_false:
                raise FileNotFoundError(msg)
            return False
        return True

    def run_cmd(self, cmds: Union[str, list[str], Callable],
                message: Optional[str] = None, shell: bool = False,
                **kwargs):
        """
        Display and run command line `cmd_list`, and return result.
        
        The command line can be given in three forms:
        - as a single string, which is just used as command line
        - as a list of strings, which are joined with spaces to form the command line
        - as a callable, which is called without arguments
        
        Before running the command, display `message` if given, 
        or a string representation of the command line if not.
    
        Arguments:
            cmds: The command line to run, as a string, a list of strings, or a callable.
            message: A message to display before running the command.
            shell: Run the command in a shell?
            kwargs: Additional keyword arguments for `subprocess.run`.
        
        Returns:
            The result of the command.
        """
        call = False
        cmd_line = ""
        if isinstance(cmds, list):
            cmd_line = " ".join(cmds)
        elif isinstance(cmds, str):
            cmd_line = cmds
        else:
            call = True
        print()
        msg = message if message else str(cmds) if call else cmd_line
        print("[NEZ] Running:" + "\n" + msg)
        if self.wait:
            input("--> Press Enter to run or Ctrl-C to abort.")
        if call:
            res = cmds()
        elif shell:
            res = subprocess.run(cmd_line, check=False, shell=True, **kwargs)
        else:
            res = subprocess.run(cmds, check=False, **kwargs)
        print()
        return res

    def github_download(self, username: str, project: str, sha: str) -> str:
        """
        Download snapshot of GitHub repository as zip into temporary directory. 
        Return path to downloaded zip.
        
        Arguments:
            username: GitHub username of project owner
            project: GitHub project name
            sha: commit identifier
            
        Returns:
            Path to downloaded zip file with snapshot of repository.
        """
        self.is_cmd_available("wget")
        tmpdir = tempfile.mkdtemp()
        self.run_cmd([
            "wget", "-P", tmpdir, f"https://github.com/{username}/{project}/archive/{sha}.zip"
            ])
        return os.path.join(tmpdir, f"{sha}.zip")



class Installer:
    """Install Arduino CLI, boards, and libraries necessary to deploy 
    the Nezoba board's software."""

    # Set to empty strings to download latest versions
    # Check README.md before doing so: some specific versions are required!
    ARDUINO_CLI_VERSION = "0.21.0"
    ARDUINO_SAMD_VERSION = "1.8.12"
    ADAFRUIT_SAMD_VERSION = "1.5.14"
    HID_PROJECT_SHA = "2.8.3"
    NSGADGET_SHA = "dfdcb35a07d242a2acb177f93eb8b0ea1c0bcef8"

    # Board specification (Adafruit Trinket M0)
    BOARD_SPEC="adafruit:samd:adafruit_trinket_m0:usbstack=arduino"

    # Path to patch file for HID Project library, relative to this file's location
    PATCH_PATH = str(_patch_file)  # Must convert Path object to string

    # Path where to install the system
    system_dir: str

    # Overwrite existing installation?
    overwrite: bool

    # Wait for user confirmation before each command?
    wait: bool

    # Runner to execute commands
    _runner: Runner

    # platform-independent path to arduino-cli executable in `system_dir`
    arduino_cli: str = os.path.join(".", "arduino-cli")

    def __init__(self, system_dir: str, overwrite: bool = False, wait: bool = True):
        """Setup installer.
        
        Arguments:
            system_dir: Path where to install the system (Arduino CLI).
            overwrite: Overwrite an existing system installation?
            wait: Wait for user confirmation before each command?
        """
        self.system_dir = system_dir
        self.overwrite = overwrite
        self.wait = wait
        self._runner = Runner(wait=wait)

    def setup(self):
        """Install Arduino CLI, boards, and libraries."""
        self.install_arduino_cli()
        self.install_boards()
        self.install_libraries()
        self.patch_boards()

    def install_arduino_cli(self) -> str:
        """Install portable Arduino CLI under `self.system_dir`. If `self.system_dir` 
           doesn't exist, create it. If it already exists and `self.overwrite` is True, 
           delete it first. Return path to CLI's configuration file.
        """
        # Check that curl and shell are available
        self._runner.is_cmd_available("curl")
        self._runner.is_cmd_available("sh")
        # if `self.system_dir` is a non-empty existing directory
        if os.path.isdir(self.system_dir) and os.listdir(self.system_dir):
            # if `overwrite` is True, delete the directory
            if self.overwrite:
                self._runner.run_cmd(
                    lambda: shutil.rmtree(self.system_dir),
                    message=f"Deleting existing non-empty directory: {self.system_dir}"
                    )
            else:
                logging.error("Directory %s already exists and is not empty.",
                              self.system_dir)
                raise FileExistsError("Project directory already exists.")
        # if `self.system_dir` is not an existing directory, create it
        if not os.path.isdir(self.system_dir):
            os.makedirs(self.system_dir, exist_ok=True)
        # Download arduino-cli into `path`
        cli_install = [
            "curl",
            "-fsSL",
            "https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh",
            "|",
            "BINDIR='" + self.system_dir + "'", "sh"] + (
            ["-s", self.ARDUINO_CLI_VERSION] if self.ARDUINO_CLI_VERSION else []
        )
        self._runner.run_cmd(cli_install, shell=True)
        # Create configuration file and capture its location
        outcome = self._runner.run_cmd(
            [self.arduino_cli, "config", "init", "--overwrite"],
            cwd=self.system_dir, text=True, capture_output=True
            )
        # re.MULTILINE uses ^ and $ to identify lines within a multi-line string
        match = re.search(r"^Config file written to: (.+)\w*$", outcome.stdout,
                       re.MULTILINE)
        if not match:
            logging.error("Could not parse Arduino configuration file: {outcome}")
            raise FileNotFoundError("Could not parse Arduino configuration file.")
        cfg_old = match.group(1)
        # Move configuration file to `self.system_dir`
        cfg_path = os.path.join(self.system_dir, os.path.basename(cfg_old))
        os.rename(cfg_old, cfg_path)
        # identify base path of config file
        parts = pathlib.Path(os.path.dirname(cfg_old)).parts
        base_path = ""
        for part in parts:
            if part.startswith(".arduino"):
                break
            base_path = os.path.join(base_path, part)
        # read config file
        with open(cfg_path, "r", encoding="utf-8") as cfgf:
            cfg = yaml.safe_load(cfgf)
        # modify section "directories"
        directories = cfg["directories"]
        # items() iterates over a copy, so it's safe to modify while iterating
        for key, directory in directories.items():
            # set all directories to relative paths
            directories[key] = os.path.relpath(directory, base_path)
        # add board manager for Adafruit products
        cfg["board_manager"]["additional_urls"] += [
            "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
        ]
        # permit installing libraries given as zip files
        cfg["library"]["enable_unsafe_install"] = True
        # write out modified config file
        with open(cfg_path, "w", encoding="utf8") as cfgf:
            yaml.dump(cfg, cfgf, allow_unicode=True)
        return cfg_path

    def install_boards(self):
        """Install SAMD boards using arduino-cli in `self.system_dir`."""
        # download board data
        self._runner.run_cmd(
            [self.arduino_cli, "core", "update-index"],
            cwd=self.system_dir
            )
        # install cores for SAMD (Arduino and Adafruit)
        self._runner.run_cmd(
            [self.arduino_cli, "core", "install",
             "arduino:samd" + "@" + self.ARDUINO_SAMD_VERSION],
            cwd=self.system_dir
            )
        self._runner.run_cmd(
            [self.arduino_cli, "core", "install",
             "adafruit:samd" + "@" + self.ADAFRUIT_SAMD_VERSION],
            cwd=self.system_dir
            )

    def install_libraries(self):
        """Install all required libraries using arduino-cli in `self.system_dir`."""
        # install HID Project library
        hid = self.HID_PROJECT_SHA if self.HID_PROJECT_SHA else "master"
        hid_path = self.github_install("NicoHood", "HID", sha=hid)
        # download NSGamepad extension of HID Project library
        nsg = self.NSGADGET_SHA if self.NSGADGET_SHA else "master"
        nsg_zip = self._runner.github_download("gdsports", "NSGadget_HID", sha=nsg)
        # collect paths of all zip content
        with zipfile.ZipFile(nsg_zip) as zip_file:
            nsg_content = [pathlib.Path(p) for p in zip_file.namelist()]
        # normalize paths by removing first component (the root dir)
        # use relative paths as keys, full path as values
        nsg_content = {pathlib.Path(*p.parts[1:]):p for p in nsg_content}
        # select paths with new files
        dirs_to_copy = ["src/SingleReport/", "src/HID-APIs/"]
        files_to_copy = [p for p in nsg_content for d in dirs_to_copy \
                        if pathlib.Path(d) in p.parents]
        assert len(files_to_copy) == 4
        # unzip those files to the corresponding directories of HID Project library
        with zipfile.ZipFile(nsg_zip) as zip_file:
            for source in files_to_copy:
                # this seems the simplest (!) way of extracting from zip without
                # replicating directory structure
                source_fp = zip_file.open(str(nsg_content[source]))
                target_fp = open(os.path.join(hid_path, source), "wb")
                with source_fp, target_fp:
                    shutil.copyfileobj(source_fp, target_fp)
        # include NSGamepad extensions header into HID Project library
        self._runner.is_cmd_available("patch")
        hid_target = "HID-Project.h"
        self._runner.run_cmd([
            "patch", "-b",
            os.path.join(hid_path, "src", hid_target),
            self.PATCH_PATH
            ])

    def patch_boards(self):
        """Patch boards file in `self.system_dir`, so that it can spoof other boards."""
        # installation directory of hardware specs
        cfg_str = self._runner.run_cmd(
            [self.arduino_cli, "config", "dump"],
            cwd=self.system_dir, text=True, capture_output=True
            )
        cfg = yaml.safe_load(cfg_str.stdout)
        boards_txt = os.path.join(
            self.system_dir,
            cfg["directories"]["data"],
            "packages",
            "adafruit", "hardware", "samd", self.ADAFRUIT_SAMD_VERSION,
            "boards.txt"
            )
        # get content of boards.txt
        with open(boards_txt, "r", encoding="utf-8") as file_handle:
            boards = file_handle.readlines()
        # find where vid and pid specifications are
        vid_id = "adafruit_trinket_m0.build.vid="
        pid_id = "adafruit_trinket_m0.build.pid="
        def is_pid_vid(s: str) -> bool: # pylint: disable=invalid-name # Gimme a break, pylint
            return (s.startswith(vid_id) or s.startswith(pid_id))
        insertion_idx = 0
        for k, k_board in enumerate(boards):
            if is_pid_vid(k_board):
                insertion_idx = k + 1
        # comment out vid and pid specifications
        boards = [(line if not is_pid_vid(line) else ("# " + line)) for line in boards]
        # add new pid specifications
        new_ids = [
            "# NSGamepad spoofing" + "\n",
            vid_id + "0x0F0D" + "\n",
            pid_id + "0x00C1" + "\n"
            ]
        boards = boards[:insertion_idx] + new_ids + boards[insertion_idx:]
        # write out new boards.txt
        with open(boards_txt, "w", encoding="utf-8") as file_handle:
            file_handle.writelines(boards)

    def github_install(self, username: str, project: str, sha: str) -> str:
        """
        Install library into `self.system_dir` by downloading zip from GitHub.

        Arguments:
            username: GitHub username of project owner
            project: GitHub project name
            sha: commit identifier
        
        Returns:
            Path to the installed library.
        """
        # get list of user installed libraries before installing new one
        old_libs = self.installed_libraries()
        zip_file = self._runner.github_download(username, project, sha=sha)
        # install library from zip file
        self._runner.run_cmd([
            self.arduino_cli, "lib", "install", "--zip-path", zip_file
            ], cwd=self.system_dir)
        # name of newly installed library
        new_libs = self.installed_libraries()
        installed_lib = set(new_libs) - set(old_libs)
        assert len(installed_lib) <= 1
        if installed_lib:
            installed_lib = list(installed_lib)[0]
        # installation directory of libraries
        cfg_str = self._runner.run_cmd(
            [self.arduino_cli, "config", "dump"],
            cwd=self.system_dir, text=True, capture_output=True
            )
        cfg = yaml.safe_load(cfg_str.stdout)
        install_dir = os.path.join(self.system_dir, cfg["directories"]["user"], "libraries")
        if installed_lib:
            result = os.path.join(install_dir, installed_lib)
        else:
            result = os.path.join(install_dir, f"{project}-{sha}")
        return result

    def installed_libraries(self) -> list[str]:
        """Currently installed libraries in `self.system_dir`."""
        libs_raw = self._runner.run_cmd(
            [self.arduino_cli, "lib", "list"],
            cwd=self.system_dir, text=True, capture_output=True
            )
        libs = [row.split() for row in libs_raw.stdout.split("\n")[1:]]
        libs = [row[0].strip() for row in libs if row]
        return libs


class Deployer:
    """Compile and upload the Nez-Oba board's software."""

    # Path where the system is installed
    system_dir: str

    # Path where the Nez-Oba board's software is located
    project_dir: str

    # Wait for user confirmation before each command?
    wait: bool

    # Serial port to which the board is connected
    port: Optional[str]

    # Runner to execute commands
    _runner: Runner

    arduino_cli: str = Installer.arduino_cli

    def __init__(self, system_dir: str, project_dir: str, port: Optional[str]=None,
                 wait: bool = True):
        """Setup deployer.
        
        Arguments:
            system_dir: Path where the system (Arduino CLI) is installed.
            project_dir: Path where the Nez-Oba board's software is located 
              (including the encoded mapping header files).
            port: Serial port to which the board is connected. If None, try all available ports.
            wait: Wait for user confirmation before each command?
        """
        self.system_dir = system_dir
        # switch to absolute project path
        self.project_dir = os.path.abspath(project_dir)
        self.port = port
        self.wait = wait
        self._runner = Runner(wait=wait)

    def deploy(self):
        """Compile and upload the Nez-Oba board's software."""
        compiled = self.compile()
        if compiled:
            logging.info("Compilation was successful.")
            uploaded = self.upload()
        else:
            logging.error("Compilation was unsuccessful.")
            raise ValueError("Compilation was unsuccessful.")
        if uploaded:
            print("\n[NEZ] Project compiled and uploaded to board!")
        else:
            print("\n[NEZ] Upload failed!")

    def compile(self) -> bool:
        """Compile board software in `self.project_dir` with arduino-cli's compiler 
        installed in `self.system_dir`. Return True iff compilation was successful."""
        # check that a suitable environment is installed
        check = self._runner.run_cmd(
            [self.arduino_cli, "version"],
            cwd=self.system_dir, text=True, capture_output=True
            )
        if check.returncode != 0:
            raise FileNotFoundError("arduino-cli not found at {self.system_dir}")
        if not re.search("Version: " + Installer.ARDUINO_CLI_VERSION, check.stdout):
            raise ValueError("arduino-cli must have version {Installer.ARDUINO_CLI_VERSION}")
        # compile project
        comp = self._runner.run_cmd(
            [self.arduino_cli, "compile",
             "--fqbn=" + Installer.BOARD_SPEC,
             "--warnings=default",
             self.project_dir],
            cwd=self.system_dir
            )
        exit_status = comp.returncode
        return exit_status == 0

    def upload(self) -> bool:
        """
        Upload compiled board software in `self.project_dir` with arduino-cli's compiler 
        installed in `self.system_dir`. Return True iff upload was successful.
        
        If `self.port` is None, try all all available ports; otherwise, use the given port.
        """
        # Look for a suitable port if none was given
        if not self.port:
            ports_raw = self._runner.run_cmd(
                [self.arduino_cli, "board", "list"],
                cwd=self.system_dir, text=True, capture_output=True
                )
            ports = [row.split() for row in ports_raw.stdout.split("\n")[1:]]
            ports = [row[0].strip() for row in ports if row]
        else:
            ports = [self.port]
        uploaded = False
        for port in ports:
            logging.info("Trying upload to port %s", port)
            if not input(f"--> Upload to port {port}: reset board and type Enter to upload,\n"
                         "or type anything else to skip and try another port.\n"):
                upl = self._runner.run_cmd([
                    self.arduino_cli, "upload",
                    "--fqbn=" + Installer.BOARD_SPEC,
                    "--verify",
                    "--port=" + port,
                    self.project_dir
                    ], cwd=self.system_dir)
                exit_status = upl.returncode
                print()
                if exit_status != 0:
                    logging.error("Upload to port %s was unsuccessful!", port)
                else:
                    logging.info("Upload to port %s was successful", port)
                    uploaded = True
                    break
        return uploaded
