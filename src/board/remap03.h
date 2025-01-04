/*
  SMM2 button mashing: A variant of "SMM2 button mashing" with the
  addition of turbo on run (X) and jump (A). Plain buttons X and A are
  still available on the bottom row's right-hand side for menu
  navigation; for a similar reason, the top rightmost button maps to L
  & R so that you can start SMM2 without having to use a different
  controller.
*/

// NS
{
   /* ⇐ */          K_DP_LEFT,   K_NOOP,   K_NOOP,
   /* ⇓ */          K_DP_DOWN,   K_NOOP,   K_NOOP,
   /* ⇒ */         K_DP_RIGHT,   K_NOOP,   K_NOOP,
   /* ⇑ */            K_DP_UP,   K_NOOP,   K_NOOP,
   /* Y */                K_Y,   K_NOOP,   K_NOOP,
   /* B */                K_B,   K_NOOP,   K_NOOP,
   /* L */                K_L,   K_NOOP,   K_NOOP,
   /* L & R */            K_L,      K_R,   K_NOOP,
   /* X' */              -K_X,   K_NOOP,   K_NOOP,
   /* A' */              -K_A,   K_NOOP,   K_NOOP,
   /* X */                K_X,   K_NOOP,   K_NOOP,
   /* A */                K_A,   K_NOOP,   K_NOOP,
   /* - */            K_MINUS,   K_NOOP,   K_NOOP,
   /* + */             K_PLUS,   K_NOOP,   K_NOOP,
   /* ⌂ */             K_HOME,   K_NOOP,   K_NOOP
}