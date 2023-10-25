
#<div align="center"> 
   # Flute: Enabling a Battery-free and Energy Harvesting Ecosystem for the Internet of Things
</div>

## 1. Description
<div align="justify">
   Nowadays, most Internet of Things (IoT) devices still operate on batteries, offering lifetimes of just a few years; leading to high maintenance costs and excess waste. Energy Harvesting (EH) in combination with super-capacitor charge storage offers a solution, however, it is considered complex and unreliable, hampering its real-world deployment. To address this problem, we contribute Flute, a power management system for building battery-free IoT deployments. Unlike prior work, Flute focuses on transforming existing IoT development boards into battery-free devices. Reliable operation is achieved through a combination of generic power management hardware and self-adaptive software enabling sustainable operation in the face of dynamic power supply and demand. We evaluate our approach through a series of diverse one-week solar EH scenarios and show that Flute efficiently harvests energy and achieves reliable operation for a range of unmodified IoT development boards using LTE-M and LoRa. Hence, Flute provides a promising foundation for building a battery-free and EH ecosystem for the Internet of Things.
</div>


## 2. Flute Design 
We define the following requirements for the design of Flute:
- <div align="justify"> First, <strong> Low power duty cycling </strong>: Sustainable EH requires aggressive duty cycling. However, the power efficiency of IoT development boards varies dramatically. Flute addresses this problem via a power board that allows the host board to be powered down or placed into deep sleep mode between executions. </div>

- <div align="justify"> Second, <strong> Adaptive task scheduling </strong>: Intelligent scheduling is required to tailor application energy demands to match available energy supply. However, additional support is required to enable more consistent scheduling in the case of diurnal EH patterns.  </div>

- <div align="justify"> Third, <strong> PnP operation </strong>: Flute will support the existing ecosystem of IoT development boards by offering the first PnP battery-free and EH solution for the boards, specifically focusing on the Adafruit Feather due to its extensive range and popularity.  </div>

- <div align="justify"> Finally, <strong> Developer support </strong>: Flute contributes energy management libraries that simplify task scheduling, time management, and handling power faults. Reference implementations are available for the Arduino and Zephyr development environments.  </div>

### 2.1. Flute Hardware
<p align="center">
   <img width="700" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/75bab354-0a51-4e70-870a-4a9e69547c28">
</p>

**<div align="center">
  Fig 1.  Block diagram of the Flute PnP power board**
</div>

<strong> Figure 1 </strong> provides a high-level block diagram of the power board and each block is then explained as follows:

- <div align="justify"> <strong> Charge Storage </strong>: Flute’s charge storage <strong>(1)</strong> uses an array of up to four reconfigurable super-capacitors. As Flute aims to ensure sustainable operation, these capacitors should be sized to power the device at an acceptable duty cycle during the longest 
   expected energy droughts (i.e. periods with no environmental energy available). Capacitors with minimal leakage current and low Equivalent Series Resistance (ESR) are preferred. </div>

- <div align="justify"> <strong> Charge Monitoring </strong>: Flute uses the ADC of the host development board to monitor the capacitor voltage via a 50% voltage divider circuit <strong> (2) </strong>. Large-value resistors are selected to minimize the power consumption of this circuit element. The remaining useful 
   charge is calculated based on the array size, voltage level and brownout voltage. </div>

 - <div align="justify"> <strong> Power Control </strong>: Most development boards using Flute have onboard regulators with different specifications and efficiencies. To address this heterogeneity, Flute supports two power management strategies. First, an efficient Real Time Clock (RTC) <strong> (3) </strong> 
   provides a common sleep timer with power consumption under 50nA. The sleep timer can be used in two ways. For boards with acceptable sleep power, the MCU can enter deep sleep and the RTC is used to wake it based on an external interrupt. For boards with prohibitive sleep power, the RTC can
    use its digital power switch to completely power down the board during sleep, mitigating design inefficiencies. To prevent power leakage, I2C and ADC lines are also isolated during power down. The output of the capacitors is regulated using the onboard regulator. </div>


