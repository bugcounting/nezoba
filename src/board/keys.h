#ifndef KEYS
#define KEYS

/* 
	Buttons are the physical buttons on the controller, each identified
   by a number. See BUTTON2MCP in globals.h for how each button id maps
	to a pin number in the PCB.

          -:12 +:13  home:14
   
   left:0 down:1 right:2      X:4  Y:5  ZL:6 ZR:7
                              A:8 B:9 L:10 R:11
                 up:3

*/
#define N_BUTTONS 15

/*
  Keys are the possible events on the gamepad, corresponding to all
  usual buttons on a regular controller, plus a "no op" key that
  denotes buttons that have no corresponding key.
*/

#define N_KEYS 42
#define N_DIRECTIONS 9

enum key {
   K_NOOP=0,
   K_DP_UP=1,         // D-pad up
   K_DP_UP_RIGHT=2,   // D-pad up right
   K_DP_RIGHT=3,      // D-pad right
   K_DP_DOWN_RIGHT=4, // D-pad down right
   K_DP_DOWN=5,       // D-pad down
   K_DP_DOWN_LEFT=6,  // D-pad down left
   K_DP_LEFT=7,       // D-pad left
   K_DP_UP_LEFT=8,    // D-pad up left
	K_DP_CENTER=9,     // D-pad centered
   K_A=10,
   K_B=11,
   K_X=12,
   K_Y=13,
   K_L=14,
   K_R=15,
   K_ZL=16,
   K_ZR=17,
   K_HOME=18,
   K_PLUS=19,
   K_MINUS=20,
	K_LS_PRESS=21,   // Click left stick
	K_RS_PRESS=22,   // Click right stick
	K_CAPTURE=23,
   K_LS_UP=24,         // Left stick up
   K_LS_UP_RIGHT=25,
   K_LS_RIGHT=26,
   K_LS_DOWN_RIGHT=27,
   K_LS_DOWN=28,
   K_LS_DOWN_LEFT=29,
   K_LS_LEFT=30,
   K_LS_UP_LEFT=31,
	K_LS_CENTER=32,
   K_RS_UP=33,         // Right stick up
   K_RS_UP_RIGHT=34,
   K_RS_RIGHT=35,
   K_RS_DOWN_RIGHT=36,
   K_RS_DOWN=37,
   K_RS_DOWN_LEFT=38,
   K_RS_LEFT=39,
   K_RS_UP_LEFT=40,
	K_RS_CENTER=41
};

#define IS_NOOP(K)       ((K) == K_NOOP)
#define IS_BUTTON(K)     (K_A <= (K) && (K) <= K_CAPTURE)
#define IS_DP(K)         (K_DP_UP <= (K) && (K) <= K_DP_CENTER)
#define IS_LS(K)         (K_LS_UP <= (K) && (K) <= K_LS_CENTER)
#define IS_RS(K)         (K_RS_UP <= (K) && (K) <= K_RS_CENTER)

// KEYn[b]: when b is pressed activate this key
// If the key is a negative number k, it means press -k with turbo.
// Only regular buttons can be turboed, not directions.
signed char KEY1[N_BUTTONS] = {K_NOOP};
signed char KEY2[N_BUTTONS] = {K_NOOP};
signed char KEY3[N_BUTTONS] = {K_NOOP};
#define N_KEYS_PER_BUTTON 3
#define N_REMAPPINGS 16

signed char MAPPINGS[N_REMAPPINGS][N_KEYS_PER_BUTTON * N_BUTTONS] = {
                                  #include "remap00.h"
											 ,
                                  #include "remap01.h"
											 ,
                                  #include "remap02.h"
											 ,
                                  #include "remap03.h"
											 ,
                                  #include "remap04.h"
											 ,
                                  #include "remap05.h"
											 ,
                                  #include "remap06.h"
											 ,
                                  #include "remap07.h"
											 ,
                                  #include "remap08.h"
											 ,
                                  #include "remap09.h"
											 ,
                                  #include "remap10.h"
											 ,
                                  #include "remap11.h"
											 ,
                                  #include "remap12.h"
											 ,
                                  #include "remap13.h"
											 ,
                                  #include "remap14.h"
											 ,
                                  #include "remap15.h"
                                 };
  
#endif
