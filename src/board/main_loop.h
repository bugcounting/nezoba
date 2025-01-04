debug("BEGIN: main loop iteration\n");

NSGamepad.releaseAll();
// no need to recenter D-pad, since a direction will be assigned in any case
  
int dpad_x = 0, dpad_y = 0;

// Complement turbo toggle every TURBO_PERIOD seconds
// This means that a turboed button is pushed approximately every
// 2*TURBO_PERIOD ms
if ((unsigned long) (millis() - last_toggle_time) >= TURBO_PERIOD) {
  last_toggle_time = millis();
  TT = !TT;
 }

// read all buttons into local variables
MCP_READ(MCP_GPIOA);
byte reading_gpioa = Wire.read();
GPIOA_state = reading_gpioa;
debug("Read GPIOA state: "); debug(GPIOA_state); debug("\n");
MCP_READ(MCP_GPIOB);
byte reading_gpiob = Wire.read();
GPIOB_state = reading_gpiob;
debug("Read GPIOB state: "); debug(GPIOB_state); debug("\n");

// DEBOUNCING
// if state has changed, reset the debouncing timer
if (reading_gpioa != GPIOA_previous)
  GPIOA_last_debounce_time = millis();
if (reading_gpiob != GPIOB_previous)
  GPIOB_last_debounce_time = millis();
// if the DEBOUNCING time has passed since the last state change,
// we can use the latest reading as the actual current state
if ((unsigned long)(millis() - GPIOA_last_debounce_time) > DEBOUNCING) {
  // update state to latest reading
  if (reading_gpioa != GPIOA_state)
	 GPIOA_state = reading_gpioa;
 }
if ((unsigned long)(millis() - GPIOB_last_debounce_time) > DEBOUNCING) {
  // update state to latest reading
  if (reading_gpiob != GPIOB_state)
	 GPIOB_state = reading_gpiob;
 }
// the latest reading becomes the previously read state
GPIOA_previous = reading_gpioa;
GPIOB_previous = reading_gpiob;

for (int b = 0; b < N_BUTTONS; b++) {
  unsigned char p = BUTTON2MCP[b];
  // select proper register according to pin number
  byte _gpio = (IS_GPIOA_PIN(p) ? GPIOA_state : GPIOB_state);
  // a bit is 0 iff the digital input is LOW iff the switch is pressed
  bool pressed = ((_gpio & PIN2BITMASK(p)) == 0x00);
  /* bool pressed = (BUTTONS[b].read() == LOW); */
  if (pressed) {
	 debug("Key #"); debug(b); debug(" pressed\n");
	 // first key
	 debug("Handling first key\n");
	 HANDLE_KEY(KEY1, b);
	 // second key
	 debug("Handling second key\n");
	 HANDLE_KEY(KEY2, b);
	 // third key
	 debug("Handling third key\n");
	 HANDLE_KEY(KEY3, b);
  }
 }

// basic SOCD cleaning
debug("Cleaning of x: "); debug((int) dpad_x); debug(", y: "); debug((int) dpad_y); debug("\n");
if (dpad_x == 0 && dpad_y == 0) {
  debug("Setting D-pad to center\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_CENTER]);
 } else if (dpad_x == 0 && dpad_y == 1) {
  debug("Setting D-pad to up\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_UP]);
 } else if (dpad_x == 1 && dpad_y == 1) {
  debug("Setting D-pad to up right\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_UP_RIGHT]);
 } else if (dpad_x == 1 && dpad_y == 0) {
  debug("Setting D-pad to right\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_RIGHT]);
 } else if (dpad_x == 1 && dpad_y == -1) {
  debug("Setting D-pad to down right\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_DOWN_RIGHT]);
 } else if (dpad_x == 0 && dpad_y == -1) {
  debug("Setting D-pad to down\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_DOWN]);
 } else if (dpad_x == -1 && dpad_y == -1) {
  debug("Setting D-pad to down left\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_DOWN_LEFT]);
 } else if (dpad_x == -1 && dpad_y == 0) {
  debug("Setting D-pad to left\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_LEFT]);
 } else if (dpad_x == -1 && dpad_y == 1) {
  debug("Setting D-pad to up left\n");
  NSGamepad.dPad(KEYS2PAD[K_DP_UP_LEFT]);
 }

NSGamepad.loop();

debug("END: main loop iteration\n");

loop_end();