<div align="justify"> The hardware goal of Flute is to convert commodity IoT development boards into battery-free EH devices. Flute’s software goal is to schedule tasks: (i.) as frequently as possible, while (ii.) accumulating an optimum charge level and (iii.) preserving system operation by throttling execution when environmental energy is lost. This requires a PnP power supply board and software support to manage energy usage. <div/>


### 2.2.  Flute Software 

<p align="center">
   <img width="650" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/cdf80caf-2857-4250-a6d0-a94e76947a27">
</p>

**<div align="center">
  Fig 2. The Flute Hardware/Software Architecture**
</div>

<div align="justify"> Flute aims to convert commodity IoT development boards into battery-free EH devices that can work in either outdoor or indoor environments reliably. To validate this, we employed long-range networking, 433MHz LoRa, and LTE-M, parameterized for low power and extended coverage. To show its deployment in the real world, we deployed Flute both outdoors and indoors and in 2 different countries on 2 different continents Vietnam and Belgium. </div>
The pseudo-code of the proposed algorithms is shown as follows.

```javascript
1    getAdaptedRate ( V_New , V_Prev ) {
2    IF ( V_New - V_Prev ) < 0 for last 10 minutes AND V_New <= V_Day_Optimum
3      Night_Mode = True
4    ELSE IF ( V_New - V_Prev ) > 0
5      Night_Mode = False
6    IF Night_Mode
7      V_Optimum = V_Day_Optimum - ( T_Since_Sunset * V_Swing_Night / Length_Night_EWMA )
8    IF V_New < V_Min
9      T_Sleep = Max_Sleep
10   ELSE IF V_New > V_Max
11     T_Sleep = Min_Sleep
12   ELSE IF V_New < V_Optimum
13      IF ( V_New - V_Prev ) < 0
14         T_Sleep = T_Sleep * 5
15      ELSE
16         Sleep_Delta = T_Sleep / 10
17         IF Sleep_Delta < 1
18           Sleep_Delta = 1
19         T_Sleep = T_Sleep - Sleep_Delta
20   ELSE IF V_New >= V_Optimum
21     IF ( V_New - V_Prev ) < 0
22       Sleep_Delta = T_Sleep / 10
23       IF Sleep_Delta < 1
24         Sleep_Delta = 1
25       IF Night_Mode
26         T_Sleep = T_Sleep - Sleep_Delta
27       ELSE T_Sleep = T_Sleep + Sleep_Delta
28     ELSE T_Sleep = T_Sleep /5
29   IF T_Sleep < Min_Sleep
30     T_Sleep = Min_Sleep
31   IF Night_Mode AND T_Sleep < Min_Night_Sleep
32     T_Sleep = Min_Night_Sleep
33   RETURN T_Sleep
34   }
```

<div align="justify"> Flute uses the proposed AsTAR++ algorithm which manages energy droughts by tracking the duration of power outages using an Exponentially Weighted Moving Average. When an energy drought is detected based on 10 minutes of no charge gain (e.g. sunset), Flute changes strategies, aiming to schedule tasks at such a rate that 90% of the available charge is used by the expected end of the energy drought (e.g. sunrise). Once charge accumulation resumes, Flute reverts to the standard, conservative, AsTAR strategy. In this way, available energy is more fully exploited overnight. </div>

The parameters of the proposed algorithm is described in <strong> Table 1 </strong> as follows:

**<div align="center">
  Table 1: User-defined energy drought task rates for AsTAR++**
</div>

<p align="center">
   <img width="450" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/12d5ea07-117e-4704-9371-36fcdc00ac64">
</p>


## 3. Implementation
### 3.1. Implementing the proposed AsTAR++ algorithm on LTE-M nodes
For LTE_M nodes, the circuitdojo_feather_nrf9160 board is used.

<p align="center">
   <img width="350" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/8e5c1a75-011e-4c58-9604-d834a3b9f65b"> <img width="400" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/c5457a4d-94c8-4a32-a166-e696c6b28684">
</p>

**<div align="center">
  Fig 3. The image of Circuitdojo nrf9160**
</div>

