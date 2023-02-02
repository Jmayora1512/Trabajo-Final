#!/usr/bin/python3
#-*-coding:utf8-*-
"""
Carriots.com
Creado 11 Ene 2013
Este programa envía transmisiones a Carriots de acuerdo con los valores leídos por un sensor LDR
Modificado por Jorge Mayora 13 Feb 2018    
"""
import RPi.GPIO as GPIO
import http.client
import urllib.request
import urllib.parse
from time import mktime, sleep
from datetime import datetime
import json
class Client (object):
    api_url = "http://api.carriots.com/streams"
        
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.content_type = "application/json" 
        self.headers = {'User-Agent': 'Raspberry-Carriots',
                        'Content-Type': self.content_type,
                        'Carriots.apikey': self.api_key}
        self.data = None
        self.response = None

    def send(self, data):
        self.data = json.dumps(data).encode('ascii')
        req = urllib.request.Request(Client.api_url, self.data, self.headers)
        self.response = urllib.request.urlopen(req)
        return self.response
def rc_time(pipin):
    measurement = 0
    GPIO.setup(pipin, GPIO.OUT)
    GPIO.output(pipin, GPIO.LOW)
    sleep(0.1)

    GPIO.setup(pipin, GPIO.IN)

    while GPIO.input(pipin) == GPIO.LOW:
        measurement += 1

    return measurement


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(10, GPIO.IN) #Configuracion variable como entrada
    Boton = 1
    
    on = 1  # Constante para indicar que las luces estan encendidas
    off = 2  # Constante para indicar que las luces estan apagadas

    device = "SensorLuz@jmayora.jmayora"  # id_developer de mi dispositivo
    apikey = "4f18e390209cb527dc671acf12f4bc6c770f5c8143c9ec0a3b61d6ffcff15aa0"  # Mi Carriots apikey

    lights = off  # Estado actual

    client_carriots = Client(apikey)

    # La rutina de bucle se repite una y otra vez para siempre
    # Para salir "Ctrl + c"
    while True: #rc_time
        timestamp = int(mktime(datetime.utcnow().timetuple()))
        #timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print (rc_time(3))
        # Este es el limite de valores entre el dia o la noche con el sensor LDR y nuestro condensador.
        # Puede ser necesario ajustar este valor.
        if rc_time(3) > 15000:
            new_lights = off
            print("Lights OFF")
        else:
            new_lights = on
            print("Lights ON")

        if lights is not new_lights:  # Verifique si tenemos un cambio en el estado
            lights = new_lights  # Actualizacion de estado y transmisión de envio
            Boton = (GPIO.input(10))
            data = {"protocol": "v2",
                        "device": device,
                        "at": timestamp,
                        "data": dict( lights=("ON" if new_lights is on else "OFF"),Pressed=("YES" if Boton == 0 else "NO"))}
            carriots_response = client_carriots.send(data)
            print (carriots_response.read())

main()
