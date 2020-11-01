import socket
import os

IP = '127.0.0.1'
PORT = 1729

client_file_path = r'RemoteClient\client_screen.jpg'
server_file_path = r'RemoteServer\server_screen.jpg'
server_dir_path = r'D:\\'
server_delete_file_path = r'D:\segev\\alice.txt'
server_copy_src_file_path = r'D:\alice.txt'
server_copy_dst_file_path = r'D:\segev\\'
server_exe_file_path = r'C:\Windows\System32\\notepad.exe'


def valid_request(request):
    """Check if the request is vakid(is included in the available command list)"""
    if (request == 'TAKE_SCREENSHOT' or request == 'SEND_FILE' or
                request == 'DIR' or request == 'DELETE' or request == 'COPY' or
                request == 'EXECUTE' or request == 'EXIT'):
        valid = True
    else:
        valid = False
    return valid


def send_request_to_server(client_socket, request):
    """ Send the request to the server."""
    if (request == 'TAKE_SCREENSHOT'):
        if os.path.exists(client_file_path):
            os.remove(client_file_path)
            print('client_screen.jpg file has been removed')
        client_socket.send(('TAKE_SCREENSHOT' + " " + server_file_path).encode())
    elif (request == 'DIR'):
        client_socket.send(('DIR' + " " + server_dir_path).encode())
    elif (request == 'EXIT'):
        client_socket.send(('EXIT').encode())
    elif (request == 'SEND_FILE'):
        client_socket.send(("SEND_FILE" + " " + server_file_path).encode())
    elif (request == 'DELETE'):
        client_socket.send(("DELETE" + " " + server_delete_file_path).encode())
    elif (request == 'COPY'):
        client_socket.send(("COPY" + " " + server_copy_src_file_path + " " + server_copy_dst_file_path).encode())
    elif (request == "EXECUTE"):
        client_socket.send(("EXECUTE" + " " + server_exe_file_path).encode())


def handle_server_response(client_socket, request):
    """ Receive the response from the server and handle it,
        according to the request.
        For example: DIR should result in printing the contents to the screen, 
        while SEND_FILE should result in saving the received file 
        and ntifying the user"""
    if (request == 'TAKE_SCREENSHOT' or request == 'DELETE' or request == 'COPY' or
                request == 'EXECUTE'):
        data = client_socket.recv(1024).decode()
        print(data)
    elif (request == "SEND_FILE"):
        if (os.path.exists(client_file_path)):
            os.remove(client_file_path)
            print(client_file_path + " removed")
        f = open(client_file_path, 'ab')
        data = client_socket.recv(1024)
        try:
            data = data.decode()
        except:
            while (data != 'LAST'):
                f.write(data)
                client_socket.send('ACK'.encode())
                data = client_socket.recv(1024)
                try:
                    data = data.decode()
                    print("the file has been sent")
                except:
                    pass
        f.close()
    elif (request == "DIR"):
        print("The content of " + server_dir_path + ":")
        data = client_socket.recv(8 * 1024).decode()
        print(data)


def main():
    # open socket to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    # print instructions
    print('Welcome to remote computer application. Available commands are:\n')
    print('TAKE_SCREENSHOT\nSEND_FILE\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')
    done = False
    # loop until user requested to exit
    while not done:
        request = input("Please enter command:\n")
        if (valid_request(request)):
            send_request_to_server(client_socket, request)
            handle_server_response(client_socket, request)
            if request == 'EXIT':
                done = True
        else:
            print('Welcome to remote computer application. Available commands are:\n')
            print('TAKE_SCREENSHOT\nSEND_FILE\nDIR\nDELETE\nCOPY\nEXECUTE\nEXIT')
            request = input("Please enter command:\n")
    client_socket.close()


if __name__ == '__main__':
    main()
