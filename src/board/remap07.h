/*
  PC kaizo: This is similar to "SMW standard" plus a "grab throwblock"
  key combo (A & B). If you prefer to spin jump with the ring finger,
  use the lower button row. This remapping is meant for playing SMW
  ROM hacks in an emulator; since an emulator usually supports button
  remapping, use the "PC plain" remapping to define the key bindings
  in the emulator (so that the emulator recognizes all the usual
  button inputs), and then switch to this remapping when playing.
*/

// PC
{
   /* ⇐ */           K_DP_LEFT,   K_NOOP,   K_NOOP,
   /* ⇓ */           K_DP_DOWN,   K_NOOP,   K_NOOP,
   /* ⇒ */          K_DP_RIGHT,   K_NOOP,   K_NOOP,
   /* ⇑ */             K_DP_UP,   K_NOOP,   K_NOOP,
   /* Y */                 K_X,   K_NOOP,   K_NOOP,
   /* B */                 K_A,   K_NOOP,   K_NOOP,
   /* A & B */             K_B,      K_A,   K_NOOP,
   /* LB */                K_L,   K_NOOP,   K_NOOP,
   /* A */                 K_B,   K_NOOP,   K_NOOP,
   /* X */                 K_Y,   K_NOOP,   K_NOOP,
   /* B */                 K_A,   K_NOOP,   K_NOOP,
   /* A */                 K_B,   K_NOOP,   K_NOOP,
   /* select */        K_MINUS,   K_NOOP,   K_NOOP,
   /* start */          K_PLUS,   K_NOOP,   K_NOOP,
   /* ⌂ */              K_HOME,   K_NOOP,   K_NOOP
}