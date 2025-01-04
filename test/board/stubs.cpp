#ifdef TESTING

#include <bitset>

#define BYTE2STRING(VALUE) (std::bitset<8>((VALUE)).to_string())

#define byte int

#include "../../src/board/mcp.h"

#define INPUT_PULLUP 0
#define INPUT 1

#define HIGH 1
#define LOW 0


// high means unpressed for a switch
static uint8_t _pressed[1+N_BUTTONS];
static uint8_t _cfg[P_CFG_4+1];


void pinMode(uint8_t pin, uint8_t mode) {
  debug("[Board] pin #"); debug((int) pin); debug(" setup");
  if (mode == INPUT_PULLUP)
	 debug(" (input with pullup)");
  else
	 debug(" (unknown mode)"); debug(mode);
  debug("\n");
}

uint8_t digitalRead(uint8_t pin) {
  uint8_t result = _cfg[pin];
  debug("[Board] pin #"); debug((int) pin); debug(" has value "); debug((int) result);
  debug("\n");
  return result;
}

void _setCfgBit(uint8_t pin, uint8_t value) {
  _cfg[pin] = value;
  debug("[Board] pin #"); debug((int) pin); debug(" set to value "); debug((int) value); debug("\n");
}

void delay(uint16_t delay) {
  debug("[Board] sleeping for ");
  debug(delay);
  debug(" ms\n");
}


class _Wire {
public:
  _Wire() {
  }
  
  void begin() {
	 debug("[Wire] Initialized\n");
  }

  void beginTransmission(uint8_t address) {
	 available = false;
	 debug("[Wire] Begin transmission at address ");
	 debug((int) address);
	 debug("\n");
	 current_address = address;
  }

  void write(uint8_t value) {
	 available = false;
	 debug("[Wire] Writing value ");
	 debug((int) value);
	 debug("\n");
	 current_register = value;
  }

  void endTransmission() {
	 available = false;
	 debug("[Wire] End transmission\n");
  }

  void requestFrom(uint8_t address, uint8_t n) {
	 available = false;
	 debug("[Wire] Reading ");
	 debug((int) n);
	 debug(" bytes from address ");
	 debug((int) address);
	 debug("\n");
	 if (address == current_address) {
		available = true;
		if (current_register == MCP_GPIOA)
		  next_value = gpioa;
		else if (current_register == MCP_GPIOB)
		  next_value = gpiob;
		else {
		  available = false;
		  debug("[Wire] Unknown read register ");
		  debug((int) current_register);
		  debug("\n");
		}
	 }
  }

  uint8_t read() {
	 if (available) {
		debug("[Wire] Reading value ");
		debug(BYTE2STRING(next_value));
		debug("\n");
		return next_value;
	 } else {
		debug("[Wire] No available value: returning 0");
		return 0;
	 }
  }

  void _setState(uint8_t pin, bool value) {
	 debug("[Wire] ");
	 if (value) debug("setting"); else debug("clearing");
	 debug(" pin #"); debug((int) pin); debug("\n");
	 uint8_t bm = PIN2BITMASK(pin);
	 debug("[Wire] using bitmask "); debug(BYTE2STRING(bm)); debug("\n");
	 if (IS_GPIOA_PIN(pin)) {
		debug("[Wire] Value of GPIOA: from "); debug(BYTE2STRING(gpioa));
		if (value)  {
		  gpioa |= bm;
		  debug(" to "); debug(BYTE2STRING(gpioa)); debug("\n");
		} else {
		  gpioa &= ~(bm);
		  debug(" to "); debug(BYTE2STRING(gpioa)); debug("\n");
		}
	 } else {
		  debug("[Wire] Value of GPIOB: from "); debug(BYTE2STRING(gpiob));
		if (value) {
		  gpiob |= bm;
		  debug(" to "); debug(BYTE2STRING(gpiob)); debug("\n");
		} else {
		  gpiob &= ~(bm);
		  debug(" to "); debug(BYTE2STRING(gpiob)); debug("\n");
		}
	 }
  }
  
private:
  uint8_t current_address;
  uint8_t current_register;
  uint8_t next_value;
  bool available;
  uint8_t gpioa = 0;
  uint8_t gpiob = 0;

};

_Wire Wire = _Wire();



class NSGamepad_ {
public:
  static void begin() {
	 debug("[Gamepad] Initialized\n");
  }

  static void releaseAll() {
	 debug("[Gamepad] Releasing all buttons\n");
  }

  static void press(uint8_t b) {
	 debug("[Gamepad] Press button ");
	 debug((int) b);
	 debug("\n");
  }
  
  static void dPad(int8_t dir) {
	 debug("[Gamepad] Sets D-pad to direction ");
	 debug((int) dir);
	 debug("\n");
  }

  static void loop() {
	 debug("[Gamepad] Sending presses\n");
  }

};

NSGamepad_ NSGamepad;

enum NSGamepad_values {
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
							  NSButton_LeftThrottle,
							  NSButton_RightThrottle,
							  NSButton_LeftTrigger,
							  NSButton_RightTrigger,
							  NSButton_Home,
							  NSButton_Plus,
							  NSButton_Minus,
							  NSButton_LeftStick,
							  NSButton_RightStick,
							  NSButton_Capture
};


#endif
