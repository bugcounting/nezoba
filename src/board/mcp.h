#ifndef MCP_H
#define MCP_H


// address of MCP 23017 when the three address pins A0, A1, A2 are all to ground
#define MCP_ADDRESS 0x20
// address of IODIR register: to configure pins as input/output
#define MCP_IODIRA 0x00
#define MCP_IODIRB 0x10
// address of GPPU register: to enable pull-up resistors
#define MCP_GPPUA 0x0c
#define MCP_GPPUB 0x0d
// address of GPIO register: to read/write the pin values
#define MCP_GPIOA 0x12
#define MCP_GPIOB 0x13
// address of GPINTEN register: to turn on/off interrupt triggers
#define MCP_GPINTENA 0x04
#define MCP_GPINTENB 0x05

// Is PIN a pin of GPIOA?
#define IS_GPIOA_PIN(PIN) ((0 <= (PIN) && (PIN) < 8))

// Is PIN a pin of GPIOB?
#define IS_GPIOB_PIN(PIN) ((8 <= (PIN) && (PIN) < 16))

// address of register corresponding to pin #PIN
// using the same PIN ids as the AdaFruit library
// https://github.com/adafruit/Adafruit-MCP23017-Arduino-Library
#define PIN2REGISTER(PIN) (IS_GPIOA_PIN((PIN)) ? (MCP_GPIOA) : (MCP_GPIOB))

// bitmask that identifies bit corresponding to pin #PIN
#define PIN2BITMASK(PIN) (IS_GPIOA_PIN((PIN)) ? \
								  (0x01 << (PIN)) :				\
								  (0x01 << ((PIN)-8)))

// Write VALUE on REGISTER on the MCP
#define MCP_WRITE(REGISTER, VALUE) {				\
	 Wire.beginTransmission(MCP_ADDRESS);			\
	 Wire.write((REGISTER));				\
	 Wire.write((VALUE));								\
	 Wire.endTransmission();							\
  }

// Setup a read of one byte from REGISTER on the MCP
// After this macro: Wire.read() returns the byte
#define MCP_READ(REGISTER) {							\
	 Wire.beginTransmission(MCP_ADDRESS);			\
	 Wire.write((REGISTER));							\
	 Wire.endTransmission();							\
	 Wire.requestFrom(MCP_ADDRESS, 1);				\
  }


#endif
