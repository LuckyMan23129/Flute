# Gateway2 (433MHz and for Node 101 to Node 105)

# ********************************************* For Adafruit LoRa concentrator and Rasp ****************************************** S1
import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_rfm9x

Freq = 433.0
#Freq = 434.0
# ********************************************* For Adafruit LoRa concentrator and Rasp ****************************************** E1


# *****************************************************  For Python  *********************************************** S2
from datetime import datetime
import json
from base64 import b64encode
#import paho.mqtt.client as mqtt
# *****************************************************  For Python  *********************************************** E2


# ************************************************* For INFLUXDB 1.7 *********************************************** S3
from influxdb import InfluxDBClient
my_influxdb_url = '3.123.xxx.xx'            
my_influxdb_port = 6808
my_influxdb_user = 'xxxxxx'
my_influxdb_passs = 'YRYUVwMepNWxxxxx'
my_influxdb_Database = 'nes_xx'    # Measurement = table
# ************************************************* For INFLUXDB 1.7 *********************************************** E3

# ********************************** For Weather API ******************************************************** S1
import requests
# import json
 
# Enter your API key here
api_key = "0fb1c49b9f013892b4e1f992d571xxxx"    # Vu - https://home.openweathermap.org/api_keys
                                                # Vu -  https://pythonhowtoprogram.com/get-weather-forecasts-and-show-it-on-a-chart-using-python-3/

#lat = 50.86427869277179        # Node 1 - The latitude of the Node Location (Leuven)          - @@@@@@@@@@@@@@@@@@@@
#lon = 4.678953323558871        # Node 1 - The longitude of the Node Location (Leuven)         - @@@@@@@@@@@@@@@@@@@@
lat = 13.759178530633887        # Node 2 - The latitude of the Node Location (Quy Nhon)        - @@@@@@@@@@@@@@@@@@@@
lon = 109.2178465677162         # Node 2 - The longitude of the Node Location (Quy Nhon)       - @@@@@@@@@@@@@@@@@@@@
coord_API_endpoint = "http://api.openweathermap.org/data/2.5/weather?"
lat_long = "lat=" + str(lat)+ "&lon=" + str(lon)
join_key = "&appid=" + api_key
units = "&units=metric"

current_coord_weather_url= coord_API_endpoint + lat_long + join_key + units
# ************************************************ For Weather API ***************************************************** E1


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Receive data and show on Rasp Screen ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ S 9_1

# Configure RFM9x LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Attempt to set up the RFM9x module
try:
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, Freq)
    rfm9x.tx_power = 23 # range from 5 to 23 if high_power is True
    rfm9x.coding_rate = 5 # range from 5 to 8
    rfm9x.spreading_factor = 12 # range from 6 tot 12
    rfm9x.signal_bandwidth = 125000
    # valid values 7800, 10400, 15600, 20800, 31250, 41700, 62500, 125000, 250000
    
    print('RFM9x detected')
except RuntimeError:
    print('RFM9x error')


