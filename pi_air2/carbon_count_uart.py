import time
import board
import datetime
import configparser

from influxdb import InfluxDBClient
import adafruit_dht
import UART

class Measurement:
    def __init__(self, session, runNo, location, device, time, ppm, temp, hum):
        self.measurement = session
        self.tags  = {'run': runNo, 'device': device, 'location':location}
        self.time = time
        self.fields = {'ppm': ppm, 'temp': temp, 'hum': hum}

class Sensor:
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
    def __init__(self, sensor):
        self.sensor = sensor
        self.hum = 0
        self.temp = 0
        
    def measure(self):
        self.hum = self.validate(self.hum, self.sensor.humidity)
        self.temp = self.validate(self.temp, self.sensor.temperature)
    
class Co2(Sensor):
    def __init__(self, sensor):
        self.sensor = sensor
        self.ppm = 0
        
    def measure(self):
        self.ppm = self.validate(self.ppm, self.sensor.read())

    

def main():
    print("Start PI-Air measurment")
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Initialize sensors
    cO2Sensor = Co2(UART.CO2())
    dhtSensor = Dht(adafruit_dht.DHT22(board.D24))
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
                dhtSensor.measure()
                cO2Sensor.measure()
                measurement = Measurement(session, runNo, location, device, iso, cO2Sensor.ppm, dhtSensor.temp, dhtSensor.hum)
                client.write_points([vars(measurement)])
            except Exception as ex:
                print(ex.args[0])

            time.sleep(int(config['Global']['MeasureInterval']))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
