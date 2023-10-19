# Flute: Enabling a Battery-free and Energy Harvesting Ecosystem for the Internet of Things


## Description
Nowadays, most Internet of Things (IoT) devices still operate on batteries, offering lifetimes of just a few years; leading to high maintenance costs and excess waste. Energy Harvesting (EH) in combination with super-capacitor charge storage offers a solution, however, it is considered complex and unreliable, hampering its real-world deployment. To address this problem, we contribute Flute, a power management system for building battery-free IoT deployments. Unlike prior work, Flute focuses on transforming existing IoT development boards into battery-free devices. Reliable operation is achieved through a combination of generic power management hardware and self-adaptive software enabling sustainable operation in the face of dynamic power supply and demand. We evaluate our approach through a series of diverse one-week solar EH scenarios and show that Flute efficiently harvests energy and achieves reliable operation for a range of unmodified IoT development boards using LTE-M and LoRa. Hence, Flute provides a promising foundation for building a battery-free and EH ecosystem for the Internet of Things.

## The Design of Flute
![Figure11](https://github.com/LuckyMan23129/Flute/assets/141725842/cfe9bf0a-529b-48e2-bc80-37559d8d2dcd)
**Fig 1.  Block diagram of the Flute PnP power board**


![Figure2](https://github.com/LuckyMan23129/Flute/assets/141725842/38830606-cbdd-4c90-a091-20c9ea03b0f8)
**Fig. 2: The Flute Hardware/Software Architecture**

## Implementation
Energy drought listing of AsTAR++ is shown as follows:
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
![Biểu đồ không có tiêu đề drawio](https://github.com/LuckyMan23129/Flute/assets/141725842/6bff642e-8ed6-4e80-9e45-cfac93b6b6cc)
****Fig. 3: Prototype Flute board (left) and finished battery-free EH nodes (right)****

## 5. Experimental results
We evaluate the performance of Flute using two IoT daughter-boards described in Section 4 through a 7-day test deployed in Vietnam and Belgium under outdoor and indoor conditions. The boards were connected and ran the Flute software locally. Each of the 7-day experiment was performed at a different time,
therefore absolute results of the graphs cannot be directly compared due to changing energy availability. However, the relative trends remain clear. From the results shown in Figures 4 and 5, label (A) denotes the maximumVoltage, (B) optimumVoltage, (C) shutOffVoltage plus a 10% safety margin and (D) NightOptimumVoltage, respectively. For the sleep time (E) represents maximumSleepTime, (F) nightMinimumSleepTime and (G) minimumSleepTime, respectively.

### 5.1. Outdoor Operation
Figure 4 shows outdoor performance of baseline AsTAR compared to AsTAR++ for each of the two boards. AsTAR ensures reliability through a conservative approach; throttling software to a minimum of one execution every two hours at night when harvesting energy is unavailable. Conversely, when the sun rises, AsTAR rapidly acquires an optimum charge level and commensurately increases task rates. This daily pattern repeats throughout the experiment. Analysis of the nodes’ night-time behaviour reveals the AsTAR inefficiency; while nodes can safely operate down to 2.6V, the capacitor voltage never falls below 3.5V, leaving a large amount of unused charge. While this is reasonable with unpredictable EH scenarios, it is inefficient for diurnal scenarios.
In contrast, AsTAR++ tracks the night-time energy droughts length to safely use most of the available charge overnight. In all cases AsTAR++ reaches approximately 1.1x the brownout voltage of the daughter-board (2.86V for LoRa and 3.3V for LTE-M). This way, it efficiently uses the daytime charge, increasing messaging rates while preserving reliability with changing energy availability.
Critically, Flute availability remains unaffected, delivering 100% using both algorithms. Our results demonstrate that in certain scenarios battery-free EH platforms can deliver very high levels of availability.

**Table 1: User-defined energy drought task rates for AsTAR++**
![Table1 drawio](https://github.com/LuckyMan23129/Flute/assets/141725842/76711c46-18d1-4482-a6cb-3905b8ce7c5a)


**Table 2: 1-week Flute message rate metrics for AsTAR and AsTAR++ across two deployment locations**
![Table 2](https://github.com/LuckyMan23129/Flute/assets/141725842/5b94967a-6a0d-4e9b-a337-eb3f80b3c89a)

![Fig 4](https://github.com/LuckyMan23129/Flute/assets/141725842/3fabbabe-a1c9-4904-abe5-f9065f58ecdd)
![Fig 5](https://github.com/LuckyMan23129/Flute/assets/141725842/a6b589f4-4324-4737-80c4-a8259c84928d)

### 5.2. Indoor Operation
Figure 5 shows Flute indoor performance across the two locations. The indoor nodes received sunlight for just a few hours daily. Specifically, the nodes were deployed in summer of 2023 with many days of rain and inside of laboratories opening briefly without artificial lightening. Annotations (A) through (G) remain the same. The graphs 
how that AsTAR and AsTAR++ algorithms ensure sustainable operation even with reduced amount of harvested solar energy when indoors. Additionally, AsTAR++ significantly outperforms AsTAR through more aggressive overnight energy use, without negatively impacting device availability.
As shown in Table 2, with AsTAR, LoRa nodes achieve an average 0.51 messages per hour indoor and 2.47 outdoor. AsTAR++ improves messaging rate by over 16x for indoor and 5x for outdoor, respectively. With AsTAR, LTE-M nodes achieve an average 0.53 messages per hour while indoor and 6.84 outdoor. Again, AsTAR++ improves messaging by over 1.7x for indoor and 2.2x for outdoor.

## Contributing
Contributions of this paper facilitate the vision of a battery-free EH IoT by enabling PnP conversion of commodity dev-boards into battery-free EH platforms. A week-long evaluation of our approach shows a promising performance profile. Specifically, Flute sustainably supports simple wireless sensing applications in both indoor and outdoor scenarios running on multiple networks and processors using solar power alone. Moreover, with diurnal operation, Flute outperforms the original AsTAR algorithm by a factor of 2x to 17x while always maintaining a 10% safety margin, well over the brown-out voltage.

## Future work
Our future work will focus on three scientific tracks: (i.) Improving self-adaptive energy management by broadening its scope beyond the application layer and integrating it into the OS and network. (ii.) Implementing approaches to simplify developer construction of complex multi-tasking schedules. (iii.) Broadening Flute evaluation to include more EH methods like thermal, RF and kinetic. Additionally, as an engineering track, we intend to establish large-scale Flute deployments in multiple locations for a year-long study across seasons.

## Authors and acknowledgment
This work is partially funded by VLIR-UOS for the IUC-QNU/KU Leuven project (VN2022IUC044A101), the KU Leuven Research fund and the VLAIO TRUSTI project.

=================================================================== The end ========================================================================









## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a 
'''
Requirements subsection.
'''
## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Deployment
```bash
  npm run deploy
```

## Usage/Examples

```javascript
import Component from 'my-project'

function App() {
  return <Component />
}
```





## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
