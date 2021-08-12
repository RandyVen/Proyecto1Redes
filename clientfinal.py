from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
from sleekxmpp.plugins.xep_0096 import stanza, File
from sleekxmpp.exceptions import IqError, IqTimeout
#slixmpp no me conecta por alguna razon :(
import logging
import threading #para concurrencia
from prettytable import PrettyTable
import base64 # para envio de archivos
from datetime import datetime
import time


class Register(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.registerAccount)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0045') # Mulit-User Chat (MUC)
        self.register_plugin('xep_0096') # File transfer

    #Metodo inicial
    def start(self, event):
        self.send_presence()
        self.get_roster()
        self.disconnect()

    #Metodo el cual registra al usuario por medio de stanza Iq
    def registerAccount(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            resp.send(now=True)
            print("Usuario creado  - %s!" % self.boundjid)
            log = logging.getLogger("my-logger")
            log.info("Usuario creado  - %s!" % self.boundjid)
        except IqError as e:
            print("No se pudo realizar el registro: %s" % e.iq['error']['text'])
            log.error("No se pudo realizar el registro: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No hay respuesta del servidor.")
            log.error("No hay respuesta del servidor.")
            self.disconnect()

# Clase de cliente la cual tiene todos los metodos cuando el usuario esta logueado
class Client(ClientXMPP):
    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.auto_authorize = True     #Para autorizacion automatica de solicitudes
        self.auto_subscribe = True     #Para suscripcion automatica de solitides [both]
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('message', self.message)
        self.add_event_handler('presence_subscribe',self.new_user_suscribed)
        self.add_event_handler("groupchat_message", self.group_mention)

        # Para concurrencia al momento de consultar al servidor todos los usuarios
        self.received = set()
        self.presences_received = threading.Event()


        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data forms
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # Multi-User Chat (MUC)
        self.register_plugin('xep_0096') # File transfer

        self.nick = ""

    # Metodo de inicio para envio de presencia de conexion y obtener el roster
    def start(self, event):
        try:
            log = logging.getLogger("my-logger")
            self.send_presence(pshow='chat',pstatus='como estas')
            self.get_roster()
        except IqError as e:
            print("No se pudo loguear: %s" % e.iq['error']['text'])
            log.error("No se pudo logear: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            print("No hay respuesta del server.")
            log.error("No hay respuesta del server .")
            self.disconnect()
    
    # Metodo para cerrar sesion
    def logout(self):
        print("Desconectado")
        self.disconnect(wait=True)

    # Metodo para event handler en tal caso que mi nombre de usuario fue escrito en algun room
    def group_mention(self, msg):
        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            user = str(msg['from'])
            index = user.find('@conference')
            print('\n')
            print("<< NOTIFICATION >>")
            print(user[:index]+': han mencionado tu nickname en el grupo y fue => '+msg['mucnick']+'\n')
            print('Ve y revisa que han dicho de ti \n')
            print("<< >>")
            print('\n')

    # Metodo para event handler que avisa si algun usuario se ha suscrito a mi
    def new_user_suscribed(self,presence):
        print('\n')
        print("<< NOTIFICATION >>")
        print(str(presence['from'])+' te ha agregado! ')
        print("<< >>")
        print('\n')

    # Metodo para event handler que recibe los mensajes, y muestra notificacion dependiendo del tipo
    # Puede ser chat o groupchat o un archivo
    def message(self,msg):
        if str(msg['type']) == 'chat':
            if str(msg['subject']) == 'send_file' or len(msg['body']) > 500: #If para validar si esta entrando un archivo
                print("** Te han enviado un archivo **")
                img_body = msg['body']
                file_ = img_body.encode('utf-8')
                file_ = base64.decodebytes(file_)
                with open("xmpp_"+str(int(time.time()))+".png","wb") as f:
                    f.write(file_)
            else: #Sino es un mensaje normal
                print("** Mensaje de "+str(msg['from'])+" **")
                print(str(msg['body']))
                print("** **")
        elif str(msg['type']) == 'groupchat': #En caso que sea un mensaje grupal
            print("** mensaje grupal **")
            print('\n  (%(from)s): %(body)s' %(msg))
            print("** **")
    # Para enviar un mensaje grupal a un room especifico
    def messageRoom(self,room,msg):
        try:
            self.send_message(mto=room+'@conference.alumchat.xyz',mbody=msg, mtype='groupchat')
            print("Mensaje enviado a: "+room)
        except IqError:
            print("No response from server.")

    # Para unirse a un room
    def joinRoom(self, room, nick):
        status = "Hello :D"
        print("Te vas a unir al room ")
        self.plugin['xep_0045'].joinMUC(room+'@conference.alumchat.xyz', nick, pstatus=status, pfrom=self.boundjid.full, wait=True)
        self.nick = nick

    # Para crear y unirse a un room
    # Diferencia con joinRoom es la afiliacion para ser administrador y desbloquear el room para que cualquier usuario pueda ingresar
    def createRoom(self, room, nick):
        status = "Hello"
        print("Te vas a unir al room ")
        self.plugin['xep_0045'].joinMUC(room+'@conference.alumchat.xyz', nick, pstatus=status, pfrom=self.boundjid.full, wait=True)
        self.nick = nick
        # Para afiliacion de adminstrador y desbloquear el grupo
        self.plugin['xep_0045'].setAffiliation(room+'@conference.alumchat.xyz', self.boundjid.full, affiliation='owner')
        self.plugin['xep_0045'].configureRoom(room+'@conference.alumchat.xyz',ifrom=self.boundjid.full)

    # Cambiar el status e ingresar mensaje
    def changeStatus(self, show, status):
        show_text = ""
        if(show == 1):
            show_text = "chat"
        elif(show == 2):
            show_text = "away"
        elif(show == 3):
            show_text = "xa"
        elif(show == 4):
            show_text = "dnd"

        self.send_presence(pshow=show_text, pstatus=status)

    # Para suscribirte a un usuario
    def saveUser(self,jid):
        self.send_presence_subscription(pto=jid)

    # Para enviar un mensaje de tipo chat a un usuario en especifico
    def sendMessage(self,jid,message):
        try:
            self.send_message(mto=jid+'@alumchat.xyz',mbody=message, mfrom=self.boundjid.user, mtype='chat')
            print("Mensaje enviado a: "+jid)
        except IqError:
            print("No response from server.")