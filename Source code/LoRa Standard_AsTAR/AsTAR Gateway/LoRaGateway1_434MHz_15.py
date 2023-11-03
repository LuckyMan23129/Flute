
# Gateway1 (434MHz and for Node 1 to Node 5)

import time
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
import adafruit_rfm9x

#Freq = 433.0
Freq = 434.0
# **************************************** For Adafruit LoRa concentrator and Rasp ********************************* E1


# *****************************************************  For Python  *********************************************** S2
from datetime import datetime
import json
from base64 import b64encode
#import paho.mqtt.client as mqtt
# *****************************************************  For Python  *********************************************** E2


# ************************************************* For INFLUXDB 1.7 *********************************************** S3
# This is program that writing for InfluxDB 1.7   
    # => Reference at:  https://github.com/influxdata/influxdb-python
    
    # For InfluxDB's credentials are offered from Jonathan
from influxdb import InfluxDBClient
my_influxdb_url = '3.123.xxx.xx'            
my_influxdb_port = 6808
my_influxdb_user = 'xxx'
my_influxdb_passs = 'xxxxxxxxx'
my_influxdb_Database = 'xxxxxxx'    # Measurement = table
# ************************************************* For INFLUXDB 1.7 *********************************************** E3

# ********************************** For Weather API ******************************************************** S1
# https://medium.com/@joseph.magiya/weather-data-and-forecasts-from-open-weather-api-1636691d5ba

import requests
# import json
 
# Enter your API key here
api_key = "0fb1c49b9f013892b4e1f992d57xxxxx"    # Vu - https://home.openweathermap.org/api_keys
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
    print('RFM9x detected')
except RuntimeError:
    print('RFM9x error')


