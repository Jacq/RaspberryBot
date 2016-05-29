#!/usr/bin/python
# -*- coding: utf-8 -*-
import time, os, sys, logging
import commands
import telebot
from telebot import types
from yaml import load

from helpers import BotHelper
from sensors import Sensors

class BotSubscribers:
    def __init__(self,bot,init_subscribers):
        self.subscribers = [] + init_subscribers
        self.bot = bot

    def subscribe(self, m):
        if not m.chat.id in self.subscribers:
            self.subscribers.append(m.chat.id)
            logging.info("Subscribed " + str(m.from_user))
            bot.reply_to(m, "Subscribed")
        else:
            bot.reply_to(m, "Already Subscribed")

    def unsubscribe(self, m):
        if m.chat.id in self.subscribers:
            self.subscribers.remove(m.chat.id)
            logging.info("Unsubscribed " + str(m.from_user))
            bot.reply_to(m, "Unsubscribed")
        else:
    	    bot.reply_to(m, "Not found")

    def motion_event(self):
        self.send_msg_all("Motion Detected")

    def sound_event(self):
        self.send_msg_all("Sound Detected")

    def send_msg_all(self, message):
        if len(self.subscribers) > 0:
            for cid in self.subscribers:
                bot.send_message(cid, message)
                #os.system('./pushbullet.sh '+message)


config = load(open('config.yml'))
admin_cid = config['admin_cid']
bot = telebot.TeleBot(config['bot_token'])

telebot.logger.setLevel(logging.ERROR)
telebot.logger.setLevel(logging.WARNING) # Outputs debug messages to console.
logging.getLogger('urllib3').setLevel(logging.WARNING) #hide urllib3 messages

#############################################
#Funciones
@bot.message_handler(commands=['help','start'])
def command_ayuda(m):
    bot.reply_to(m, "Comandos Disponibles: \n"+help)

@bot.message_handler(commands=['mpdstatus'])
def command_temp(m):
    state = bot_helper.get_mpd_state();
    bot.reply_to(m, str(state))

@bot.message_handler(commands=['temp'])
def command_temp(m):
    humidity, temperature = my_sensors.get_humidity_temp()
    msg = 'Temp = {0:0.0f} *C, Hum = {1:0.0f} %'.format(temperature, humidity)
    bot.reply_to(m, msg)

@bot.message_handler(commands=['tempg'])
def command_temp(m):
    photo = bot_helper.get_temp_graph();
    bot.send_photo(m.chat.id, photo)

@bot.message_handler(commands=['subscribe'])
def command_temp(m):
    subscribers.subscribe(m)

@bot.message_handler(commands=['unsubscribe'])
def command_temp(m):
    subscribers.unsubscribe(m)

@bot.message_handler(commands=['run'])
def command_temp(m):
    success = bot_helper.run()
    if success:
        message = "Bot Started!";
        bot.reply_to(m, message)
        bot.send_message(admin_cid,message)
        logging.info("Started by " + str(m.from_user))
    else:
        bot.reply_to(m, "Already started")

@bot.message_handler(commands=['stop'])
def command_temp(m):
    success = bot_helper.stop()
    if success:
        message = "Bot Stopped!";
        bot.reply_to(m, message)
        bot.send_message(admin_cid,message)
        logging.info("Stopped by " + str(m.from_user))
    else:
        bot.reply_to(m, "Already stopped")

def bounce_time_response_step(msg):
    bounce_time_response(msg,0)

def bounce_time_response(msg ,index):
    try:
       temp = int(msg.text.split()[index])
    except:
       bot.reply_to(msg,"Bouncetime must be integer")

    if temp >= 1 and temp <= 60:
       bouncetime = temp * 1000
       bot_helper.stop()
       bot_helper.run(bouncetime)
       markup = types.ReplyKeyboardHide(selective=False)
       bot.reply_to(msg,"Bouncetime updated at bouncetime "+str(bouncetime)+" ms, restarting", reply_markup=markup)
       bot.send_message(admin_cid,"Motion/Sound detector restarted")
    else:
       bot.reply_to(msg,"Bouncetime must be in range [1,60]")
       bot.register_next_step_handler(m, bounce_time_response_step)

