from client import Register,Client
import os

DOMAIN = '@alumchat.xyz'


if __name__ == '__main__':
    username = 'marciano44'
    password = 'marciano441'

    active = True
    login_flag = False

    menu_logout = """============ MENU ============== \n
    1. Registrar un usuario\n
    2. Login\n
    3. Salir \n
    =================================================
    """

    menu_login = """============ MENU ============== \n
    1. Registrar un usuario \n
    2. Logout \n
    3. Eliminar cuenta del servidor \n
    4. Mostrar todos los usuarios \n
    5. Agregar un usuario a los contactos \n
    6. Mostrar detalles de un usuario \n
    7. Enviar mensaje a usuario \n
    8. Unirse a grupo \n
    9. Enviar mensaje a grupo \n
    10. Crear un grupo \n
    12. Enviar archivo \n
    ===============================================
    """
    # Ciclo que se ejecuta hasta que el usuario decide cerrar el programa
    while active:
        # Para mostrar el menu dependiendo si esta loqgueado o no el usuario
        if login_flag:
            print(menu_login)
        else:
            print(menu_logout)
        opcion = input('Ingrese una opcion')

        if opcion == '1': #Registrar un usuario
            username = input('Ingrese nombre usuario: ')
            password = input('Ingrese contraseña: ')
            register = Register(username+DOMAIN, password)
            if register.connect():
                register.process(block=True)
            else:
                print("No ha sido posible conectarse")

        elif opcion == '2' and login_flag == False: #Iniciar sesión
            username = input('Ingrese nombre usuario: ')
            password = input('Ingrese contraseña: ')
            cliente = Client(username+DOMAIN, password)
            if cliente.connect():
                cliente.process()
                print("Conectado")
                login_flag = True
            else:
                print("No fue posible conectarse")

        elif opcion == '2' and login_flag == True: #Logout
            if cliente.connect():
                cliente.logout()
                login_flag = False
            else:
                print("No fue posible desconectarse")

        elif opcion == '3' and login_flag == True: #Eliminar cuenta
            seguro = input("¿Esta totalmente seguro de eliminar la cuenta? (y/n)  ")
            if seguro == 'y':
                cliente.unregister()
                login_flag = False

        elif opcion == '4' and login_flag == True: #Mostrar usuarios
            cliente.getUsers()
        
        elif opcion == '5' and login_flag == True: #Agregar usuarios
            user = input("Ingrese el usuario que desea agregar: ")
            cliente.saveUser(user+DOMAIN)
        
        elif opcion == '6' and login_flag == True: #Mostrar usuario especifico
            user = input("Ingrese el usuario a buscar: ")
            cliente.getUser(user)

        elif opcion == '7' and login_flag == True: #Enviar mensaje
            jid = input("Usuario a enviar el mensaje: ")
            message = input("Mensaje a enviar")
            cliente.sendMessage(jid,message)

        elif opcion == '8' and login_flag == True: #Unirse a grupo
            room = input("Ingrese nombre del room: \n")
            nick = input("Ingrese apodo con el que aparecera en el room: \n")
            cliente.joinRoom(room,nick)

        elif opcion == '9' and login_flag == True: #Enviar mensaje a grupo
            room = input("Ingrese nombre del room: ")
            message = input("Ingrese el mensaje: ")
            cliente.messageRoom(room,message)
        
        elif opcion == '10' and login_flag == True: #Unirse a grupo
            room = input("Ingrese nombre del room: \n")
            nick = input("Ingrese apodo con el que aparecera en el room: \n")
            cliente.createRoom(room,nick)

        elif opcion == '11' and login_flag == True: #Cambiar estado
            print("""
            ========== Opciones de status ==========
            1. chat - Estas disponible para conversar \n
            2. away - No estas disponible para IM por periodo corto de tiempo \n
            3. xa - No estas disponible para un periodo largo de tiempo \n
            4. dnd - Estas ocupado y no quieres interrupcciones \n
            """)
            state = True
            show = 0
            while state:
                try:
                    show = int(input("Ingrese una opcion de status: "))
                    if(show>=1 and show<=4):
                        state = False
                except:
                    print("Debe ingresar un valor numerico")
            status = input("Ingrese mensaje para el status")
            cliente.changeStatus(show,status)
        
        elif opcion == '12' and login_flag == True: #Enviar archivo
            path = input('Ingrese el nombre del archivo: ')
            path_ = os.path.join(os.path.expanduser('~'),'Desktop','Images',path)
            dest = input('Ingrese al destinatario: ')
            cliente.sendFile(path_,dest)


        elif (opcion == '3') and (login_flag == False): #Salir
            active = False

        else:
            print('Ha ingresado una opcion que no es valida, intente de nuevo')
            
