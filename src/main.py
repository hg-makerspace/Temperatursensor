import gc
import time
import netzwerk
import oled
import sensor
import conf
import sys
from machine import Pin


def start_test():
    anzeige.prints('start..', clear=True)
    time.sleep(1)

    # test dht
    anzeige.prints("temp", 0, 10)
    if sensor.connected is False:
        anzeige.prints('err', 42, 10)
    else:
        anzeige.prints('ok', 50, 10)

    # start and test wifi
    anzeige.prints('wifi', 0, 20)
    if not config['use_network']:
        anzeige.prints('--', 50, 20)
        time.sleep(1)
        anzeige.clear()
        return
    internet.wifi_disconnect()
    if internet.wifi_connect():
        anzeige.prints('ok', 50, 20)
        # start mqtt
        anzeige.prints("mqtt", 0, 30)
        if internet.mqtt_connect(3):
            anzeige.prints("ok", 50, 30)
        else:
            anzeige.prints("err", 42, 30)
    else:
        status = internet.wifi_status()
        anzeige.prints(str(status), 42, 20)
    time.sleep(1)
    anzeige.clear()


def messen():
    (temperatur, feuchtigkeit, druck) = sensor.read()
    print(temperatur, feuchtigkeit, druck)
    if temperatur is not None:
        str_temp = str(temperatur)
    else:
        str_temp = "--"
    if str_temp != anzeige.lastoutput_text:
        anzeige.print(str_temp, x_pos='center', y_pos='center', clear_last=True)
    return temperatur, feuchtigkeit, druck


def senden(temperatur, feuchtigkeit, druck):
    if temperatur is not None:
        internet.mqtt_send(
            {'tags': {"group": "iot_ag",
                        "client_id": internet.mqtt_client_id
                        },
             'fields': {'temperatur': str(temperatur),
                        'luftfeuchtigkeit': str(feuchtigkeit),
                        'druck': str(druck)
                        }
             }
        )


gc.collect()
# print(gc.mem_free())

led = Pin(2, Pin.OUT)
anzeige = oled.Anzeige()
sensor = sensor.Temperatursensor(use_bme=True)

# load configuration from file
config = conf.loadconfig()
if config is None:
    anzeige.prints('config', clear=True)
    sys.exit()

# do we want to connect to the internet?
if config['use_network']:
    internet = netzwerk.Netzwerk(ssid=config['wlan_name'],
                                 wifi_password=config['wlan_passwort'],
                                 mqtt_server=config['mqtt_server'],
                                 mqtt_topic=config['mqtt_topic']
                                 )
gc.collect()
start_test()
while True:
    led.on()
    (temp, feuchte, druck) = messen()
    if config['use_network']:
        senden(temp, feuchte, druck)
    led.off()
    time.sleep(1)
