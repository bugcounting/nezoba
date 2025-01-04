/*
  Celeste with combos: A variant of "Celeste standard" with the
  addition of macros to climb up (L & up) and dash up (A & up), which
  are common actions in Celeste gameplay.
*/

// NS
{
   /* ⇐ */          K_DP_LEFT,    K_NOOP,   K_NOOP,
   /* ⇓ */          K_DP_DOWN,    K_NOOP,   K_NOOP,
   /* ⇒ */         K_DP_RIGHT,    K_NOOP,   K_NOOP,
   /* ⇑ */            K_DP_UP,    K_NOOP,   K_NOOP,
   /* B */                K_B,    K_NOOP,   K_NOOP,
   /* Y */                K_Y,    K_NOOP,   K_NOOP,
   /* ZL */              K_ZL,    K_NOOP,   K_NOOP,
   /* L & ⇑ */            K_L,   K_DP_UP,   K_NOOP,
   /* A & ⇑ */            K_A,   K_DP_UP,   K_NOOP,
   /* X */                K_X,    K_NOOP,   K_NOOP,
   /* A */                K_A,    K_NOOP,   K_NOOP,
   /* R */                K_R,    K_NOOP,   K_NOOP,
   /* - */            K_MINUS,    K_NOOP,   K_NOOP,
   /* + */             K_PLUS,    K_NOOP,   K_NOOP,
   /* ⌂ */             K_HOME,    K_NOOP,   K_NOOP
}