<div align="justify">  The nRF9160 Feather by Circuit Dojo is a single-board development for bringing your LTE-M and NB-IoT applications to life. The circuitdojo_feather_nrf9160 board configuration leverages the pre-existing support for the Nordic Semiconductor nRF9160. Supported nRF9160 peripherals such as: </div>

- ADC 
- CLOCK
- FLASH
- GPIO
- I2C
- MPU
- NVIC
- PWM
- RTC
- Segger RTT (RTT Console)
- SPI
- UARTE
- WDT
- IDAU. 

<div align="justify">  It features a Nordic Semiconductor nRF9160-SICA part. This part is capable of both CAT M1 LTE and NB-IoT for communication with the outside world. It's compatible primarily with Zephyr via the nRF Connect SDK. More information about the board can be found at https://docs.circuitdojo.com/nrf9160-introduction.html. Reference implementations for the Zephyr development environments are shown at https://docs.zephyrproject.org/3.2.0/develop/tools/index.html. </div>

<br/>
<div align="justify">  Besides, tutorials from Nordic will give you basic backgrounds to start implementing a Zephyr project for a Circuitdojo circuitdojo_feather_nrf9160. Please see at https://academy.nordicsemi.com/courses/nrf-connect-sdk-fundamentals/lessons/lesson-2-reading-buttons-and-controlling-leds/topic/gpio-generic-api/ </div>

<br/>
<div align="justify"> In our work, we offer a <strong> reference code </strong> for outdoor and indoor LTE-M Node that can help everyone refer to it to develop a Battery-free IoT application easily. The reference code is available at https://github.com/LuckyMan23129/Flute/tree/master/Source%20code/LTE-M. LTE-M is a low-power cellular technology that reduces power through local Power Saving Mode (PSM) or extended Discontinuous Reception. Therefore, due to no downlink in our LTE-M application, the PSM was set longer than the sleep time, ensuring immediate return after sending data over UDP and power efficiency. </div>


### 3.2. Implementing LTE-M gateway





### 3.3. Implementing the proposed AsTAR++ algorithm on 433Mhz nodes
<div align="justify"> Regarding 433Mhz nodes, This work uses Adafruit Feather M0 RFM95 LoRa Radio (433MHz) board. The images and pinout of the board are shown in <strong> Figure 4 </strong> and <strong> Figure 5 </strong>. There are also a lot of pins and ports on the Feather M0 Radio board which is covered in-depth at https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/pinouts 
</div>

 </br> 
<p align="center">
   <img width="270" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/0b812eb8-f5f0-424e-94f7-d84e461dd5bc">
</p>

**<div align="center">
  Fig 4. The image of the Adafruit Feather M0 RFM95 LoRa Radio board**
</div>
<br/>

<p align="center">
   <img width="800" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/cab9d6c3-0283-4b41-871d-677b5416197f">
</p>

**<div align="center">
  Fig 5. The image of Adafruit Feather M0 RFM95 LoRa Radio board**
</div>

Below are some handy specifications of M0 RFM95 LoRa Radio board:
- Measures 2.0" x 0.9" x 0.3" (51mm x 23mm x 8mm) without headers soldered in
- Light as a (large?) feather - 5.8 grams
- ATSAMD21G18 @ 48MHz with 3.3V logic/power
- No EEPROM
- 3.3V regulator with 500mA peak current output USB native support, comes with USB bootloader and serial port debugging
- You also get tons of pins - 20 GPIO pins
- Hardware Serial, hardware I2C, hardware SPI support
- 8 x PWM pins
- 10 x analog inputs
- 1 x analog output
- Built-in 100mA lipoly charger with charging status indicator LED
- Pin #13 red LED for general purpose blinking
- Power/enable pin
- 4 mounting holes
- Reset button

<div align="justify"> To support developers, Adafruit also provides a series of basic examples about how to install necessary libraries and how to implement simple LoRa-433MHz applications on Arduino IDE as depicted at https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/overview.  </div>

