debug("BEGIN: setup\n");

debug("Starting MCP\n");

Wire.begin();

debug("Setting up pins on board and MCP device\n");

pinMode(P_CFG_1, INPUT_PULLUP);
pinMode(P_CFG_2, INPUT_PULLUP);
pinMode(P_CFG_3, INPUT_PULLUP);

// set all group As and Bs pins to input
MCP_WRITE(MCP_IODIRA, 0xff);
MCP_WRITE(MCP_IODIRB, 0xff);
// turn off interrupt triggers (for good measure)
MCP_WRITE(MCP_GPINTENA, 0x00);
MCP_WRITE(MCP_GPINTENB, 0x00);
// enable pull-up resistors on all group As and Bs pins
MCP_WRITE(MCP_GPPUA, 0xff);
MCP_WRITE(MCP_GPPUB, 0xff);

debug("Reading configuration number\n");

bool cfg1 = (digitalRead(P_CFG_1) == LOW);
bool cfg2 = (digitalRead(P_CFG_2) == LOW);
bool cfg3 = (digitalRead(P_CFG_3) == LOW);

// bare-bones debouncing (probably not needed):
// read until getting a stable state
byte __cfg4 = 0x00;
byte _cfg4;
while(1) {
  delay(DEBOUNCING);
  MCP_READ(PIN2REGISTER(P_CFG_4));
  _cfg4 = Wire.read();
  if (_cfg4 == __cfg4)
	 break;
  __cfg4 = _cfg4;
 }
// bit == 0 iff digital input is LOW iff switch is on 1
bool cfg4 = ((_cfg4 & PIN2BITMASK(P_CFG_4)) == 0);

CFG = (cfg1 << 3) + (cfg2 << 2) + (cfg3 << 1) + cfg4;

debug("Configuration number is: ");
debug(CFG);
debug(" (");
debug(cfg1); debug(" ");
debug(cfg2); debug(" "); 
debug(cfg3); debug(" "); 
debug(cfg4);
debug(")\n");

// assign mapping based on CFG number
signed char * CFG_MAPPING = MAPPINGS[CFG];
for (int b = 0; b < N_BUTTONS; b++) {
  debug("Mapping for button #"); debug((int) b); debug(": ");
  KEY1[b] = CFG_MAPPING[3*b];
  debug((int) KEY1[b]); debug(" ");
  KEY2[b] = CFG_MAPPING[3*b + 1];
  debug((int) KEY2[b]); debug(" ");
  KEY3[b] = CFG_MAPPING[3*b + 2];
  debug((int) KEY3[b]); debug("\n");
}

debug("Starting gamepad\n");

NSGamepad.begin();

debug("END: setup\n");

init_time();
