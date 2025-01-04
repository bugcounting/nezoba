#ifndef DEBUG_H
#define DEBUG_H

#ifdef DEBUG
#define DEBUG_ON 1
#else
#define DEBUG_ON 0
#endif


/* 
 * This should be removed by the compiler when DEBUG_ON is 1.
 * Leaving the definition in and letting the compiler remove its instances 
 * has the advantage that the compiler will always check the calls to debug().
 * Alternatively, you can just wrap this in #ifdef DEBUG as in the commented out
 * macro code, if you want to directly control what the compiler sees.
 */
// #ifdef DEBUG
#ifndef TESTING
#define debug(str) do { if (DEBUG_ON) Serial.print(str); } while(0)
#else
#include <iostream>
#define debug(str) do { if (DEBUG_ON) std::cout << str; } while(0)
#endif
// #else
// #define debug(str)  
// #endif


// #ifdef DEBUG

// set when setup is done
unsigned long _init_time;
// number of iterations of main control loop
unsigned long _num_loops = 0;

#ifdef TESTING
#include <chrono>
#define millis() std::chrono::duration_cast<std::chrono::milliseconds>( \
	   std::chrono::system_clock::now().time_since_epoch() \
																		  ).count()
#endif

#define init_time() do { if (DEBUG_ON) _init_time = millis(); } while(0)

#define loop_end() do { if (DEBUG_ON) {											\
	 unsigned long _new_time = millis();											\
	 _num_loops += 1;																		\
	 double _average_time = (_new_time - _init_time)/_num_loops;			\
	 debug("Average loop time: ");													\
	 debug((double)_average_time);										\
	 debug(" ms\n");															\
	 }} while (0)

// #else
// #define init_time()
// #define loop_end()
// #endif

#endif
