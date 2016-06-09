import threading, logging, time
from wakeonlan import wol
from mpd import MPDClient
import pprint
import rrdtool
import remote # samsung remote
from subprocess import call

class BotHelper:
    def __init__(self, sensors, rrd, log_path,mpd_event,mpd_host='localhost',mpd_port='6600'):
        self.sensors = sensors
        self.worker_thread_mpd = None
        self.running_thread = False
        self.started = False
        self.rrd = rrd
        self.mpd_event = mpd_event
        self.mpd_client = MPDClient()               # create client object
        self.mpd_client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self.mpd_client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
        self.mpd_client.connect(mpd_host, mpd_port)  # connect to localhost:6600

        # logging config
        logging.basicConfig(level=logging.ERROR)
        pp = pprint.PrettyPrinter(indent=4)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        logger = logging.getLogger('')
        logger.setLevel(logging.INFO)

        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.info("Init")


    def get_mpd_state(self):
        #return self.mpd_client.status()
        pass

    def mpd_worker(self):
        self.running_thread = True
        logging.info("===Starting thread for mpd status listener===")
        while self.running_thread:
            self.mpd_client.idle()
            logging.info("===Waiting thread mpd status===")
            status = self.mpd_client.status()
            logging.info("===Status event in thread mpd===")
            state = status['state']
            logging.info("Music change state: "+str(state))
            result = self.sensors.detect_sound(state!='play')
            if hasattr(self,'mpd_event'):
                self.mpd_event(result);
        logging.info("===Ending thread for mpd status listener===\n")

    def run(self):
        if not self.started:
            self.sensors.detect_all(True)
            self.worker_thread_mpd = threading.Thread(target=self.mpd_worker)
            self.worker_thread_mpd.start()
            self.started = True
            return True;
        else:
            return False;

    def stop(self):
        if self.started:
            self.sensors.detect_all(False)
            self.running_thread = False # signal thread end and wait for it
            self.mpd_client._write_command("noidle") # https://github.com/Mic92/python-mpd2/pull/26 instead of self.mpd_client.noidle()
            time.sleep(1)
            self.worker_thread_mpd.join()
            self.started = False
            return True
        else:
            return False

    def get_temp_graph(self):
        rrdtool.graph("./test.png",
                  '--imgformat', 'PNG',
                  '--width', '540',
                  '--height', '100',
                  #'--start', "-%i" % YEAR,
                  #'--end', "-1",
                  '--vertical-label', 'Humidity',
                  '--title', 'Temp/Humidity',
                  '--upper-limit', '100',
                  '--lower-limit', '0',
                  '--right-axis', '0.2:10',
                  '--right-axis-label','Temperature',
                  'DEF:temp='+self.rrd['path']+self.rrd['temp_file']+':living_room_temp:AVERAGE',
                  'DEF:humid='+self.rrd['path']+self.rrd['humidity_file']+':humidity:AVERAGE',
                  'CDEF:temp_scale=temp,10,-,5,*',
                  'LINE1:humid#0000ff:Humidity',
                  'LINE1:temp_scale#ff0000:Temperature',)
        photo = open('./test.png', 'rb')
        return photo

    def power_self(self):
        call("sudo poweroff", shell=True)

    def reboot_self(self):
        call("sudo reboot", shell=True)

    def power_samsung_tv(self, tv):
        try:
            myremote = remote.Remote(tv['ip'],tv['mac'],tv['model'])
            myremote.connect(3)
            myremote.sendkey('KEY_POWEROFF')
            myremote.close()
        except:
            pass

    def power_nas(self):
        pass

    def wol(self,mac):
        wol.send_magic_packet(mac)
