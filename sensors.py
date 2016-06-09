import time, logging
import RPi.GPIO as GPIO
import Adafruit_DHT

class Sensors:

    def __init__(self, snd_pin, pir_pin, dht_pin, dht_sensor, sound_event, motion_event,bouncetime=60000):
        self.active_sound_detector = False
        self.active_motion_detector = False
        self.sound_event = sound_event
        self.motion_event = motion_event
        self.snd_pin = snd_pin
        self.pir_pin = pir_pin
        self.dht_pin = dht_pin
        self.dht_sensor = dht_sensor
        self.bouncetime = bouncetime
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pir_pin, GPIO.IN)
        GPIO.setup(snd_pin, GPIO.IN)

    def __del__(self):
        GPIO.cleanup()

    def update_bouncetime(self, bouncetime):
        self.bouncetime = bouncetime
        self.detect_all(False) 
        self.detect_all(True)

    def detect_all(self, active):
        self.detect_sound(active)
        self.detect_motion(active)

    def detect_sound(self, active=True):
        logging.info("Detecting sound: "+str(active))
        if active and not self.active_sound_detector:
            print "detect" + str(self.bouncetime)
            GPIO.add_event_detect(self.snd_pin, GPIO.FALLING, callback=self.sound_callback, bouncetime=self.bouncetime)
            self.active_sound_detector = True
        elif not active and self.active_sound_detector:
            GPIO.remove_event_detect(self.snd_pin)
            self.active_sound_detector=False
        return self.active_sound_detector;

    def detect_motion(self, active=True):
        logging.info("Detecting motion: "+str(active))
        if active and not self.active_motion_detector:
            GPIO.add_event_detect(self.pir_pin, GPIO.RISING, callback=self.motion_callback, bouncetime=self.bouncetime)
            self.active_motion_detector=True
        elif not active and self.active_motion_detector:
            GPIO.remove_event_detect(self.pir_pin)
            self.active_motion_detector=False
        return self.active_motion_detector

    def motion_callback(self, channel):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info('Time = {} Motion Detected!\n'.format(now))
        if hasattr(self, 'motion_event'):
            self.motion_event()

    def sound_callback(self, channel):
    	now = time.strftime("%Y-%m-%d %H:%M:%S")
    	logging.info('Time = {} Sound Detected!\n'.format(now))
        if hasattr(self, 'sound_event'):
            self.sound_event()

    def get_humidity_temp(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.dht_sensor, self.dht_pin)
        return humidity, temperature
