
// Library
#include <SPI.h>
#include <RH_RF95.h>
#include <Adafruit_SleepyDog.h>
#include<math.h>

// Declare Variables
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

//Start **************** Using for Gateway2 433MHz in Vietnam ****************
#define RF95_FREQ 433.0                     // Gateway_2's frequency
RH_RF95 rf95(RFM95_CS, RFM95_INT);
// Start ************************* Variables  ****************************
//const uint8_t LORA_NODE_ADDR = 0x65;      // ************ Vu - This is node101's address
const uint8_t LORA_NODE_ADDR = 0x66;        // ************ Vu - This is node102's address
const uint8_t LORA_SERVER_ADDR = 0x02;      // Vu - LoRa receiving address ((Vu - Gateway_2 Address))
//Stop **************** Using for Gateway2 433MHz in Vietnam ****************

uint16_t TX_BUF_SIZE = 8;                   // Vu - Transmit buffer size

#define VBATPIN A0      // Analog input pin is A0 that the potentiometer is attached to
float Water_Level;      // Contain the value of Water level
uint16_t Battery_Level; // Contain the value of Battery level
float Temp;             // Contain the value of Temperature 


//****  Prof.Danny - API parameters
//bool DEBUG = 1;                         // If true, debug information will be printed.
bool DEBUG = 0;                           // If true, debug information will be printed.
uint16_t sleepTimer = 180;                // Sleep Timer holds the time to sleep 180*1(s) = 3m
const uint16_t LowVolt_SleepTime = 7200;  // When new voltage < shutoff voltage, the node sleeps and wakes up in 720*10s =120 minutes
uint16_t oldV = 0;                        // Last measured voltage
uint16_t newV = 0;                        // Current measured voltage
int16_t deltaV = 0;                       // newV - oldV
bool shutOff = true;                      // True when device is in shutoff mode
String state = "init";                    // Holds the current state description

const uint16_t maxRate = 1;               // The maximum execution rate (seconds, lower = faster)    - 1*10s
const uint16_t minRate= 7200;             // The minimum execution rate (seconds, lower = faster)    - 120 minutes = 2 hours
const uint16_t shutOffVoltage = 2600;     // The voltage at which execution should be suspended.
const uint16_t maxVoltage = 5000;
uint16_t optimumV = 4500;                 // Target capacitor voltage

//Variables are only dedicated to NightOptimisation algorithms
const uint16_t nighttimeMaxRate = 25;     // Outdoor nodes
//const uint16_t nighttimeMaxRate = 90;   // Indoor nodes
const uint16_t daytimeOptimumV = 4500;
uint16_t nighttimeVSwing = daytimeOptimumV - (1.1 * shutOffVoltage);
bool nighttimeFlag = false;

uint32_t nightDurationRollingEstimate =  43200;         // In seconds, starting at 12 hours night length (accurate start point for 26 May)
uint32_t timeSinceSunset = 0;                           // In seconds
uint16_t nighttimeLowestV = daytimeOptimumV;
const uint16_t nightVLossTimeThreshold = 600;           // In seconds, declare night if only voltage losses are recorded for this time period
const uint8_t weightingNewNightLength = 30;             // Percentage weighting for newly recorded night length to total night length
//End **************************** Variables ****************************


//Function Definition
void myLoRa_Init(void);                                 // Initiating LoRa Parameters
void Read_WaterLevel(void);                             // Vu - This function is used for calculating the Water level
uint16_t Read_BatteryLevel(void);                       // Vu - This function is used for calculating the Battery level
void mysleep(uint16_t sleepTimer);                      // Vu - This function is used for putting the node at low power mode

void setSuspensionHandler(void);
void Schedule(void);
//End ***************************** Declare variables + Function Definition *****************************



void setup()
{
  analogReference(AR_INTERNAL1V0);                      // https://www.arduino.cc/reference/en/language/functions/analog-io/analogreference/
  analogReadResolution(12); 
           
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.begin(9600);
  Serial.print("Begin ....!");
  delay(8000);  // for being easy to flash MCU
  myLoRa_Init();  // Initiating LoRa Parameters
}

void loop()
{
  newV = Read_BatteryLevel();
  if (newV <= shutOffVoltage) 
    setSuspensionHandler();                             // Below the minimum voltage, tasks will not run immediately + Wake up in 2 hour
  else
  {  
    Schedule();                                         // Schedule the node based on DeltaV, Voltage level
    SendData();
    mysleep(sleepTimer);
    oldV = newV;
  }  
}

