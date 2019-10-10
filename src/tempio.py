from machine import Pin, SPI
import adafruit_max31865 as max31865

RTD_NOMINAL = 1000.0  ## Resistance of RTD at 0C
RTD_REFERENCE = 4300.0  ## Value of reference resistor on PCB

class TempIO():
    """deals with reading raw temperature input from MAX31865 modules"""
    def __init__(self, settings):
        ## Create Software SPI controller.  MAX31865 requires polarity of 0 and phase of 1.
        ## Currently, the micropython on the ESP32 does not support hardware SPI
        sck = Pin(5, Pin.OUT)
        mosi = Pin(18, Pin.IN)
        miso = Pin(19, Pin.OUT)
        spi = SPI(baudrate=50000, sck=sck, mosi=mosi, miso=miso, polarity=0, phase=1)

        ## Create SPI Chip Select pins
        cs1 = Pin(33, Pin.OUT, value=1)
        cs2 = Pin(15, Pin.OUT, value=1)
        cs3 = Pin(32, Pin.OUT, value=1)
        cs4 = Pin(14, Pin.OUT, value=1)
        css = [cs1, cs2, cs3, cs4]

        self.sensors = []
        self.sensor_info = []
        idx = 0

        ## Create array of active RTD sensors and information about them
        for name in settings['device']['sensors']:
            idx += 1

            if name.upper() == "DISABLE":
                continue

            self.sensors.append([
                idx,
                max31865.MAX31865(
                    spi, css[idx-1],
                    wires=4,
                    rtd_nominal=RTD_NOMINAL,
                    ref_resistor=RTD_REFERENCE)
            ])

            self.sensor_info.append({
                "id"       : idx,
                "scale"    : settings['device']['scale'],
                "type"     : "temperature",
                "sensor"   : "RTD1000 -> MAX31865",
                "name"     : name
            })

        self.scale = settings['device']['scale']
        self.to_int = settings['device']['to_int']

    def mean(self, data):
        return sum(data)/float(len(data))

    def _ss(self, data):
        c = self.mean(data)
        ss = sum((x-c)**2 for x in data)
        return ss

    def stddev(self, data, ddof=0):
        ss = self._ss(data)
        pvar = ss/(len(data)-ddof)
        return pvar**0.5

    def poll_sensors(self, extra_info=False):
        meta = []
        samples = []

        for idx, sensor in self.sensors:
            value = sensor.temperature*self.scale

            if self.to_int:
                value = int(value)

            data = {'id':idx, 'value':value}

            if extra_info:
                data['name'] = self.sensor_info[idx-1]['name']

            meta.append(data)
            samples.append(value)

        meta.append({
            'id': 'agg', 
            'mean': self.mean(samples),
            'stddev': self.stddev(samples)
        })
        return meta
