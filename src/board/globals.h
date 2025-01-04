#ifndef GLOBALS
#define GLOBALS 

/* The turbo modifier rapidly toggles the other keys 
   it is associated to */
#define TURBO_PERIOD (1.6*1000.0/120.0)
/* One Pro Controller cycle should be 1/120 s, whereas the display is
   refreshed every 1/60 s (60 Hz). However, I found this intermediate
   value to work best with mashing SMM2 levels. In particular, the
   infamous level GW9-JSR-07G featured in one of PangaeaPanga's videos
   https://www.youtube.com/watch?v=k9B57UplgpQ which I can finish in
   approximately 9.4 with this turbo value (holding up the whole time). */

// turbo toggle flag
bool TT = false;
// the last time the TT was toggled
unsigned long last_toggle_time = 0;


// map of each button number to an MCP pin: see keys.h for default key names
                                  // left down right  up  X  Y  ZL
unsigned char BUTTON2MCP[N_BUTTONS] = {11,  12,  13,   7, 0, 1,  2, 
											  // ZR  A  B  L  R  -   +  home
												  8,  3, 4, 5, 6, 9, 10, 15};

#define DEBOUNCING 5  // 5 ms debouncing

#define P_CFG_1 1       // 1st bit of configuration is regular pin 1
#define P_CFG_2 4       // 2nd bit of configuration is regular pin 4
#define P_CFG_3 3       // 3rd bit of configuration is regular pin 3
#define P_CFG_4 14      // 4th bit of configuration is MCP pin GPB6

// configuration number
unsigned int CFG;  


#ifndef TESTING

#include <Wire.h>
#include <HID-Project.h>

#else
#include "../../test/board/stubs.cpp"
#endif


// current (latest) GPIOA state
byte GPIOA_state = 0xff;
// previous GPIOA state
byte GPIOA_previous = 0xff;
// current (latest) GPIOB state
byte GPIOB_state = 0xff;
// previous GPIOB state
byte GPIOB_previous = 0xff;

// the last time a state change was detected in GPIOA
unsigned long GPIOA_last_debounce_time = 0;
// the last time a state change was detected in GPIOB
unsigned long GPIOB_last_debounce_time = 0;

// map of each key number to the corresponding constant in NSGamepad
uint8_t KEYS2PAD[N_KEYS] = {0,
									 NSGAMEPAD_DPAD_UP,
									 NSGAMEPAD_DPAD_UP_RIGHT,
									 NSGAMEPAD_DPAD_RIGHT,
									 NSGAMEPAD_DPAD_DOWN_RIGHT,
									 NSGAMEPAD_DPAD_DOWN,
									 NSGAMEPAD_DPAD_DOWN_LEFT,
									 NSGAMEPAD_DPAD_LEFT,
									 NSGAMEPAD_DPAD_UP_LEFT,
									 NSGAMEPAD_DPAD_CENTERED,
									 NSButton_A,
									 NSButton_B,
									 NSButton_X,
									 NSButton_Y,
									 NSButton_LeftTrigger,
									 NSButton_RightTrigger,
									 NSButton_LeftThrottle,
									 NSButton_RightThrottle,
									 NSButton_Home,
									 NSButton_Plus,
									 NSButton_Minus,
									 NSButton_LeftStick,
									 NSButton_RightStick,
									 NSButton_Capture
									 };
                   // analog sticks currently unsupported

#endif
