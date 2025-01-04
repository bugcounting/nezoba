#define TESTING
#define DEBUG


#include "../../src/board/debug.h"

#include "../../src/board/keys.h"

#include "../../src/board/globals.h"

#include "../../src/board/key_handler.h"

#include <sstream>
#include <string>
#define CFG_BITS 4


int main(int argc, char** argv) {

  unsigned int n = 0;
  std::string line;

  while (1) {

	 if (n == 0) {

		std::cout << "SETUP: reading control bits "
					 << "(up to " << CFG_BITS << " 0/1 values)" << std::endl;
		std::getline(std::cin, line);

		unsigned int cfg_n = 0;
		uint8_t _cfg[CFG_BITS];
		std::fill(std::begin(_cfg), std::end(_cfg), HIGH);
		std::istringstream iss(line);
		do {
		  std::string word;
		  iss >> word;
		  if (word.empty())
			 break;
		  if (word == "1") {
			 _cfg[cfg_n] = LOW;
		  } else if (word == "0") {
			 _cfg[cfg_n] = HIGH;
		  } else {
			 std::cout << "[Testing] bit value " << word << " unknown" << std::endl;
		  }
		  cfg_n++;
		} while (iss && cfg_n < CFG_BITS);
		_setCfgBit(P_CFG_1, _cfg[0]);
		_setCfgBit(P_CFG_2, _cfg[1]);
		_setCfgBit(P_CFG_3, _cfg[2]);
		Wire._setState(P_CFG_4, (_cfg[3] == HIGH));

#include "../../src/board/setup.h"
		
	 } else {
	 
		std::cout << std::endl << "CONTROL LOOP ITERATION #" << n
					 << ": reading presses"
					 << " (integers in [0.." << (N_BUTTONS-1) << "])"
					 << std::endl;
		std::getline(std::cin, line);

		uint8_t _presses[N_BUTTONS];
		std::fill(std::begin(_presses), std::end(_presses), HIGH);
		std::istringstream iss(line);
		do {
		  std::string word;
		  iss >> word;
		  if (word.empty())
			 break;
		  try {
			 int v = stoi(word);
			 if (0 <= v && v < N_BUTTONS)
				_presses[v] = LOW;
			 else throw std::invalid_argument("");
		  } catch (const std::invalid_argument &e) {
			 std::cout << "[Testing] button " << word << " not valid" << std::endl;
		  }
		} while (iss);
		for (int b = 0; b < N_BUTTONS; b++) {
		  unsigned char p = BUTTON2MCP[b];
		  Wire._setState(p, (_presses[b] == HIGH));
		}

#include "../../src/board/main_loop.h"

	 }
	 n++;
  }

  return 0;  

}


