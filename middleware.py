import socket
import os
import pickle

HOST = "localhost"
PORT = 8000
PORT_CONNECT4 = 8001

table = [["0", "0", "0", "0", "0", "0"],
         ["0", "0", "0", "0", "0", "0"],
         ["0", "0", "0", "0", "0", "0"],
         ["0", "0", "0", "0", "0", "0"],
         ["0", "0", "0", "0", "0", "0"],
         ["0", "0", "0", "0", "0", "0"]]


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Middleware: Server is running on {HOST}: {PORT}")


def find_crosses_player():
    """
    Check if there are any four adjacent "X" in a row, column, or diagonal in the given table.

    Parameters:
        table (list): A 2D list representing the table.

    Returns:
        bool: True if there are four adjacent "X", False otherwise.
    """
    # Check rows
    for row in table:
        for i in range(len(row) - 3):
            if row[i:i+4] == ["X", "X", "X", "X"]:
                return True

    # Check columns
    for i in range(len(table[0])):
        for j in range(len(table) - 3):
            column = [table[k][i] for k in range(j, j+4)]
            if column == ["X", "X", "X", "X"]:
                return True

    # Check diagonals
    for i in range(len(table) - 3):
        for j in range(len(table[0]) - 3):
            diagonal1 = [table[i+k][j+k] for k in range(4)]
            diagonal2 = [table[i+k][j+3-k] for k in range(4)]
            if diagonal1 == ["X", "X", "X", "X"] or diagonal2 == ["X", "X", "X", "X"]:
                return True

    return False


def find_crosses_robot():
    """
    Checks if there are any crosses ("Y") in the given table.

    Returns:
        True if there are any crosses in the table, False otherwise.
    """
    # Check rows
    for row in table:
        for i in range(len(row) - 3):
            if row[i:i+4] == ["Y", "Y", "Y", "Y"]:
                return True

    # Check columns
    for i in range(len(table[0])):
        for j in range(len(table) - 3):
            column = [table[k][i] for k in range(j, j+4)]
            if column == ["Y", "Y", "Y", "Y"]:
                return True

    # Check diagonals
    for i in range(len(table) - 3):
        for j in range(len(table[0]) - 3):
            diagonal1 = [table[i+k][j+k] for k in range(4)]
            diagonal2 = [table[i+k][j+3-k] for k in range(4)]
            if diagonal1 == ["Y", "Y", "Y", "Y"] or diagonal2 == ["Y", "Y", "Y", "Y"]:
                return True

    return False


def clear_console():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def show_table():
    """
    Prints the elements of a 2D list, representing a table, row by row.
    """
    for row in table:
        for elemento in row:
            print(elemento+" ", end="")
        print("")


def insert_coin_player(column):
    """
    Insert a coin for the player in the specified column of the game table.

    Parameters:
        column (int): The column number in which to insert the coin.

    Returns:
        bool: True if the coin was successfully inserted in an empty spot, False otherwise.
    """
    for row in range(5, -1, -1):
        if table[row][column] == "0":
            table[row][column] = "X"
            return True
    return False


def insert_coin_robot(column):
    """
    Inserts a coin into the specified column in the robot game table.

    Args:
        column (int): The index of the column to insert the coin into.

    Returns:
        bool: True if the coin was successfully inserted, False otherwise.
    """
    for row in range(5, -1, -1):
        if table[row][column] == "0":
            table[row][column] = "Y"
            return True
    return False


def connect(option):
    """
    Connects to a server using a UDP socket.
    """
    global PORT_CONNECT4
    server_connect4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_connect4.connect((HOST, PORT_CONNECT4))

    server_connect4.sendto(option.encode(), (HOST, PORT_CONNECT4))

    data, address = server_connect4.recvfrom(1024)
    message, random_port = data.decode().split(":")


    print('Middleware:', address[0], ':', address[1])
    print('Middleware:', data.decode())

    PORT_CONNECT4 = int(random_port)
    print('Middleware: PORT_CONNECT4 =', PORT_CONNECT4)
    server_connect4.close()
    return message.encode()





def listen():
    while True:
        client, address = server.accept()
        print(f"Middleware Client Address: {address}")
        data = client.recv(1024)
        option = data.decode()
        #clear_console()
        if option == "Jugar":
            response_connect4 = connect(option)
            client.sendall(response_connect4)
        elif option == "Ver Tablero":
            table_serialized = pickle.dumps(table)
            client.sendall(table_serialized)
        elif option == "Escoger Columna":
            client.sendall("OK".encode())
            column = client.recv(1024)
            inserted = insert_coin_player(int(column)-1)
            if inserted:
                if find_crosses_player():
                    print("Middleware: Jugador Gana")
                    client.sendall("Jugador Gana".encode())
                    client.recv(1024)
                    connect("Desconectar")
                    table_serialized = pickle.dumps(table)
                    client.sendall(table_serialized)
                    client.close()
                    break
                column_robot = connect("Insertar")
                inserted = insert_coin_robot(int(column_robot))
                if find_crosses_robot():
                    print("Middleware: Robot Gana")
                    client.sendall("Robot Gana".encode())
                    client.recv(1024)
                    connect("Desconectar")
                    table_serialized = pickle.dumps(table)
                    client.sendall(table_serialized)
                    client.close()
                    break
                table_serialized = pickle.dumps(table)
                client.sendall(table_serialized)
                print("Middleware: Movimiento del robot",
                      int(column_robot.decode())+1)
            else:
                table_serialized = pickle.dumps(table)
                client.sendall(table_serialized)
                print("Middleware: Columna Llena")
        elif option == "Desconectar":
            response_connect4 = connect("Desconectar")
            client.sendall("Robot Desconectado".encode())
            client.close()
            break
        else:
            print("Middleware: Juego Terminado")
            client.close()
            break


listen()
