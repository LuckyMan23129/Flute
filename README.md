# Flute: Enabling a Battery-free and Energy Harvesting Ecosystem for the Internet of Things


## 1. Description
Nowadays, most Internet of Things (IoT) devices still operate on batteries, offering lifetimes of just a few years; leading to high maintenance costs and excess waste. Energy Harvesting (EH) in combination with super-capacitor charge storage offers a solution, however, it is considered complex and unreliable, hampering its real-world deployment. To address this problem, we contribute Flute, a power management system for building battery-free IoT deployments. Unlike prior work, Flute focuses on transforming existing IoT development boards into battery-free devices. Reliable operation is achieved through a combination of generic power management hardware and self-adaptive software enabling sustainable operation in the face of dynamic power supply and demand. We evaluate our approach through a series of diverse one-week solar EH scenarios and show that Flute efficiently harvests energy and achieves reliable operation for a range of unmodified IoT development boards using LTE-M and LoRa. Hence, Flute provides a promising foundation for building a battery-free and EH ecosystem for the Internet of Things.

## 2. The Design of Flute
We define the following requirements for the design of Flute:
- First, **Low power duty cycling**: Sustainable EH requires aggressive duty cycling. However, the power efficiency of IoT development boards varies dramatically. Flute addresses this problem via a power board that allows the host board to be powered down or placed into deep sleep mode between executions.
- Second, **Adaptive task scheduling**: Intelligent scheduling is required to tailor application energy demands to match available energy supply. However, additional support is required to enable more consistent scheduling in the case of diurnal EH patterns.
- Third, **PnP operation**: Flute will support the existing ecosystem of IoT development boards by offering the first PnP battery-free and EH solution for the boards, specifically focusing on the Adafruit Feather due to its extensive range and popularity.
- Finally, **Developer support**: Flute contributes energy management libraries that
simplify task scheduling, time management, and handling power faults. Refer-
ence implementations are available for the Arduino and Zephyr¶ development
environments
![Figure11](https://github.com/LuckyMan23129/Flute/assets/141725842/cfe9bf0a-529b-48e2-bc80-37559d8d2dcd)
**Fig 1.  Block diagram of the Flute PnP power board**

![Figure2](https://github.com/LuckyMan23129/Flute/assets/141725842/38830606-cbdd-4c90-a091-20c9ea03b0f8)
**Fig 2. The Flute Hardware/Software Architecture**

 The hardware goal of Flute is to convert commodity IoT development boards into battery-free EH devices. Flute’s software goal is to schedule tasks: (i.) as frequently as possible, while (ii.) accumulating an optimum charge level and (iii.) preserving system operation by throttling execution when environmental energy is lost. This requires a PnP power supply board and software support to manage energy usage.

## 3. Installation and Sourcecode
Flute aims to convert commodity IoT development boards into battery-free EH devices that can work in either outdoor or indoor environments reliably. To validate this, we employed long-range networking, 433MHz LoRa, and LTE-M, parameterized for low power and extended coverage. To show its deployment in the real world, we deployed Flute both outdoors and indoors and in 2 different countries in 2 different continents Vietnam and Belgium.
The Psuedo code of proposed algorithms is shown as follows.
```javascript
1    getAdaptedRate ( V_New , V_Prev ) {
2    IF ( V_New - V_Prev ) < 0 for last 10 minutes AND V_New <=
       V_Day_Optimum
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
Flute uses proposed AsTAR++ algorithm which manages energy droughts by tracking the duration of power outages using an Exponentially Weighted Moving Average. When an energy drought is detected based on 10 minutes of no charge gain (e.g. sunset), Flute changes strategies, aiming to schedule tasks at such a rate that 90% of the available charge is used by the expected end of the energy drought (e.g. sunrise). Once charge accumulation resumes, Flute reverts to the standard, conservative, AsTAR strategy. In this way, available energy is more fully exploited overnight.
### 3.1. Applying the proposed AsTAR++ algorithm  on LTE-M nodes
In this application, the circuitdojo_feather_nrf9160 board is used.

<img width="500" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/8e5c1a75-011e-4c58-9604-d834a3b9f65b"> <img width="500" alt="image" src="https://github.com/LuckyMan23129/Flute/assets/141725842/c5457a4d-94c8-4a32-a166-e696c6b28684">

**Fig 3. The image of Circuitdojo nrf9160**

The nRF9160 Feather by Circuit Dojo is a single-board development for bringing your LTE-M and NB-IoT applications to life. The circuitdojo_feather_nrf9160 board configuration leverages the pre-existing support for the Nordic Semiconductor nRF9160. Supported nRF9160 peripherals include:
* ADC
* CLOCK
* FLASH
* GPIO
* I2C
* MPU
* NVIC
* PWM
* RTC
* Segger RTT (RTT Console)
* SPI
* UARTE
* WDT
* IDAU

It features a Nordic Semiconductor nRF9160-SICA part. This part is capable of both CAT M1 LTE and NB-IoT for communication with the outside world. It's compatible primarily with Zephyr via the nRF Connect SDK. More information about the board can be found at the https://docs.circuitdojo.com/nrf9160-introduction.html. Reference implementations for the Zephyr development environments is shown at: https://docs.zephyrproject.org/3.2.0/develop/tools/index.html

Besides, tutorials from Nordic (see also at https://academy.nordicsemi.com/courses/nrf-connect-sdk-fundamentals/lessons/lesson-2-reading-buttons-and-controlling-leds/topic/gpio-generic-api/) will give you basic backgrounds so that you can start implementing a zephyr Project for a Circuitdojo circuitdojo_feather_nrf9160.

In our work, we offer a reference code for outdoor and indoor LTE-M Node available at: https://github.com/LuckyMan23129/Flute/tree/master/Source%20code/LTE-M that can help everyone on it to develop a Battery-free IoT application easily. 
LTE-M is a low-power cellular technology that reduces power through local Power Saving Mode (PSM) or extended Discontinuous Reception. Therefore, due to no downlink in our LTE-M application, the PSM was set longer than the sleep time, ensuring immediate return after sending data over UDP and power efficiency.

### 3.2. Applying the proposed AsTAR++ algorithm  on 433Mhz nodes
Similar to LTE-M nodes, the reference source code for outdoor and indoor LoRa 433MHz is also described in a GitHub as follows: https://github.com/LuckyMan23129/Flute/tree/master/Source%20code/LoRa%20AsTAR%2B%2B 

Reference implementations are available for the Arduino development environments .............


## 4. Experimental results
![Biểu đồ không có tiêu đề drawio](https://github.com/LuckyMan23129/Flute/assets/141725842/6bff642e-8ed6-4e80-9e45-cfac93b6b6cc) 
****Fig. 3: Prototype Flute board (left) and finished battery-free EH nodes (right)****
We evaluate the performance of Flute using two IoT daughter-boards described in Section 4 through a 7-day test deployed in Vietnam and Belgium under outdoor and indoor conditions. The boards were connected and ran the Flute software locally. Each of the 7-day experiment was performed at a different time,
therefore absolute results of the graphs cannot be directly compared due to changing energy availability. However, the relative trends remain clear. From the results shown in Figures 4 and 5, label (A) denotes the maximumVoltage, (B) optimumVoltage, (C) shutOffVoltage plus a 10% safety margin and (D) NightOptimumVoltage, respectively. For the sleep time (E) represents maximumSleepTime, (F) nightMinimumSleepTime and (G) minimumSleepTime, respectively.
### 4.1. Outdoor Operation
Figure 4 shows outdoor performance of baseline AsTAR compared to AsTAR++ for each of the two boards. AsTAR ensures reliability through a conservative approach; throttling software to a minimum of one execution every two hours at night when harvesting energy is unavailable. Conversely, when the sun rises, AsTAR rapidly acquires an optimum charge level and commensurately increases task rates. This daily pattern repeats throughout the experiment. Analysis of the nodes’ night-time behaviour reveals the AsTAR inefficiency; while nodes can safely operate down to 2.6V, the capacitor voltage never falls below 3.5V, leaving a large amount of unused charge. While this is reasonable with unpredictable EH scenarios, it is inefficient for diurnal scenarios.
In contrast, AsTAR++ tracks the night-time energy droughts length to safely use most of the available charge overnight. In all cases AsTAR++ reaches approximately 1.1x the brownout voltage of the daughter-board (2.86V for LoRa and 3.3V for LTE-M). This way, it efficiently uses the daytime charge, increasing messaging rates while preserving reliability with changing energy availability.
Critically, Flute availability remains unaffected, delivering 100% using both algorithms. Our results demonstrate that in certain scenarios battery-free EH platforms can deliver very high levels of availability.

**Table 1: User-defined energy drought task rates for AsTAR++**
![Table1 drawio](https://github.com/LuckyMan23129/Flute/assets/141725842/76711c46-18d1-4482-a6cb-3905b8ce7c5a)


**Table 2: 1-week Flute message rate metrics for AsTAR and AsTAR++ across two deployment locations**
![Table 2](https://github.com/LuckyMan23129/Flute/assets/141725842/5b94967a-6a0d-4e9b-a337-eb3f80b3c89a)

![Fig 4](https://github.com/LuckyMan23129/Flute/assets/141725842/3fabbabe-a1c9-4904-abe5-f9065f58ecdd)

### 4.2. Indoor Operation
![Fig 5](https://github.com/LuckyMan23129/Flute/assets/141725842/a6b589f4-4324-4737-80c4-a8259c84928d)

Figure 5 shows Flute indoor performance across the two locations. The indoor nodes received sunlight for just a few hours daily. Specifically, the nodes were deployed in summer of 2023 with many days of rain and inside of laboratories opening briefly without artificial lightening. Annotations (A) through (G) remain the same. The graphs 
how that AsTAR and AsTAR++ algorithms ensure sustainable operation even with reduced amount of harvested solar energy when indoors. Additionally, AsTAR++ significantly outperforms AsTAR through more aggressive overnight energy use, without negatively impacting device availability.
As shown in Table 2, with AsTAR, LoRa nodes achieve an average 0.51 messages per hour indoor and 2.47 outdoor. AsTAR++ improves messaging rate by over 16x for indoor and 5x for outdoor, respectively. With AsTAR, LTE-M nodes achieve an average 0.53 messages per hour while indoor and 6.84 outdoor. Again, AsTAR++ improves messaging by over 1.7x for indoor and 2.2x for outdoor.

## 5. Contributions
Contributions of this paper facilitate the vision of a battery-free EH IoT by enabling PnP conversion of commodity dev-boards into battery-free EH platforms. A week-long evaluation of our approach shows a promising performance profile. Specifically, Flute sustainably supports simple wireless sensing applications in both indoor and outdoor scenarios running on multiple networks and processors using solar power alone. Moreover, with diurnal operation, Flute outperforms the original AsTAR algorithm by a factor of 2x to 17x while always maintaining a 10% safety margin, well over the brown-out voltage.

## 6. Future work
Our future work will focus on three scientific tracks: (i.) Improving self-adaptive energy management by broadening its scope beyond the application layer and integrating it into the OS and network. (ii.) Implementing approaches to simplify developer construction of complex multi-tasking schedules. (iii.) Broadening Flute evaluation to include more EH methods like thermal, RF and kinetic. Additionally, as an engineering track, we intend to establish large-scale Flute deployments in multiple locations for a year-long study across seasons.

## 7. Authors and acknowledgment
This work is partially funded by VLIR-UOS (IUC-QNU/KU Leuven, VN2022IUC044A101), the KU Leuven Research Fund (ReSOS, C3/20/014), and VLAIO
(TRUSTI, HBC.2021.0742).

