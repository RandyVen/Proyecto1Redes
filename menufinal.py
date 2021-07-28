from client import Register,Client


DOMAIN = '@alumchat.xyz'


if __name__ == '__main__':
    username = 'rands'
    password = '123'

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
    11. Definir mensaje de presencia \n
    12. Enviar archivo \n
    ===============================================
    """