# Wait for LoRa packets
while True:
    packet = None
    try:
        packet = rfm9x.receive(timeout=0.9)
        print("Vu -  Length of bytearray:", len(packet))
    except:
        packet = None
    if packet != None:
        try:
            print("Received:",  str(packet))  
            # Split packet
            from_addr = packet[0]
            to_addr = packet[1]
    
            Water = int.from_bytes(packet[2:4], byteorder='little') / 10.0
            SuperCap = int.from_bytes(packet[4:6], byteorder='little') / 1000.0
            Rate = int.from_bytes(packet[6:8], byteorder='little') 
            SleepTime = int.from_bytes(packet[6:8], byteorder='little')
        except:
            print("The length of receiving bytes is not enough!")
        # Printing out to see Which Node send data to Gateway
        if (((from_addr == 1) or (from_addr == 2) or (from_addr == 3) or (from_addr == 4) or (from_addr == 5)) and (to_addr == 0)):
            # Print results
            print("From:", from_addr)       # "from_addr" la dia chi cua node ma send den
            print("To:", to_addr)           # "to_addr" La dia chi Gateway nhan TN
        
      # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ S 9_2
            ####################################  Send Node 1's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 1)  and (to_addr == 0)):
            try:
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
            except:
                print("Vu - Cannot read weather API")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7

            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
            json_body = [
            {
                "measurement": "Table1_Nodev1",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v1",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam1)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam1)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam1)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam1)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam1)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam1)" : current_humidity,
                    "Current_Weather (Vietnam1)" : weather_description,
            
                }
            }
            ]    

          
            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            try:
                InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
                #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
                InfluxDB_client.write_points(json_body)
            except:
                print("Vu - Failed sending data to InfluxDB") 
            print("Data from Node 1: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 1's Data to InfluxDB cloud V1.7 ##################################### End



        ####################################  Send Node 2's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 2)  and (to_addr == 0)):
            try:
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
            except:
                print("Vu - Cannot read weather API")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
        
            json_body = [
            {
                "measurement": "Table2_Nodev2",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v2",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam2)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam2)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam2)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam2)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam2)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam2)" : current_humidity,
                    "Current_Weather (Vietnam2)" : weather_description,
            
                }
            }
            ]    

            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            try:
                InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
                #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
                InfluxDB_client.write_points(json_body)
            except:
                print("Vu - Failed sending data to InfluxDB") 
            print("Data from Node 2: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 2's Data to InfluxDB cloud V1.7 ##################################### End


        ####################################  Send Node 3's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 3)  and (to_addr == 0)):
            try:
                # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
                # https://medium.com/@joseph.magiya/weather-data-and-forecasts-from-open-weather-api-1636691d5ba

                json_data = requests.get(current_coord_weather_url).json()

                x = json_data
                # Now x contains list of nested dictionaries
                # Check the value of "cod" key is equal to
                # "404", means city is found otherwise,
                # city is not found
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
            except:
                print("Vu - Cannot read weather API")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
            json_body = [
            {
                "measurement": "Table3_Nodev3",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v3",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam3)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam3)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam3)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam3)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam3)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam3)" : current_humidity,
                    "Current_Weather (Vietnam3)" : weather_description,
            
                    #"RSSI": my_RSSI_Node1                               # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"RSSI": my_RSSI_Node2                               # Node 2  - @@@@@@@@@@@@@@@@@@@@
            
                }
            }
            ]    


            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            try:
                InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
                #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
                InfluxDB_client.write_points(json_body)
            except:
                print("Vu - Failed sending data to InfluxDB") 
            print("Data from Node 3: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 3's Data to InfluxDB cloud V1.7 ##################################### End


            ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 4)  and (to_addr == 0)):
            try:
                # ****************************************** Using API to read "WEATHER DATA" ********************************** S7
                # https://medium.com/@joseph.magiya/weather-data-and-forecasts-from-open-weather-api-1636691d5ba

                json_data = requests.get(current_coord_weather_url).json()

                x = json_data
                # Now x contains list of nested dictionaries
                # Check the value of "cod" key is equal to
                # "404", means city is found otherwise,
                # city is not found
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
            except:
                print("Vu - Cannot read weather API")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
            json_body = [
            {
                "measurement": "Table4_Nodev4",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v4",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam4)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam4)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam4)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam4)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam4)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam4)" : current_humidity,
                    "Current_Weather (Vietnam4)" : weather_description,
            
                    #"RSSI": my_RSSI_Node1                               # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"RSSI": my_RSSI_Node2                               # Node 2  - @@@@@@@@@@@@@@@@@@@@
            
                }
            }
            ]    


            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            try:
                InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
                #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
                InfluxDB_client.write_points(json_body)
            except:
                print("Vu - Failed sending data to InfluxDB") 
            print("Data from Node 4: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
        ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### End
        
        
        ####################################  Send Node 5's Data to InfluxDB cloud V1.7 ##################################### Start
        if ((from_addr == 5) and (to_addr == 0)):
            try:
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
            except:
                print("Vu - Cannot read weather API")
            print ("*******************************************************************************************************")
            # **************************************************** Using API to read "WEATHER DATA" ********************************** E7


            # Data that is send to InfluxDB cloud v1.7
            # => Reference at:  https://github.com/influxdata/influxdb-python
            json_body = [
            {
                "measurement": "Table5_Nodev5",      # Node 1 - @@@@@@@@@@@@@@@@@@@@
                #"measurement": "Table2_Nodev2",     # Node 2 - @@@@@@@@@@@@@@@@@@@@
                "tags": {
                    "Node": "Node v5",                   # Node 1 - @@@@@@@@@@@@@@@@@@@@
                    #"Node": "Node v2",                  # Node 2 - @@@@@@@@@@@@@@@@@@@@
                    "region": "BinhDinh - Vietnam"
                },
                "time": datetime.utcnow(),
                "fields": {
            
                    "Water Level (Vietnam5)": Water,                # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"Water Level (Vietnam2)": my_waterlevel_Nodev2,               # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "SuperCap (Vietnam5)": SuperCap + 0.0,          # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"SuperCap (Vietnam2)": my_SuperCaplevel_Nodev2 + 0.0,         # Node 2  - @@@@@@@@@@@@@@@@@@@@
                    "Temperature (Vietnam5)" : Rate + 0.0,          # "Temp" Thuc Ra dang chua gia tri "sleep timer"
                    "Task Rate (Vietnam5)": SleepTime,              # New collumn  to contain the value of "Task Rate"
                    # From Weather API
                    "Temperature_ (Vietnam5)" : current_temperature + 0.0,        # New collumn of "Temperature" => Chua gia tri nhiet do
                    "Humidity (Vietnam5)" : current_humidity,
                    "Current_Weather (Vietnam5)" : weather_description,
            
                    #"RSSI": my_RSSI_Node1                               # Node 1  - @@@@@@@@@@@@@@@@@@@@
                    #"RSSI": my_RSSI_Node2                               # Node 2  - @@@@@@@@@@@@@@@@@@@@
            
                }
            }
            ]    

            # Send data to InfluxDB server ************************** 
                # => Reference at:  https://github.com/influxdata/influxdb-python
            try:
                InfluxDB_client = InfluxDBClient(my_influxdb_url, my_influxdb_port, my_influxdb_user, my_influxdb_passs, my_influxdb_Database)
                #InfluxDB_client.create_database(my_influxdb_Measurement)  # Database is availabel, So we do not need to create
                InfluxDB_client.write_points(json_body)
            except:
                print("Vu - Failed sending data to InfluxDB") 
            print("Data from Node 5: ")
            print("Water_Level:", Water, "Cm")
            print("SuperCapacitor Votage Level:", SuperCap, "V")
            print("Sleep time:", SleepTime, "s")
            print("Temperature:", current_temperature, "oC")
            print()
            
        ####################################  Send Node 4's Data to InfluxDB cloud V1.7 ##################################### End
            
         # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Send Data to influxDb cloud V1.7 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ E 9_2