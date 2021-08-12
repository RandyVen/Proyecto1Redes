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
        status = "Activo"
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
            print("No hay respuesta del server.")

     # Metodo para borrar cuenta del servidor
    def unregister(self):
        iq = self.make_iq_set(ito='alumchat.xyz', ifrom=self.boundjid.user)
        item = ET.fromstring("<query xmlns='jabber:iq:register'> \
                                        <remove/> \
                                    </query>")
        iq.append(item)
        res = iq.send()
        if res['type'] == 'result':
            print("Cuenta eliminada")

    # Metodo para enviar un archivo por medio de base64
    def sendFile(self, path, to):
        with open(path,'rb') as img:
            file_ = base64.b64encode(img.read()).decode('utf-8')

        self.send_message(mto=to+'@alumchat.xyz', mbody=file_, msubject='send_file', mtype='chat')

    # Metodo para obtener un usuario en especifico
    def getUser(self, username):
        print("== Contacto a buscar ==")
        print('Esperando...\n')
        proof = False
        self.presences_received.wait(1) #Para evitar problemas de concurrencia
        groups = self.client_roster.groups() #Para obtener los diferentes tipos de grupos del server
        t2 = PrettyTable(['Username','Subscription','Status'])
        for group in groups:
            for jid in groups[group]:
                temp = []
                sub = self.client_roster[jid]['subscription']           
                temp.append(jid)
                temp.append(sub)

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'chat'
                    if pres['show']:
                        show = pres['show']
                    temp.append(show)
                if len(temp) == 2: # Para validar que si no tiene estado de available, se ponga away
                    temp.append('away')
                if str(jid) == username+"@alumchat.xyz": #Valida que sea el usuario solicitado
                    proof = True
                    t2.add_row(temp)
        #Si el usuario esta disponible muestra la tabla, sino muestra mensaje de usuario no encontrado
        if proof:
            print(t2)
        else:
            print("No se encontro al usuario")


    # Metodo para obtener usuarios del server y del roster
    def getUsers(self):
        iq = self.Iq()
        iq['type'] = 'set'
        iq['id'] = 'search_result'
        iq['to'] = 'search.alumchat.xyz'
        #Stanzas de query para obtener usaurios del server
        item = ET.fromstring("<query xmlns='jabber:iq:search'> \
                                <x xmlns='jabber:x:data' type='submit'> \
                                    <field type='hidden' var='FORM_TYPE'> \
                                        <value>jabber:iq:search</value> \
                                    </field> \
                                    <field var='Username'> \
                                        <value>1</value> \
                                    </field> \
                                    <field var='search'> \
                                        <value>*</value> \
                                    </field> \
                                </x> \
                              </query>")
        iq.append(item)
        res = iq.send()
        data = []
        temp = []
        cont = 0
        # PAra rellenar la informacion si hace falta, y appendear en array para mostrar en tabla
        for i in res.findall('.//{jabber:x:data}value'):
            cont += 1
            txt = ''
            if i.text == None:
                txt = '--'
            else:
                txt = i.text

            temp.append(txt)
            if cont == 4:
                cont = 0
                data.append(temp)
                temp = []

        t = PrettyTable(['Email', 'JID', 'Username', 'Name'])
        for i in data:
            t.add_row(i)
        print(t)

        # Muestra lista de contactos del roster
        print("== Lista de Contactos ==")
        print('Esperando...\n')
        self.presences_received.wait(1) #Para la concurrencia
        groups = self.client_roster.groups() #Obtener los diferentes grupos del server
        t2 = PrettyTable(['Username','Subscription','Status'])
        for group in groups:
            for jid in groups[group]:
                temp = []
                sub = self.client_roster[jid]['subscription']           
                temp.append(jid)
                temp.append(sub)

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    temp.append(show)
                if len(temp) == 2:
                    temp.append('unavailable')
                if str(jid) != str(self.boundjid.bare) and str(jid).find('@conference.alumchat.xyz') == -1:
                    t2.add_row(temp)
        print(t2)
            
# Para saber cuantas entradas he recibido de presencia
def wait_for_presences(self, pres):
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()