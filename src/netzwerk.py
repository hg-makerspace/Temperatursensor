import time
import network
import machine
from umqtt.simple import MQTTClient
import ujson
import ubinascii


class Netzwerk:
    # wifi
    ap_if = network.WLAN(network.AP_IF)
    sta_if = network.WLAN(network.STA_IF)

    # mqtt
    client_id = ubinascii.hexlify(sta_if.config('mac'))[-6:].decode()

    # defaults
    mqtt_clientid = "iot_hg_%s" % client_id
    mqtt_topic = 'iot_hg/json'
    LED = machine.Pin(2, machine.Pin.OUT)

    def __init__(self,
                 ssid,
                 wifi_password,
                 mqtt_server=None,
                 mqtt_client_id=mqtt_clientid,
                 mqtt_topic=mqtt_topic,
                 wifi_ap_password="dasisteinlangespasswortohnekomma"
                 ):
        self.ssid = ssid
        self.wifi_password = wifi_password
        self.mqtt_server = mqtt_server
        self.mqtt_client_id = mqtt_client_id
        self.mqtt_topic = mqtt_topic
        # set dummy password for ap mode
        # self.ap_if.config(password=wifi_ap_password)

        # use client mode
        self.ap_if.active(False)
        self.sta_if.active(True)

        # create mqtt object
        if mqtt_server is not None:
            self.mqtt = MQTTClient(self.mqtt_client_id, self.mqtt_server)

    def wifi_disconnect(self):
        try:
            self.sta_if.disconnect()
            time.sleep(0.5)
        except:
            pass

    def wifi_connect(self, retries=2, max_time=10, indicate=True):
        if self.sta_if.isconnected():
            return True

        for i in range(retries):
            t_start = time.time()
            self.sta_if.connect(self.ssid, self.wifi_password)

            while not self.sta_if.isconnected():
                if indicate:
                    self.LED.value(0)  # 0 - is enable for LED
                    time.sleep(0.2)
                    self.LED.value(1)
                time.sleep(0.2)

                t = time.time() - t_start
                if t >= max_time:
                    break

            if self.sta_if.isconnected():
                return True
            else:
                return False

    def wifi_status(self):
        status = self.sta_if.status()
        if status == network.STAT_NO_AP_FOUND:
            return "eAP"
        elif status == network.STAT_WRONG_PASSWORD:
            return "ePW"
        elif status == network.STAT_IDLE:
            return "xID"
        elif status == network.STAT_CONNECTING:
            return "xCO"
        elif status == network.STAT_CONNECT_FAIL:
            return "err"
        elif status == network.STAT_GOT_IP:
            return "ok"

    def mqtt_connect(self, retries=3):
        # check wifi
        if not self.wifi_connect(retries=1, max_time=7):
            return False

        mqtt_connected = False
        for i in range(0, retries):
            try:
                self.mqtt.connect()
            except OSError:
                time.sleep(1)
                continue
            else:
                mqtt_connected = True
                break
        return mqtt_connected

    def mqtt_send(self, data, topic=mqtt_topic):
        payload = ujson.dumps(data)
        retries = 2
        while retries > 0:
            try:
                self.mqtt.publish(topic, payload)
            except (AttributeError, OSError):
                self.mqtt_connect(retries=1)
            else:
                retries = 0
            retries -= 1

    def output(self, text, x_pos=0, y_pos=0):
        print(text)

    def wifi_start(self):
        self.output('wifi', 0, 20)
        is_connected = self.wifi_connect()
        if is_connected:
            self.output('ok', 50, 20)
        else:
            self.output('err', 42, 20)
            print("wifi error")

    def mqtt_start(self):
        self.output("mqtt", 0, 30)
        if self.mqtt_connect(3):
            self.output("ok", 50, 30)
        else:
            self.output("err", 42, 30)
            print("mqtt error")
        time.sleep(0.5)


if __name__ == "__main__":
    netzwerk = Netzwerk(ssid="my_wifi_name",
                        wifi_password="my_wifi_password",
                        mqtt_server="mqtt_server_fqdn",
                        mqtt_client_id="iot-42")
    netzwerk.wifi_connect()
    netzwerk.mqtt_connect()
    netzwerk.mqtt_send(topic='sensors/json',
                       data={'testvalue': 42})
