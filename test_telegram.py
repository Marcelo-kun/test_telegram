from config import * # importamos aqui el token#
import telebot #para manejar la API de Telegram#
from flask import Flask, request #para crear el servidor web "seria local este"
from pyngrok import ngrok, conf #para crear un tunel entre nuestro servidor web local e internet (URL publica)
import time
from waitress import serve #para ejecutar el servidor en un entorno de produccion 

#instanciamos el bot de Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)
#instanciar servidor web de Flask
web_server = Flask(__name__)

#gestiona las peticiones POST enviadas al servidor web
@web_server.route('/', methods=['POST'])
def webhook():
	# si el POST recibido es un JSON
	if request.headers.get("content-type") == "application/json":
		update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
		bot.process_new_updates([update])
		return "OK", 200

#responde al comando /start
@bot.message_handler(commands=["start"])
def cmd_start(message):
	"""Da la bienvenida al usuario del bot"""
	bot.send_message(message.chat.id, "Hola! ¿Que tal?", parse_mode="html")
	#print(message.chat.id)
	
# responde a los mensajes de texto que no son comandos
#text basicamente se trata de todo tipo de contenido tales como text,audio,
#document, photo, sticker, video, video_note, voice, location, conatct, new_chat_members, 
#left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo, group_chat_created,
#supergroup_chat_created, channel_chat_created, migrate_to_chat_id,
#migrate_from_chat_id, pinned_message
@bot.message_handler(content_types=['text'])
#definimos a la funcion que esta decorando esto
def bot_texto(message):
	"""Gestiona los mensajes de textos recibidos"""
	#if message.text.startswith("/"):
	bot.send_message(message.chat.id, message.text, parse_mode="html")
	
	

# MAIN ################################
if __name__ == '__main__' :
	print('Iniciando el bot')
	conf.get_default().config_path = "./config_ngrok.yml"
	#configuramos la region del servidor de ngrok
	#REGIONES DISPONIBLES
	# us - Unites States (Ohio)
	# eu - Europe (Frankfurt)
	# ap - Asia/Pasific (Singapore)
	# au - Australia (Sydney)
	# sa - South America (Sao Paulo)
	# jp - Japan (Tokyo)
	# in - India (Mumbai)
	conf.get_default().region = "sa"
	#creamos el archivo de credenciales de la API de ngrok
	ngrok.set_auth_token(NGROK_TOKEN)
	#creamos un tunel https en el puerto 5000
	ngrok_tunel = ngrok.connect(5000, bind_tls=True)
	#url del tunel https creado
	ngrok_url = ngrok_tunel.public_url
	print("URL NGROK:", ngrok_url)
	# eliminamos el webhook
	bot.remove_webhook()
	# pequeña pausa para que se elimine el webhook
	time.sleep(1)
	# definimos el webhook
	bot.set_webhook(url=ngrok_url)
	# arrancamos el servidor
	serve(web_server, host="0.0.0.0", port=5000)
	
	
	
	
	
	
	