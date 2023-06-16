import gc
from machine import Pin, I2C
import time


class Temperatursensor:
    default_dht_pin = 0
    default_scl_pin = 5
    default_sda_pin = 4
    connected = False

    def __init__(self,
                 use_dht=False,
                 dht_pin=default_dht_pin,
                 use_bme=False,
                 i2c_scl=default_scl_pin,
                 i2c_sda=default_sda_pin):
        gc.collect()
        self.use_dht = use_dht
        self.use_bme = use_bme
        self.debug = False
        if use_dht and dht_pin is not None:
            import dht
            # dht setup
            self.DHT = dht.DHT22(Pin(dht_pin, Pin.IN, Pin.PULL_UP))
            try:
                self.DHT.measure()
            except OSError:
                print('dht error')
            else:
                self.connected = True
            self.dht_sample_time = 10
        if use_bme and i2c_scl is not None and i2c_sda is not None:
            # https://github.com/catdog2/mpy_bme280_esp8266
            # maintainer fork: https://github.com/SebastianRoll/mpy_bme280_esp8266
            try:
                import bme280
            except ImportError:
                import extramodules.bme280 as bme280
            # bme setup
            self.i2c = I2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda))
            # wait for bus to get ready
            time.sleep(1)
            try:
                self.bme = bme280.BME280(i2c=self.i2c)
            except OSError:
                print("bme sensor error")
            else:
                print("bme ok")
                self.connected = True
                # wait for sensor to get ready
                # print("wait")
                # time.sleep(5)

    def output(self, text):
        print(text)

    def read_bme(self):
        if not self.connected:
            return None, None, None
        try:
            (temperature, pressure, humidity) = self.bme.read_compensated_data()
        except OSError:
            return None, None, None
        temperature = temperature / 100
        pressure_hpa = pressure / 25600
        humidity_pct = humidity / 1024
        return temperature, humidity_pct, pressure_hpa

    def read_dht(self):
        if not self.connected:
            return None, None, None
        try:
            self.DHT.measure()
        except OSError:
            if self.debug:
                self.output('dhtfail')
            return None, None
        else:
            temp = self.roundedvalue(self.DHT.temperature())
            hum = self.roundedvalue(self.DHT.humidity())
            return temp, hum

    def roundedvalue(self, value):
        if type(value) == float or type(value) == int:
            return round(value, 1)
        else:
            return None

    def read(self):
        if not self.connected:
            return None, None, None
        if self.use_dht:
            (temp, hum) = self.read_dht()
            return self.roundedvalue(temp), self.roundedvalue(hum), None
        elif self.use_bme:
            (temp, hum, press) = self.read_bme()
            return self.roundedvalue(temp), self.roundedvalue(hum), self.roundedvalue(press)


if __name__ == "__main__":
    while True:
        sensor = Temperatursensor(use_bme=True)
        (temperature, humidity, pressure) = sensor.read()
        print(temperature, humidity, pressure)
        time.sleep(2)
