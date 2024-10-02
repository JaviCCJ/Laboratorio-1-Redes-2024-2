import socket
import sys
import os
import pickle

HOST = "localhost"
PORT = 8000
MESSAGE_MAIN_MENU = """
--------- Bienvenido al Juego --------- 
Selecciona una opcion para jugar
    1. Jugar
    2. Salir
        """
MESSAGE_CHOICE_MOVE = """1

---Jugar---
    1- Ver Tablero
    2- Escoger Columna 
    3- Salir
    """
MESSAGE_ENTER_COLUMN = "Escoge una columna: "


def show_table(table):
    """
    Prints the elements of a 2D list, representing a table, row by row.
    """
    for fila in table:
        for elemento in fila:
            print(elemento+" ", end="")
        print("")


def clear_console():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def handle_choice_move(server, option):
    """
    Handle the choice made by the player.

    Args:
        server: The server object for communication.
        option: The option chosen by the player.

    Returns:
        None
    """
    if option == "1":
        message = "Ver Tablero"
        server.sendto(message.encode(), (HOST, PORT))
        data, _ = server.recvfrom(1024)
        table = pickle.loads(data)
        show_table(table)
    elif option == "2":
        option = "Escoger Columna"
        server.sendto(option.encode(), (HOST, PORT))
        data, _ = server.recvfrom(1024)
        print(data.decode())
        if data.decode() == "OK":
            column = input(MESSAGE_ENTER_COLUMN)
            server.sendto(column.encode(), (HOST, PORT))
            data, _ = server.recvfrom(1024)
            if isinstance(data, bytes) and data.decode('utf-8', 'ignore') in ("Jugador Gana", "Robot Gana"):
                winner = data.decode()
                server.sendto("Recibido".encode(), (HOST, PORT))
                data, _ = server.recvfrom(1024)
                table = pickle.loads(data)
                show_table(table)
                print(winner)
                server.close()
                sys.exit()
            table = pickle.loads(data)
            show_table(table)
        elif data.decode() == "Columna Llena":
            print("Columna Llena")
    else:
        server.sendto("Desconectar".encode(), (HOST, PORT))
        data, _ = server.recvfrom(1024)
        print("Player: Juego Terminado")
        server.close()
        sys.exit()


def exec_menu():
    """
    Executes the main menu of the program.
    This function prompts the user for an option and performs the corresponding action.
    It establishes a connection with the server and sends/receives data.
    If the user selects option 1, it enters a loop to handle moves until the game is over.
    
    Parameters:
        None
        
    Returns:
        None
    """
    option = ""
    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST, PORT))
        option = input(MESSAGE_MAIN_MENU)
        clear_console()
        if option == "1":
            message = "Jugar"
            server.sendto(message.encode(), (HOST, PORT))
            data, _ = server.recvfrom(1024)
            print("Player:", data.decode())
            if data.decode() == "Conexion Establecida":
                while True:
                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server.connect((HOST, PORT))
                    option = input(MESSAGE_CHOICE_MOVE)
                    handle_choice_move(server, option)
            print("Player: Connection be failed")
        else:
            print("Player: Salir del Juego")
            server.close()
            sys.exit()


exec_menu()
