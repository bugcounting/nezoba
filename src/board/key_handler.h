#define HANDLE_KEY(KEYID, B) {						\
  signed char _k = KEYID[(B)];						\
  debug("Button #"); debug((B));						\
  debug(" is mapped to key ");                  \
  debug((int)_k); debug("\n");						\
  bool turboed = false;                         \
  if (_k < 0) { _k = -(_k); turboed = true; \
	            debug("Turbo this key\n"); } \
  if ((!turboed || TT) && IS_BUTTON(_k)) { debug("Pressing button\n"); \
	                                        NSGamepad.press(KEYS2PAD[_k]); } \
  else if (IS_DP(_k)) {\
    debug("Recording D-pad input\n");\
	 switch (_k) {											\
	 case K_DP_UP:         dpad_y += 1; break;	\
	 case K_DP_DOWN:       dpad_y -= 1; break;		\
	 case K_DP_LEFT:       dpad_x -= 1; break;	\
	 case K_DP_RIGHT:      dpad_x += 1; break;					\
	 case K_DP_UP_RIGHT:   dpad_y += 1; dpad_x += 1; break;	\
	 case K_DP_DOWN_RIGHT: dpad_y -= 1; dpad_x += 1; break;	\
	 case K_DP_UP_LEFT:    dpad_y += 1; dpad_x -= 1; break;	\
	 case K_DP_DOWN_LEFT:  dpad_y -= 1; dpad_x -= 1; break;	\
	 }\
    { if (dpad_x > 1) dpad_x = 1; else if (dpad_x < -1) dpad_x = -1; }\
	 { if (dpad_y > 1) dpad_y = 1; else if (dpad_y < -1) dpad_y = -1; }\
  } }
