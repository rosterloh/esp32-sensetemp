import time
import network
import ujson as json
import tempio
import timer

from machine import Pin, Timer
from display_web import DisplayWeb
from webserver import Webserver

display_web = DisplayWeb()
display = display_web

webserver = Webserver(display_web)

settings = json.load(open("settings.json", 'r'))
temp_io = tempio.TempIO(settings)

led = Pin(5, Pin.OUT)
oldvalue = True

def check_wifi(wifi):
    if 'wifi-station' not in settings:
        return

    if wifi.isconnected():
        led.value(0)
        return

    global oldvalue
    led.value(oldvalue)
    oldvalue = not oldvalue

    wifi.connect(settings['wifi-station']['name'], settings['wifi-station']['pass'])

    while not wifi.isconnected():
        time.sleep(0.2)

def wait_ap(wifi):
    if wifi.active() and wifi.isconnected():
        print("AP Already Started")
        return

    while not wifi.active() and not wifi.isconnected():
        print('***')
        time.sleep(0.2)

    print("AP Now Started")

## Setup WIFI Networking as a client
if 'wifi-station' in settings:
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    check_wifi(nic)

## Setup WIFI Networking as an access point
if 'wifi-ap' in settings:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=settings['wifi-ap']['name'])
    wait_ap(ap)

if 'mqtt' in settings:
    import mqtt
    c = mqtt.MQTTClient(settings['device']['name'], settings['mqtt']['ip'], 1883)
    c.connect()

#last_ip = ""
slow_check_timestamp = timer.timestamp

# main loop
def loop(sched=None):
    global slow_check_timestamp

    timer.update()

    ### read and update temperatures
    if temp_io.ready():

        t = temp_io.read()

        if t:
            scale_cat.measurement(c)

        check_wifi(nic)

    #stuff that doesnt have to be done every loop
    if timer.diff(timer.timestamp, slow_check_timestamp) > 1000:
        display.refresh()
        slow_check_timestamp = timer.timestamp

        ### display IP
#        if wlan.isconnected():
#            ip = wlan.ifconfig()[0]
#            global last_ip
#            if last_ip != ip:
#                print(ip)
#                display.msg(ip)
#                last_ip = ip

        #c.publish(settings['device']['name'], json.dumps(poll_sensors()))
        #time.sleep(settings['mqtt']['sleep'])

def start():
    if not settings['device']['loop_async']:
        while True:
            loop()
    else:
        tim = Timer(-1)
        tim.init(period=10, mode=Timer.PERIODIC, callback=loop)

    #start webinterface
    try:
        webserver.run()
    except KeyboardInterrupt:
        tim.deinit()
        raise