# Wait for LoRa packets
while True:
    packet = None
    packet = rfm9x.receive()
    if packet != None:
        
        print("Received:",  str(packet))
        
        # Split packet
        from_addr = packet[0]
        to_addr = packet[1]
        Water = int.from_bytes(packet[2:4], byteorder='little') / 10.0
        SuperCap = int.from_bytes(packet[4:6], byteorder='little') / 10.0
        Rate = int.from_bytes(packet[6:8], byteorder='little')              # Thuc ra Khong luu gia tri "nhiet do" ma la "Sleep time"
        SleepTime = int.from_bytes(packet[6:8], byteorder='little')
        # Printing out to see Which Node send data to Gateway
        if (((from_addr == 101) or (from_addr == 102) or (from_addr == 103) or (from_addr == 104) or (from_addr == 105)) and (to_addr == 2)):
        # Print results
            print("From:", from_addr)       # "from_addr" la dia chi cua node ma send den
            print("To:", to_addr)           # "to_addr" La dia chi Gateway nhan TN



    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ S 9_2
        ####################################  Send Node 1's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 101)  and (to_addr == 2)):

            # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
    
            json_data = requests.get(current_coord_weather_url).json()

            x = json_data
            if json_data["cod"] != "404":
 
                # store the value of "main"
                # key in variable y
                y = x["main"]
 
                # store the value corresponding
                # to the "temp" key of y
                current_temperature = y["temp"]
 
                # store the value corresponding
                # to the "pressure" key of y
                current_pressure = y["pressure"]
 
                # store the value corresponding
                # to the "humidity" key of y
                current_humidity = y["humidity"]
 
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
 
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]
                print (" ")
                print ("****************************************** Weather API *******************************************")
               
            else:
                print(" LONG and LAT Not Found ")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7

            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
            json_body = [
            {
                "measurement": "Table101_Nodev101",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v101",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam101)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam101)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    #"Temperature (Vietnam101)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam101)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature (Vietnam101)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam101)" : current_humidity,
                    "Current_Weather (Vietnam101)" : weather_description,
                }
            }
            ]    
    
            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
            #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
            InfluxDB_client.write_points(json_body)
            
            print("Data from Node 101: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 1's Data to InfluxDB cloud V1.7 ##################################### End



        ####################################  Send Node 2's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 102)  and (to_addr == 2)):
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            
            # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
            # https://medium.com/@joseph.magiya/weather-data-and-forecasts-from-open-weather-api-1636691d5ba
    
            json_data = requests.get(current_coord_weather_url).json()

            x = json_data
            if json_data["cod"] != "404":
 
                # store the value of "main"
                # key in variable y
                y = x["main"]
 
                # store the value corresponding
                # to the "temp" key of y
                current_temperature = y["temp"]
 
                # store the value corresponding
                # to the "pressure" key of y
                current_pressure = y["pressure"]
 
                # store the value corresponding
                # to the "humidity" key of y
                current_humidity = y["humidity"]
 
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
 
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]
                print (" ")
                print ("****************************************** Weather API *******************************************")
               
            else:
                print(" LONG and LAT Not Found ")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7
        
            json_body = [
            {
                "measurement": "Table102_Nodev102",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v102",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam102)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam102)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam102)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam102)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam102)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam102)" : current_humidity,
                    "Current_Weather (Vietnam102)" : weather_description,
            
                }
            }
            ]    
    
            # Send data to InfluxDB server ************************** 
    
            InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
            #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
            InfluxDB_client.write_points(json_body)

            print("Data from Node 102: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 2's Data to InfluxDB cloud V1.7 ##################################### End



        ####################################  Send Node 3's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 103)  and (to_addr == 2)):
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

            # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
            json_data = requests.get(current_coord_weather_url).json()

            x = json_data
            if json_data["cod"] != "404":
 
                # store the value of "main"
                # key in variable y
                y = x["main"]
 
                # store the value corresponding
                # to the "temp" key of y
                current_temperature = y["temp"]
 
                # store the value corresponding
                # to the "pressure" key of y
                current_pressure = y["pressure"]
 
                # store the value corresponding
                # to the "humidity" key of y
                current_humidity = y["humidity"]
 
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
 
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]
                print (" ")
                print ("****************************************** Weather API *******************************************")
               
            else:
                print(" LONG and LAT Not Found ")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7

            json_body = [
            {
                "measurement": "Table103_Nodev103",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v103",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam103)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam103)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam103)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam103)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam103)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam103)" : current_humidity,
                    "Current_Weather (Vietnam103)" : weather_description,
            
                }
            }
            ]    
    
            # Send data to InfluxDB server ************************** 
            InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
            #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
            InfluxDB_client.write_points(json_body)

            print("Data from Node 103: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 3's Data to InfluxDB cloud V1.7 ##################################### End



         ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 104)  and (to_addr == 2)):
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

            # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
            json_data = requests.get(current_coord_weather_url).json()

            x = json_data
            if json_data["cod"] != "404":
 
                # store the value of "main"
                # key in variable y
                y = x["main"]
 
                # store the value corresponding
                # to the "temp" key of y
                current_temperature = y["temp"]
 
                # store the value corresponding
                # to the "pressure" key of y
                current_pressure = y["pressure"]
 
                # store the value corresponding
                # to the "humidity" key of y
                current_humidity = y["humidity"]
 
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
 
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]
                print (" ")
                print ("****************************************** Weather API *******************************************")
               
            else:
                print(" LONG and LAT Not Found ")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            json_body = [
            {
                "measurement": "Table104_Nodev104",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v104",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam104)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam104)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam104)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam104)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam104)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam104)" : current_humidity,
                    "Current_Weather (Vietnam104)" : weather_description,
            
                    #"RSSI": my_RSSI_Node1                               # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"RSSI": my_RSSI_Node2                               # Node 2  - @@@@@@@@@@@@@@@@@@@@
            
                }
            }
            ]    
    
            # Send data to InfluxDB server ************************** 
            InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
            #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
            InfluxDB_client.write_points(json_body)

            print("Data from Node 104: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### End
        
        
        ####################################  Send Node 5's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 105) and (to_addr == 2)):
            # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        
        # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
            # https://medium.com/@joseph.magiya/weather-data-and-forecasts-from-open-weather-api-1636691d5ba
    
            json_data = requests.get(current_coord_weather_url).json()

            x = json_data
            if json_data["cod"] != "404":
 
                # store the value of "main"
                # key in variable y
                y = x["main"]
 
                # store the value corresponding
                # to the "temp" key of y
                current_temperature = y["temp"]
 
                # store the value corresponding
                # to the "pressure" key of y
                current_pressure = y["pressure"]
 
                # store the value corresponding
                # to the "humidity" key of y
                current_humidity = y["humidity"]
 
                # store the value of "weather"
                # key in variable z
                z = x["weather"]
 
                # store the value corresponding
                # to the "description" key at
                # the 0th index of z
                weather_description = z[0]["description"]
                print (" ")
                print ("****************************************** Weather API *******************************************")
               
            else:
                print(" LONG and LAT Not Found ")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            json_body = [
            {
                "measurement": "Table105_Nodev105",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v105",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam105)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam105)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam105)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam105)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam105)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam105)" : current_humidity,
                    "Current_Weather (Vietnam105)" : weather_description,
            
                    #"RSSI": my_RSSI_Node1                               # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"RSSI": my_RSSI_Node2                               # Node 2  - @@@@@@@@@@@@@@@@@@@@
            
                }
            }
            ]    
    
            # Send data to InfluxDB server ************************** 
            InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
            #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
            InfluxDB_client.write_points(json_body)

            print("Data from Node 105: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### End
        
     # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E 9_2