// $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Functions Definition $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
// Start ****************************** Handle Task Suspension *****************************
/*
 *  Handle Task Suspension:
 *  Below the minimum voltage, tasks will not run immediately + Wake up in 2 hour
*/
void setSuspensionHandler()
{  
   sleepTimer = LowVolt_SleepTime;
   #if DEBUG
    Serial.print("New sleep timer = ");
    Serial.print(String(sleepTimer));
    Serial.println(" (seconds)");
   #endif
   shutOff = true;
   mysleep(sleepTimer);
   oldV = newV;
}
//End ******************************** Handle Task Suspension ******************************

//Start ************************************** Schedule Function ***************************
/*
 * Schedule the node based on DeltaV, Voltage level
 */
void Schedule(void)
{
  uint16_t sleepDelta;
  deltaV = newV-oldV;

  // Print debug information
  if (DEBUG)
  {
    Serial.println("");    
    Serial.print("Old V = ");
    Serial.println(String(oldV));
    Serial.print("New V = ");
    Serial.println(String(newV));
    Serial.print("Delta V = ");
    Serial.println(String(deltaV));
    Serial.print("Old sleepTimer = ");
    Serial.println(String(sleepTimer));
  }

  // ****** Night optimisations ********
  if((deltaV >=0) && (!nighttimeFlag))   // Vu - Adds
    timeSinceSunset = 0;
    
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
    //state = "high";                                   // "high" means: newV > optimumV
    //stateNumeric = 4;
    if (deltaV >= 0.00) sleepTimer = sleepTimer / 5;    // "/5" means that the sleep time is reduced by 5x
    if (deltaV < 10.0) {
      sleepDelta = sleepTimer / 10;
      if (sleepDelta < 1) sleepDelta = 1;               // Account for rounding
      if (nighttimeFlag){
        sleepTimer -= sleepDelta;                       // Track decreasing optimumV
      } else {
        sleepTimer += sleepDelta;                       // Normal operation
      }
    }
    if (sleepTimer < maxRate) sleepTimer = maxRate;     // maxRate = sending data every 120s
    if (nighttimeFlag && (sleepTimer < nighttimeMaxRate)) sleepTimer = nighttimeMaxRate;
    if (sleepTimer > minRate) sleepTimer = minRate;     // minRate = sending data every 1200 minutes
  }
  else if (newV < optimumV)                             // AIMD State
  {
    //state = "low";                                    // "Low" means: newV < optimumV
    if (deltaV > 0.00) {
      sleepDelta = sleepTimer / 10;
      if (sleepDelta < 1) sleepDelta = 1;               // Account for rounding
      sleepTimer -= sleepDelta;
    }
    if (deltaV <= 0.00) sleepTimer = sleepTimer * 5;    // "*5" means that the sleep time is increase by 5x  
    if (sleepTimer < maxRate) sleepTimer = maxRate;
    if (nighttimeFlag && (sleepTimer < nighttimeMaxRate)) sleepTimer = nighttimeMaxRate;
    if (sleepTimer > minRate) sleepTimer = minRate;
  }
  else  {
    //When newV = optimumV => do nothing (New rate = old rate)
    //state = "optimum";      // optimum means: newV = optimumV
   }
  if(DEBUG)
  {
    Serial.print("New sleep timer = ");
    Serial.print(String(sleepTimer));
    Serial.println(" (seconds)");
  }    
}
//End *************************** Schedule Function ********************

//Start ************************** Sleep function **********************
void mysleep(uint16_t sleepTimer)
{ 
  digitalWrite(LED_BUILTIN, LOW);             // LED_BUILTIN = pin 13
  if (sleepTimer < 4)
    for (uint16_t j=0; j<sleepTimer; j++)
    {            
      rf95.sleep();
      Watchdog.sleep(1000);                   // => VŨ only accept 1/2/4/8ms
    }
  else
    for (uint16_t j=0; j<(sleepTimer/4); j++)
    {            
      rf95.sleep();
      Watchdog.sleep(4000);                   // => VŨ only accept 1/2/4/8ms
    }
}
//End ****************************** Sleep function **********************