</br>
<div align="justify"> Similar to LTE-M nodes, reference implementations are available for the Arduino development environments for outdoor and indoor LoRa 433MHz.  This facilitates developers to develop a battery-free LoRa IoT node more easily than ever. The detailed information on the source code, please see here https://github.com/LuckyMan23129/Flute/tree/master/Source%20code/LoRa%20AsTAR%2B%2B. </div>


### 3.4. Implementing a LoRa 433MHz Gateway

### * Hardware
We also implemented a one-channel 433MHz gateway. The image of the gateway is shown in <strong> Figure x </strong>.
</br>

<p align="center">
   <img width="257" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/e6875b2f-76f7-40d2-ad01-6062f593266b">
</p>

<div align="center">
  <strong> Fig 6. The image of the one-channel 433MHz LoRa gateway  </strong>
</div>

<div align ="justify"> The Structure of the gateway consists of 2 main components <strong> Raspberry Pi 3 Model B </strong> and <strong> a RFM95W LoRa Radio Transceiver BR</strong>. The image of the LoRa Radio Transceiver is shown in the figure below. </div>

<p align="center">
   <img width="250" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/768a3d4c-250f-4298-a2cb-235aba6cba95">
</p>
<div align="center">
  <strong> Fig 7. An image of RFM95W LoRa Radio Transceiver BR   </strong>
</div>
</br>

The connection of the Raspi and the LoRa transceiver is depicted as follows.

<p align="center">
   <img width="500" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/c935f590-4646-4fb7-9ef6-c5fa7d7086b5">
</p>
<div align="center">
  <strong> Fig 8. The connection of the Raspi and the LoRa transceiver  </strong>
</div>
</br>

### * Software
<div Align="justify"> For the software of Raspi, after installing Raspbian on the Raspberry Pi. From a console, run the following command to install the RFM9x Python package: </div>

``` javascript
pip3 install adafruit-circuitpython-rfm9x
```

<div Align="justify"> A Python script is run on Rasp to forward messages Raspi receives from the LoRa transceiver to the server. The reference Python script is shown at the link "xxxx". </div>















