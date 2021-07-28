from sleekxmpp import ClientXMPP
from sleekxmpp.xmlstream.stanzabase import ET, ElementBase
import threading


class Register(ClientXMPP):

    def __init__(self, jid, password):
        ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.registerAccount)

        self.register_plugin('xep_0030')
        self.register_plugin('xep_0199') 
        self.register_plugin('xep_0004') 
        self.register_plugin('xep_0077') 
        self.register_plugin('xep_0045') 
        self.register_plugin('xep_0096') 


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