@bot.message_handler(commands=['bouncetime'])
def command_temp(m):
    # time matrix:
    markup = types.ReplyKeyboardMarkup()
    itembtna = types.KeyboardButton('1')
    itembtnb = types.KeyboardButton('2')
    itembtnc = types.KeyboardButton('5')
    itembtnd = types.KeyboardButton('10')
    itembtne = types.KeyboardButton('30')
    itembtnf = types.KeyboardButton('60')
    markup.row(itembtna, itembtnb, itembtnc)
    markup.row(itembtnd, itembtne, itembtnf)
    bot.reply_to(m, "Choose time in seconds:", reply_markup=markup)
    bot.register_next_step_handler(m, bounce_time_response_step)

@bot.message_handler(commands=['bouncetimeraw'])
def command_temp(m):
    bounce_time_response(m,1)

@bot.message_handler(commands=['off'])
def command_temp(m):
    if m.from_user.id == admin_cid:
        bot.reply_to(m, "Powering off")
        logging.info("Power off by " + str(m.from_user))
        bot_helper.power_self();
    else:
        bot.reply_to(m, "Only admin can power off")

@bot.message_handler(commands=['offall'])
def command_temp(m):
    if m.from_user.id == admin_cid:
        bot.reply_to(m, "Powering off all")
        logging.info("Power off by " + str(m.from_user))
        bot.reply_to(m, "Powering off TV")
        bot_helper.power_samsung_tv(config['tv'])
        bot.reply_to(m, "Powering off NAS")
        bot_helper.power_nas()
        bot.reply_to(m, "Power off myself")
        #bot_helper.power_self();
    else:
        bot.reply_to(m, "Only admin can power off")

@bot.message_handler(commands=['reboot'])
def command_temp(m):
    if m.from_user.id == admin_cid:
        bot.reply_to(m, "Rebooting")
        logging.info("Reboot by " + str(m.from_user))
        bot_helper.reboot_self();
    else:
        bot.reply_to(m, "Only admin can reboot")

@bot.message_handler(commands=['woln'])
def command_temp(m):
    if m.from_user.id == admin_cid:
        bot.reply_to(m, "Waking NAS")
        logging.info("Wol NAS by " + str(m.from_user))
        bot_helper.wol(config['nas']['mac'])
    else:
        bot.reply_to(m, "Only admin can WOLn")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_all(message):
    try:
        is_number = int(message.text)
    except Exception as e:
        bot.reply_to(message, help)

def mpd_event(result):
    bot.send_message(admin_cid,"Sound detector state: "+str(result))

subscribers = BotSubscribers(bot,[admin_cid])
my_sensors = Sensors(config['snd']['pin'],config['pir']['pin'],config['dht']['pin'],config['dht']['sensor'], subscribers.sound_event, subscribers.motion_event)
bot_helper = BotHelper(my_sensors, config['rrd'],config['log_path'],mpd_event)

help = """/help
/temp - get temp and humidity
/tempg - get temp and humidity graph
/run - start sampling
/stop - stop sampling
/bouncetime - change bounce time
/subscribe - subscribe to detections
/unsubscribe - unsubscribe from detections
/mpdstatus - mpd status
/woln

/reboot

/off

/offall
"""
logging.info("PIR, Sound, Telegram Bot Starting (CTRL+C to exit)")
time.sleep(2)
logging.info("Ready")

#############################################
#Listener
def listener(messages): # Con esto, estamos definiendo una función llamada 'listener', que recibe como parámetro un dato llamado 'messages'.
    for m in messages: # Por cada dato 'm' en el dato 'messages'
        cid = m.chat.id # Almacenaremos el ID de la conversación.
        if m.content_type == 'text':
            log_msg = "[" + str(cid) + "] " + str(m.from_user) + ": " + m.text
            logging.info(log_msg)
            bot.send_message(admin_cid,log_msg)

bot.set_update_listener(listener) # Así, le decimos al bot que utilice como función escuchadora nuestra función 'listener' declarada arriba.

#############################################
#Peticiones
while 1:
    #try:
        bot_helper.run()
        bot.send_message(admin_cid,"Bot started")
        bot.polling(none_stop=True) # Con esto, le decimos al bot que siga funcionando incluso si encuentra algun fallo.
        '''
        except Exception as e:
        logging.error(e)
        logging.warning("Restarting bot due to error: " + str(e))
        time.sleep(5)
        '''

logging.info("Quit")