[comment]: <> (Main link: https://www.digikey.be/nl/maker/projects/arduino-lora-weather-sensor/01ff62b930ce464da429222ddbc06854)

## 4. Experimental results
<div Align="justify"> The Flute power board uses a standard connector for AdaFruit Feather format development boards. All boards are powered by four super-capacitors, selected based on high energy density and low ESR. Energy is harvested using two monocrystalline solar panels in parallel. Nodes are enclosed in waterproof
cases for indoor and outdoor tests, as shown in the figure below. </div>
</br>

<p align="center">
   <img width="700" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/67c01353-ba07-4d0d-8429-b08e52fc47ec">
</p>
**<div align="center">
  Fig. 9: Prototype Flute board (left) and finished battery-free EH nodes (right)**
</div>

<div align="justify"> We evaluate the performance of Flute using two IoT daughter-boards described in through a 7-day test deployed in Vietnam and Belgium under outdoor and indoor conditions. The boards were connected and ran the Flute software locally. Each of the 7-day experiments was performed at a different time,
therefore absolute results of the graphs cannot be directly compared due to changing energy availability. However, the relative trends remain clear. From the results shown in <strong> Figures 9 </strong> and <strong> Figure 10</strong>, label (A) denotes the maximumVoltage, (B) optimumVoltage, (C) shutOffVoltage plus a 10% safety margin and (D) NightOptimumVoltage, respectively. For the sleep time (E) represents maximumSleepTime, (F) nightMinimumSleepTime and (G) minimumSleepTime, respectively. </div>

### 4.1. Outdoor Operation

<div align="center">
  <strong> Table 2: 1-week Flute message rate metrics for AsTAR and AsTAR++ across two deployment locations </strong>
</div>

<p align="center">
   <img width="600" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/42b5e881-0478-4969-b8c4-11cf1d51f06e">
</p>

<div align="justify"> <strong> Table 2 </strong> and <strong> Figure 9 </strong> show outdoor performance of baseline AsTAR compared to AsTAR++ for each of the two boards. AsTAR ensures reliability through a conservative approach; throttling software to a minimum of one execution every two hours at night when harvesting energy is unavailable. Conversely, when the sun rises, AsTAR rapidly acquires an optimum charge level and commensurately increases task rates. This daily pattern repeats throughout the experiment. Analysis of the nodes’ night-time behaviour reveals the AsTAR inefficiency; while nodes can safely operate down to 2.6V, the capacitor voltage never falls below 3.5V, leaving a large amount of unused charge. While this is reasonable with unpredictable EH scenarios, it is inefficient for diurnal scenarios. </div>
<div align="justify"> In contrast, AsTAR++ tracks the night-time energy droughts length to safely use most of the available charge overnight. In all cases, AsTAR++ reaches approximately 1.1x the brownout voltage of the daughter-board (2.86V for LoRa and 3.3V for LTE-M). This way, it efficiently uses the daytime charge, increasing messaging rates while preserving reliability with changing energy availability. </div>
<div align="justify"> Critically, Flute availability remains unaffected, delivering 100% using both algorithms. Our results demonstrate that in certain scenarios battery-free EH platforms can deliver very high levels of availability. </div>

<br/>
<p align="center">
   <img width="700" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/7f03142c-3766-4233-a285-fba19f0bec7c">
</p>

<div align="center">
  <strong> Fig. 9: Outdoor performance graphs for AsTAR and AsTAR++ algorithms </strong>
</div>


### 4.2. Indoor Operation

<p align="center">
   <img width="700" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/b0ffbbb8-8c4b-4d3f-8629-59e4b558858b">
</p>

<div align="center">
  <strong> Fig. 10: Indoor performance of AsTAR and AsTAR++ algorithms </strong>
</div>
</br>

<div align="justify"> <strong> Table 2 </strong> and <strong> Figure 10 </strong> shows Flute indoor performance across the two locations. The indoor nodes received sunlight for just a few hours daily. Specifically, the nodes were deployed in summer of 2023 with many days of rain and inside of laboratories opening briefly without artificial lightening. Annotations (A) through (G) remain the same. The graphs show that AsTAR and AsTAR++ algorithms ensure sustainable operation even with reduced amount of harvested solar energy when indoors. Additionally, AsTAR++ significantly outperforms AsTAR through more aggressive overnight energy use, without negatively impacting device availability.
As shown in Table 2, with AsTAR, LoRa nodes achieve an average 0.51 messages per hour indoor and 2.47 outdoor. AsTAR++ improves messaging rate by over 16x for indoor and 5x for outdoor, respectively. With AsTAR, LTE-M nodes achieve an average 0.53 messages per hour while indoor and 6.84 outdoor. Again, AsTAR++ improves messaging by over 1.7x for indoor and 2.2x for outdoor. </div>

## 5. Contributions
<div align="justify"> Contributions of this work facilitate the vision of a battery-free EH IoT by enabling PnP conversion of commodity dev-boards into battery-free EH platforms. A week-long evaluation of our approach shows a promising performance profile. Specifically, Flute sustainably supports simple wireless sensing applications in both indoor and outdoor scenarios running on multiple networks and processors using solar power alone. Moreover, with diurnal operation, Flute outperforms the original AsTAR algorithm by a factor of 2x to 17x while always maintaining a 10% safety margin, well over the brown-out voltage. </div>

## 6. Future work
<div align="justify">   Our future work will focus on three scientific tracks: (i.) Improving self-adaptive energy management by broadening its scope beyond the application layer and integrating it into the OS and network. (ii.) Implementing approaches to simplify developer construction of complex multi-tasking schedules. (iii.) Broadening Flute evaluation to include more EH methods like thermal, RF and kinetic. Additionally, as an engineering track, we intend to establish large-scale Flute deployments in multiple locations for a year-long study across seasons. </div>

## 7. Authors and acknowledgment
<div align="justify"> This work is partially funded by VLIR-UOS (IUC-QNU/KU Leuven, VN2022IUC044A101), the KU Leuven Research Fund (ReSOS, C3/20/014), and VLAIO
(TRUSTI, HBC.2021.0742). </div>

