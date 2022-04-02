import time
import board
import datetime
import configparser
import json

from influxdb import InfluxDBClient
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_dht
import UART

class Measurement:
    def __init__(self, session, runNo, location, device, time):
        self.measurement = session
        self.tags  = {'run': runNo, 'device': device, 'location':location}
        self.time = time
        self.fields = {}

class Sensor():
    def __init__(self, sensor, name):
        self.name = name
        self.sensor = sensor

    def measure(self):
        pass
    def validate(self, refValue, newValue):
        if refValue != 0:
            if type(newValue) != str and newValue < refValue * 2:
                return newValue
            else:
                return refValue
        else:
            return newValue

class Dht(Sensor):

    def __init__(self, sensor, name=''):
        super().__init__(sensor, name)
        self.hum = 0
        self.temp = 0
        
    def measure(self):
        self.hum = self.validate(self.hum, self.sensor.humidity)
        self.temp = self.validate(self.temp, self.sensor.temperature)
        return {self.name+'hum' : self.hum, self.name+'temp' : self.temp}
    
class Co2(Sensor):
    def __init__(self, sensor, name=''):
        super().__init__(sensor, name)
        self.ppm = 0
        
    def measure(self):
        self.ppm = self.validate(self.ppm, self.sensor.read())
        co2 = {self.name+'ppm' : self.ppm}
        return co2


class Bme(Sensor):
    def __init__(self, sensor, name=''):
        super().__init__(sensor, name)
        self.hum = 0
        self.temp = 0
        self.pressure = 0
        
    def measure(self):
        self.hum = self.validate(self.hum, self.sensor.relative_humidity)
        self.temp = self.validate(self.temp, self.sensor.temperature)
        self.pressure = self.validate(self.pressure, self.sensor.pressure)
        return {self.name+'hum' : self.hum, self.name+'temp' : self.temp, self.name+'pressure' : self.pressure}

    

def main():
    print("Start PI-Air measurement")
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Initialize sensors
    cO2Sensor = Co2(UART.CO2())
    dhtSensor = Dht(adafruit_dht.DHT22(eval("board.D"+config['TempSensor']['Gpio'])), 'temp2_')

    i2c = board.I2C()   # uses board.SCL and board.SDA
    bmeSensor = Bme(adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76))
    
    sensors = [cO2Sensor, dhtSensor, bmeSensor]

    # Initialize InfluxDb client
    client = InfluxDBClient(config.get('InfluxDb','Host'), config.get('InfluxDb','Port'), config.get('InfluxDb','User'), config.get('InfluxDb','Password'), config.get('InfluxDb','Dbname'), True, True)

    # Initialize current session
    session = config['InfluxDb']['Session']
    location = config['InfluxDb']['Location']
    device = config['InfluxDb']['Device']

    now = datetime.datetime.now()
    runNo = config.get('InfluxDb','RunPrefix') + now.strftime("%Y%m%d%H%M")

    try:
        while True:

            utc_datetime = datetime.datetime.utcnow()
            iso = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")

            try:
                measurement = Measurement(session, runNo, location, device, iso)
                for sensor in sensors:
                    measurement.fields.update(sensor.measure())
                client.write_points([vars(measurement)])

            except Exception as ex:
                print(ex.args[0])

            time.sleep(int(config['Global']['MeasureInterval']))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
