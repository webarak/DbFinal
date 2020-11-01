import socket
import os
import sys
import glob
import shutil
from PIL import ImageGrab

IP = '0.0.0.0'
PORT = 1729
CHUNK_SIZE = 1024


def recive_client_request(client_socket):
    data = client_socket.recv(1024).decode()
    command_plus_params = data.split(" ")
    return command_plus_params


def check_client_request(command_plus_params):
    valid = True
    error_massage = None

    command = command_plus_params[0]
    if (command == "TAKE_SCREENSHOT"):
        path_params = command_plus_params[1].split("\\")
        del path_params[-1]
        dir_path = ("\\").join(path_params)
        if (os.path.exists(dir_path)):
            valid = True
            error_massage = None
        else:
            valid = False
            error_massage = dir_path + "not found"

    elif (command == 'SEND_FILE' or command == 'DIR' or command == 'DELETE' or command == 'EXECUTE'):
        if (os.path.exists(command_plus_params[1])):
            valid = True
            error_massage = None
        else:
            valid = False
            error_massage = command_plus_params[1] + "not found"

    elif (command == "COPY"):
        file_path = command_plus_params[1]
        path_params_folder = command_plus_params[2].split("\\")
        del path_params_folder[-1]
        dir_path = ("\\").join(path_params_folder)
        if (os.path.exists(file_path) and os.path.exists(dir_path)):
            valid = True
            error_massage = None
        else:
            valid = False
            error_massage = "either source file or detanation folder not found"

    return valid, error_massage


def handle_client_request(command_plus_params):
    command = command_plus_params[0]
    if (command == "TAKE_SCREENSHOT"):
        if (os.path.exists(command_plus_params[1])):
            os.remove(command_plus_params[1])
        image = ImageGrab.grab()
        image.save(command_plus_params[1])
        return command + "--ScreenShot has been saved in " + command_plus_params[1]

    if (command == "DIR"):
        files_list = glob.glob(command_plus_params[1] + '\*.*')
        files_list_string = ("\n").join(files_list)
        return command + "--" + files_list_string

    if (command == 'DELETE'):
        os.remove(command_plus_params[1])
        return "the file deleted"

    if (command == 'COPY'):
        shutil.copy(command_plus_params[1], command_plus_params[2])
        return command_plus_params[1] + "copied to" + command_plus_params[2]

    if (command == "EXECUTE"):
        os.startfile(command_plus_params[1])
        return command_plus_params[1] + "is execute"

    if (command == "SEND_FILE"):
        return command_plus_params[1] + " " + "the file was send"


def send_response_to_client(command, response, client_socket):
    if (command == "SEND_FILE" and os.path.exists(response.split(" ")[0])):
        f = open(response.split(" ")[0], 'rb')
        data = f.read(CHUNK_SIZE)
        while data:
            client_socket.send(data)
            ack = client_socket.recv(1024).decode()
            data = f.read(CHUNK_SIZE)
        client_socket.send('LAST'.encode())
        f.close()
    else:
        try:
            client_socket.send(response.encode())
        except:
            client_socket.send("THE FILE DIDNT EXCIST IN THE SERVER".encode())



def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()

    done = False
    while (not done):
        lst_params = recive_client_request(client_socket)
        if (lst_params[0] == "EXIT"):
            done = True
        else:
            valid, error_massage = check_client_request(lst_params)
            if valid:
                response = handle_client_request(lst_params)
                send_response_to_client(lst_params[0], response, client_socket)
            else:
                send_response_to_client(lst_params[0], error_massage, client_socket)

    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
