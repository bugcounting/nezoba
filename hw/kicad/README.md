# The Nez-Oba controller board

This directory schematics and assembly instructions for the Nez-Oba
game controller board, which can be manufactured as a PCB and then
programmed using the software available [elsewhere](/src/) in this
repository.

The board's design is defined in a [KiCad](https://www.kicad.org/)
(version 5.1.5) project including a schematics, a PCB layout, and
symbol and footprint libraries to make the project self-contained.


## Components

The PCB mounts the following components:

   - An Adafruit [Trinket M0](https://www.adafruit.com/product/3500)
     development board, which runs the controller software.
	 
   - An MCP 23017 port expander, which communicates with the Trinket
     through a clocked serial line. The expander supports 16
     independent digital inputs, which are needed for the many
     buttons of the controller.
	 
   - A piano-type 4-bit DIP switch, which stores the controller's
     configuration number (which, in turn, determines the mapping of
     buttons to gamepad keys).
	 
   - 12 mechanical switches, meant for the 4 directional inputs and 8
     main gamepad buttons.
	 
   - Another 3 switches, meant for the 3 auxiliary gamepad buttons
     (such as *select* and *start*).
	 
The switches are in two groups because the board uses mechanical
switches for the main buttons, and smaller/cheaper tactile buttons for
the auxiliary buttons. However, they all behave the same (and one
could easily change switch type without having to change the
schematics).


## Schematics
	 
The 15 switches are connected each to a separate input of the
expander.  The mapping switch-to-expander makes it easier to lay out
the tracks in the PCB. However, it's essentially immaterial, since any
remapping can be defined via software.

The 4 pins of the DIP switch are connected to the remaining available
digital inputs: 3 of them connect to pins 1, 4, and 2 of the Trinket;
the last one connects to the last input of the expander.

The rest of the connections complete the schematics:

   - All ground pins connect to the Trinket's `GND` pin, which is
     connected to the USB power's ground (hence, it's an output pin
     for the circuit).
	 
   - The expander's three address pins `A0`, `A1`, and `A2` also
     connect to ground. This corresponds to using the [default
     address](https://www.best-microcontroller-projects.com/mcp23017.html)
     0x20. Adding other I2C devices may require to change the address,
     by setting some of these pins to high.
	 
   - The expander's `VDD` and `RESET` pins connect to the Trinket's
     `USB` pin, which draws 5V from the USB power (hence, it's an
     output pin for the circuit).
	 
   - The expander's clock (`SCL`) and data (`SDA`) pins connect to the
     Trinket's clock (pin 2) and data (pin 0) pins (see the [Trinket's
     pinout](https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino/pinouts)). They
     also connect to 5V each [through
     a](https://learn.adafruit.com/using-mcp23008-mcp23017-with-circuitpython/python-circuitpython)
     4.7k Ohm pullup resistor.
	 

## PCB

The symbols used in the schematics are associated with footprints
suitable for the different components used on the PCB. The symbols
also include information about exact product numbers and
manufacturers, so that it should be possible to generate a BOM (bill
of materials) for automated assembly.

The expander has a footprint for a standard DIP packaging with 28 pins
at 2.54mm-pitch, with a form factor of 36x7.8mm.

The 12 mechanical switches mount [Kailh
Choc](https://www.kailhswitch.com/news/kailh-low-profile-mechanical-switches-series-19669171.html)
low-profile mechanical switches. The pin layout is incompatible with
the more common Cherry MX buttons (or other kinds of high-profile
buttons). However, the footprint's size is the same; hence, it should
not be hard to change the design to accommodate Cherry MX switches.

There are *two* symbols for Kailh switches, one for the red (linear)
switches and one for the white (clicky) ones. They are physically and
functionally identical; I created two symbols only to have a way of
storing manufacturer information for both kinds of switches. Indeed,
you can use any other kind of Kailhs, provided they are low profile.

The 3 auxiliary switches mount the cheap 4-pin tactile button
switches, which are very common in cheap electronics starter kits. The
pair of pins on each side of the switch are connected to each other;
clicking the switch connects the pairs on opposing sides. To make this
clear, the PCB connects the two holes on one side of the footprint
with a track. When soldering the switches, make sure to test which
side is connected!

The front layer mounts all switches: main buttons, auxiliary buttons,
and DIP configuration switch. The back layer mounts the control
electronics: Trinket, expander, and the two pullup resistors. This
layout minimizes the height of the top layer, so that the box can
touch the top layer's surface almost everywhere in a stable way.

Most wiring runs on the bottom layer, with only a few short tracks on
the top layer. Filled zones on the top and bottom layers are connected
to ground, which makes for a simple wiring of all ground pins.

The PCB also includes four 4.5 mm diameter mounting holes, at the four
corners of the board.

### Variants of the expander component

A previous version of the controller board (0.1, which was just a
prototype) used an expander mounted on a terminal breakout board
(usually called an CJMCU 2317). This component has the same pinout
(and behavior) as the MCP 23017 expander, but is wired [slightly
differently](https://www.best-microcontroller-projects.com/mcp23017.html):

   - The expander's clock and data pins do not use pullup resistors:
     they just connect to the Trinket.
	 
   - The expander's `RESET` pin connects to 5V through a 10k Ohm
     resistor.

In the attached library, there are also footprints for two models of
terminal breakout boards (of different widths), which should be
mounted using pin headers. The default, however, is to use the MCP
23017 expander without terminal breakout board.


## Changing the board's layout

If you change anything in the schematics (or PCB):

  1. Run the ERC (Electrical Rules Checks) in the schematics layout
     editor (ladybug icon), to make sure they all pass.
 
  2. In the PCB layout editor, click on *Update PCB from schematic*
     (icon to the left of the ladybug icon)
     
	 - Uncheck *Delete extra footprints*, so that the mounting holes
       are not removed.
	   
     - If you didn't change any references (for example, by changing
       it in the footprint editor) you can select *Re-associate
       footprints by reference*. Note that the footprints in library
       `nez-footprint` are set up so that they do not display the
       reference in the PCB view; instead, they display extra text
       that you can customize to reflect the function of each
       component (e.g., each button's default behavior).
	   
     - Click on *Update PCB* and make sure there are no errors.
	   
  3. If you changed anything in the footprints, select *Tools ->
     Update Footprints from Library*. After clicking on *Apply* there
     should be no errors.
	 
  4. Run the DRC (Design Rules Checks) in the PCB layout
     editor (ladybug icon), to make sure they all pass.
	 
	 - Check *Refill all zones*.
	 
	 - I recommend to check both *Report all errors* and *Test tracks
       against filled copper* to perform all checks. It won't take
       long on this simple PCB.
	   
     - Click on *Run DRC* and make sure there are no errors.

In the PCB layout editor, layer *Dwgs.User* is hidden by default. This
includes outlines of all components, which are useful to re-place
footprints after some significant component change.


## Ordering components

The components' symbols also include a link to a page in Digi-Key's
online catalog.

More directly, here are some suggestions about where to buy the
components (from mostly European distributors, but it should not be
hard to find them elsewhere):

   - Any basic 4.7k Ohm resistor should be fine. 5k Ohm ones should
     also work (although I haven't extensively tested them).

   - The 3 auxiliary switches are very common components. Make sure
     you select some with a sufficiently long button cap, so that it
     reaches out of the case.
	 
   - The 4-bit DIP switch is also very common. Check that its
     footprint fits the enclosing case's hole; height should not be an
     issue.
	 
   - Suppliers of components for mechanical keyboards should have the
     Kailh switches, although the Choc models are a bit less widely
     available. (I bought mine from
     [MyKeyboard](https://mykeyboard.eu/): EUR 11 for 20 switches; but
     this seller is [no longer in
     business](https://www.reddit.com/r/MechanicalKeyboards/comments/1ctgniw/mykeyboard_eu_is_bankrupt/). Alternatively,
     there's [42.keebs](https://42keebs.eu/) which is also EU based.)
	 
   - For the expander, look for MCP23017-E/SP components; "E/SP"
     denotes the packaging that the controller uses. As discussed
     [above](#variants-of-the-expander-component), with the default
     layout you just need the bare component, without any mounting
     socket or terminal breakout board (although adding a socket to
     the design should not be hard). Any online electronics shop
     should have them. (I bought mine on Amazon: EUR 4.)
	 
   - Finally, the Trinket M0 should also not be too hard to find. (I
     bought one of mine on Amazon; another one from
     [Distrelec](https://www.distrelec.ch/), which has online stores
     in various countries: CHF 10.)
	 
Altogether, the bare components should cost around EUR 30 (although
you may have to buy some in bulk, using only a few of them).


## PCB manufacturing

To send the PCB layout for manufacturing you can usually either send
the `.kicad-pcb` file or generate plot and drill files. I'll describe
this second way, which is more widely supported (although most PCB
manufacturers also accept CAD files nowadays).

   1. In KiCad's PCB layout editor, click on *Plot* (plotter icon,
      right of the printer icon).
	  
      - *Plot format*: Gerber
	  
	  - Select the following layers: F.Cu, B.Cu (front and back
        copper), F.SilkS, B.SilkS (front and back silk screen),
        F.Mask, B.Mask (front and back solder masks), and Edge.Cuts
        (the perimeter of the board). 
		
	  - Click on *Plot*. This will generate 7 plot files with
        extension `.gbr` (one per layer).
		
	  - In the same window, click on *Generate Drill Files*, and then
        again *Generate Drill File* in the window that opens. This
        will generate 2 drill files with extension `.drl`: one for
        plated through holes (PTH) and one for non-plated through
        holes (NPTH).
	  	
   2. Create a zip file including all 9 generated files (plot and
      drill files).
	   
   3. On the manufacturer's main page, you usually start by an
      approximate size for the PCB. You can measure it in the PCB
      layout editor with the measure distance tool (calipers icon):
      180x104mm should work for the controller board.
	   
   4. Then you upload the zip file with all plot information, and
      select any other options for manufacturing. Default options
      should be fine for this project.
	   
   5. The manufacturer will then perform additional checks to confirm
      they can manufacture the PCB.

I used [EuroCircuits](https://www.eurocircuits.com/) to manufacture my
two Nez-Oba PCBs. They have reasonable prices and deliver high-quality
boards (but YMMV, of course). I payed around EUR 70 for one PCB,
including shipping costs.


## Soldering components

When you assemble the PCB by soldering the components on it, there are
a few things to pay attention to.

   - The Kailh switches' mounting holes are asymmetric, so there's
     only one way that the switches will fit them.
	 
   - The DIP 4-bit switch can be mounted in either directions, but I
     recommend to mount it so that any text on the PCB (especially the
     bit numbers) is readable in the board's "natural" orientation,
     which is the one where the large writing *NEZ-oba* is readable.
	 
   - As explained above, the 4-pin auxiliary button switches have a
     polarity. Check with a multimeter which pairs of pins are wired
     to each other, and then insert one such pair into the pair of
     mounting holes that are also wired with a track on the top layer
     (red line in the PCB layout editor).
	 
   - The MCP23017 also has a polarity. Its [pin
     #1](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf)
     should be marked with a little dot on the DIP packaging; that pin
     goes into the bottom right mounting hole on the back of the PCB,
     which is also marked with a square pad (instead of circular as
     all other mounting holes), as well as with the writing *B0*.
	 
   - Solder header pins to the Trinket, and then solder the other end
     of the pins onto the bottom of the board. Use the writings on the
     board to properly orient the Trinket. In a nutshell, the
     Trinket's top layer (where the tiny reset button is) should face
     away from the PCB's bottom layer, in a way that the Trinket's
     micro USB port is next to the PCB's top edge.
	 
 If you're not sure, use a breadboard to test the components with the
 software, and then assemble them.