//Start ************************ Init LoRa Parameter *********************
void myLoRa_Init(void)
{
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  delay(100);
  if (DEBUG) Serial.println("Arduino LoRa TX Test!");
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    if (DEBUG) Serial.println("LoRa radio init failed");
    while (1);
  }
  if (DEBUG) Serial.println("LoRa radio init OK!");

  //Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    if (DEBUG) Serial.println("setFrequency failed");
    while (1);
  }
 if (DEBUG) Serial.print("Set Freq to: "); 
 if (DEBUG) Serial.println(RF95_FREQ);
  
  //Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
  //Slow long range.                                 // https://www.airspayce.com/mikem/arduino/RadioHead/classRH__RF95.html
  //rf95.setModemConfig(RH_RF95::Bw125Cr48Sf4096);   // Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on.
  //rf95.setModemConfig(RH_RF95::Bw500Cr45Sf128);
                                             
  //The default transmitter power is 13dBm, using PA_BOOST.
  //If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  //you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
}
//End ************************* Init LoRa Parameter **************************** 

//Start *********************** Read waterlevel ********************************
  //Calling function that is incharge of calculating the Water level
void Read_WaterLevel(void)
{ 
  Water_Level = random(0,1000);         // Water Level is a Random value ranging from 100 - 500
 if (DEBUG)    // whether print or not?
 {
    Serial.print(Water_Level);         // Just for Testing
    Serial.println(" cm");             // Just for Testing
 }
}
//End ************************** Read water level **************************

//Start *********************** Read Battery Level *************************
  //This Function is used for reading Battery level
uint16_t Read_BatteryLevel(void)
{
  //#define VBATPIN A7;               // (A9 = D9) if we want to measure the Voltage between 2 pin (Battery pin and Ground pin/ JST Jack)
                                      // on the board without having to connect any wire (it is Built-in connection).
  //#define VBATPIN A0;               // Analog input pin is A0 that the potentiometer is attached to
  float  F_Battery_Level;
  F_Battery_Level = analogRead(VBATPIN);
  delay(10);
  F_Battery_Level *= 6;               // we divided by 6, so multiply back (Using 01 20K-resistor and one 100K-Resistor)
  F_Battery_Level *= 1000;            // Multiply by 3.3V, our reference voltage AR_INTERNAL2V23
  F_Battery_Level /= 4096;            // convert to voltage
  Battery_Level = (uint16_t)F_Battery_Level;
  if (DEBUG)
  {
     Serial.print("VBat ------: " ); 
     Serial.println(Battery_Level);
  }
  return Battery_Level;  
}
//End ********************** Read Voltage level **************************

//Start ***************************** Send Data ************************** 
void SendData(void)
{
  uint8_t tx_buf[TX_BUF_SIZE];
  //Read data from sensor
  Read_WaterLevel();                      // Calling function that is incharge of calculating the Water level
  //Scale (x10) and round data in order to avoid sending float value
  uint16_t Water = (uint16_t)((Water_Level * 10.0));
  int16_t Battery = Battery_Level;      
 if (DEBUG)
 {
   Serial.print("Water Level: ");
   Serial.print(Water_Level, 1);
   Serial.println(" Cm");
   Serial.print("Battery Level: ");
   Serial.print(Battery_Level, 1);
   Serial.println(" mV");
   Serial.print("sleepTimer: ");
   Serial.print(sleepTimer);
   Serial.println(" seconds");
 }
 
  //Prepare and send data to the server **************
  //Stuff buffer
  tx_buf[0] = LORA_NODE_ADDR;             // From address (this node) [1 byte]
  tx_buf[1] = LORA_SERVER_ADDR;           // To address (server) [1 byte]
  tx_buf[2] = (0xff & Water);             // Temperature [2 bytes] little-endian
  tx_buf[3] = (0xff & (Water >> 8));
  tx_buf[4] = (0xff & Battery);           // Humidity [2 bytes] little-endian
  tx_buf[5] = (0xff & (Battery >> 8));
  tx_buf[6] = (0xff & sleepTimer);        // Pressure [2 bytes] little-endian
  tx_buf[7] = (0xff & (sleepTimer >> 8));
  if (DEBUG)
  {
    Serial.print("Sending buffer:");
    for (uint8_t i = 0; i < TX_BUF_SIZE; i++) 
    {
      Serial.print(" 0x");
      Serial.print(tx_buf[i], HEX);
    }
    Serial.println();
    Serial.println();
  }

  if (DEBUG) Serial.println("Sending to rf95_server");
  delay(10);
  rf95.send(tx_buf, TX_BUF_SIZE);
  if (DEBUG) Serial.println("Waiting for packet to complete...");
  delay(5);
  rf95.waitPacketSent();
  if (DEBUG) Serial.println("completed");
  delay(10);
}
//End ****************************** Send Data *****************************
