#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/util.h>
#include <zephyr/drivers/gpio.h>
#include "modem.h"
#include "battery.h"

uint16_t get_cap_voltage(void);
void setSuspensionHandler();
void Schedule(void);

// **** API parameters - For AsTAR
// Note - all voltages are mV
static int32_t sleepTimer = 100;         // Sleep Timer holds the time to sleep 3600(s) = 1h
static const uint16_t LowVolt_SleepTime = 7200;   // When new voltage < shutoff voltage, the node sleeps and wakes up in 720*10s =120 minutes
static uint16_t oldV = 0;                 // Last measured voltage
static uint16_t newV = 0;                 // Current measured voltage
static int16_t deltaV = 0;               // newV - oldV
//static bool shutOff = true;            // True when device is in shutoff mode
static uint16_t maxRate = 1;                // The maximum execution rate (seconds, lower = faster)    - 1s
static const uint16_t minRate = 7200;              // The minimum execution rate (seconds, lower = faster)    - 120 minutes = 2 hours
static const uint16_t shutOffVoltage = 3000;     // The voltage at which execution should be suspended.
static const uint16_t maxVoltage = 5000;
static uint32_t optimumV = 4500;           // Target capacitor voltage

static uint16_t nighttimeMaxRate = 600;
static const uint16_t daytimeOptimumV = 4500;
static const uint16_t nighttimeVSwing = daytimeOptimumV - (1.1 * shutOffVoltage);
static bool nighttimeFlag = false;
static uint32_t nightDurationRollingEstimate = 28800; // In seconds, starting at 8 hours night length (accurate start point for 26 May)
static uint32_t timeSinceSunset = 0; // In seconds
static uint16_t nighttimeLowestV = daytimeOptimumV;
static const uint16_t nightVLossTimeThreshold = 600; // In seconds, declare night if only voltage losses are recorded for this time period
static const uint8_t weightingNewNightLength = 30; // Percentage weighting for newly recorded night length to total night length
// End ************** Variables

void main(void) {
	modem_main_init();
  k_sleep(K_SECONDS(1));
	battery_setup();
  // Send start up notification (discarded at server)
  modem_transmitData(0xFFFFu, 0xFFFFu);
	while(1) {
		modem_transmitData(get_cap_voltage(), sleepTimer);
		newV = get_cap_voltage();
    	if (newV <= shutOffVoltage) { 
    		setSuspensionHandler();     // Below the minimum voltage, tasks will not run immediately + Wake up in 2 hour
    	} else {  
      		Schedule();                 // Schedule Node to start sleeping for a certain amount of time, then automatically wakes up
    		k_sleep(K_SECONDS(sleepTimer));
			oldV = newV;
    	}
	}
}

void setSuspensionHandler(void) {  
   sleepTimer = LowVolt_SleepTime;
   k_sleep(K_SECONDS(sleepTimer));
   oldV = newV;
}

void Schedule(void) {
  uint32_t sleepDelta;
  deltaV = newV-oldV;
  // ****** Night optimisations ********
  if (deltaV > 0) {
    if (nighttimeFlag) {
      if (newV >= (nighttimeLowestV + 50)) {
        if (timeSinceSunset >= 14400) { // Threshold of 4 hours to count towards night estimate
          nightDurationRollingEstimate = (((100 - weightingNewNightLength) * nightDurationRollingEstimate)/100) + ((weightingNewNightLength * timeSinceSunset)/100);
        }
        nighttimeFlag = false;
        optimumV = daytimeOptimumV;
        nighttimeLowestV = daytimeOptimumV;
        timeSinceSunset = 0;
      }
    } else {
      timeSinceSunset = 0;
    }
  } else {
    if (newV <= (daytimeOptimumV * 1.02)) {
      timeSinceSunset += sleepTimer;
      if (timeSinceSunset >= nightVLossTimeThreshold) {
        if (!nighttimeFlag) sleepTimer = 300;
        nighttimeFlag = true;
      } 
    }
  }
  if(nighttimeFlag) {
    if (newV < nighttimeLowestV) nighttimeLowestV = newV;
    optimumV = daytimeOptimumV - ((nighttimeVSwing * timeSinceSunset)/nightDurationRollingEstimate);
    if (optimumV < (1.1 * shutOffVoltage)) optimumV = (1.1 * shutOffVoltage);
  }
  // ****** End night optimisations ********

  if(newV >= maxVoltage)
  {  
    //state = "Very High";
    sleepTimer = maxRate;
  } 
  else if ((newV < maxVoltage)&&(newV > optimumV))      // MIAD State
  {
    //state = "high";       // "high" means: newV > optimumV
    //stateNumeric = 4;
    if (deltaV >= 0) sleepTimer = sleepTimer / 5;
    if (deltaV < 10) {
      sleepDelta = sleepTimer / 10;
      if (sleepDelta < 1) sleepDelta = 1; // Account for rounding
      if (nighttimeFlag){
        sleepTimer -= sleepDelta; // Track decreasing optimumV
      } else {
        sleepTimer += sleepDelta;
      }
    }

    if (sleepTimer < maxRate) sleepTimer = maxRate;
    if (nighttimeFlag && (sleepTimer < nighttimeMaxRate)) sleepTimer = nighttimeMaxRate;
    if (sleepTimer > minRate) sleepTimer = minRate;
  }
  else if (newV < optimumV) // AIMD State
  {
    //state = "low";          // "Low" means: newV < optimumV
    if (deltaV > 0) {
      sleepDelta = sleepTimer / 10;
      if (sleepDelta < 1) sleepDelta = 1; // Account for rounding
      sleepTimer -= sleepDelta;
    }
    if (deltaV <= 0) sleepTimer = sleepTimer * 5; 
    if (sleepTimer < maxRate) sleepTimer = maxRate;
    if (nighttimeFlag && (sleepTimer < nighttimeMaxRate)) sleepTimer = nighttimeMaxRate;
    if (sleepTimer > minRate) sleepTimer = minRate;
  }
  else  {
    // When newV = optimumV => do nothing (New rate = old rate)
    // state = "optimum";      // optimum means: newV = optimumV
   }
  //shutOff = true;
}

uint16_t get_cap_voltage(void) {
	int rc = battery_measure_enable(true);
  int32_t batt_mV = 0;
	k_sleep(K_MSEC(10));
	if (rc != 0) {
		printk("Failed initialize battery measurement: %d\n", rc);
		return 0;
	}

  // Average across 10 samples
  for (int i = 0; i < 10; i++)
  {
    batt_mV += battery_sample();
    k_sleep(K_MSEC(20));
  }
  batt_mV = batt_mV/10;
  
	if (batt_mV < 0) {
		printk("Failed to read battery voltage: %d\n",
		       batt_mV);
	} else {
		printk("battery voltage: %d mV\n", batt_mV);
	}

	battery_measure_enable(false);
	return (uint16_t) batt_mV;
}