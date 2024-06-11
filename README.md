# Command and Control (C2) with Backdoor

## Descripción

Este repositorio contiene tres scripts principales:

1. `backdoor.py`: Un script que actúa como un backdoor, conectándose a un servidor remoto y ejecutando comandos en el sistema.
2. `listener2.py`: Un script que actúa como el servidor, escuchando conexiones entrantes del backdoor y enviando comandos al cliente.
3. `malware2.py`: Un script que se encarga de obtener las contraseñas de Firefox de un usuario y enviarlas por correo electrónico.

## Archivos

### `backdoor.py`

Resumen: Este script es un backdoor que se conecta a un servidor remoto y ejecuta comandos en el sistema. El servidor puede enviar comandos al backdoor y recibir la salida de los comandos. El backdoor también puede enviar capturas de pantalla al servidor.

Funciones principales:
- `run_command(command)`: Ejecuta un comando en el sistema y devuelve la salida.
- `send_screenshot(client_socket)`: Envía una captura de pantalla al servidor.

### `listener2.py`

Este script actúa como el servidor para escuchar conexiones entrantes y enviar comandos al cliente.

Funciones principales:
- `send_email(subject, body, sender, recipients, password)`: Envía un correo electrónico con la información del comando ejecutado.
- `run_command(command)`: Ejecuta un comando en el backdoor y devuelve la salida.
- `get_users()`: Obtiene los usuarios del sistema y envía la información por correo electrónico.
- `send_file(file)`: Envía un archivo al cliente.
- `get_firefox()`: Obtiene las contraseñas de Firefox y las envía por correo electrónico.
- `get_chrome()`: Obtiene las contraseñas de Chrome y las envía por correo electrónico.
- `get_brave()`: Obtiene las contraseñas de Brave y las envía por correo electrónico.
- `screenshot()`: Obtiene una captura de pantalla del cliente y la envía por correo electrónico.
- `show_options()`: Muestra las opciones del menú de ayuda.
- `run()`: Ejecuta el listener y recibe los comandos del atacante.

### `malware2.py`

Este script se encarga de obtener las contraseñas de Firefox de un usuario y enviarlas por correo electrónico.

Funciones principales:
- `send_email(subject, body, sender, recipients, password)`: Envía un correo electrónico con las contraseñas obtenidas.
- `run_command(command)`: Ejecuta un comando a nivel de shell y devuelve la salida.
- `get_firefox_profiles(username)`: Obtiene el perfil de Firefox del usuario.
- `get_firefox_passwords(username, profile)`: Obtiene las contraseñas de Firefox usando `firefox_decrypt.py`.

## Herramientas de terceros

Este repositorio hace uso de las siguientes herramientas de terceros:

- [LaZagne](https://github.com/AlessandroZ/LaZagne): Utilizado para obtener las contraseñas almacenadas en varios navegadores, incluyendo Chrome y Brave.
- [firefox_decrypt](https://github.com/unode/firefox_decrypt): Utilizado para obtener las contraseñas almacenadas en Firefox.

Agradecemos a los desarrolladores de estas herramientas por su excelente trabajo.

## Uso

### `backdoor.py`

1. Ejecutar `backdoor.py` en el cliente (la máquina que será controlada remotamente).

### `listener2.py`

1. Ejecutar `listener2.py` en el servidor (la máquina que controlará remotamente el cliente).
2. Enviar comandos a través del terminal del servidor para controlar el cliente.

### `malware2.py`

1. Ejecutar `malware2.py` en la máquina objetivo para obtener las contraseñas de Firefox y enviarlas por correo electrónico.

## Advertencia

Este software es para fines educativos y de pruebas de seguridad solamente. No se debe utilizar en sistemas sin el permiso explícito del propietario. El uso indebido de este software puede resultar en acciones legales.

## Configuración

Asegúrate de configurar las siguientes variables en los scripts con tus propios valores:
- `sender`: El correo electrónico del remitente.
- `recipients`: El correo electrónico del destinatario.
- `password`: La contraseña del correo electrónico del remitente.
- `ip_server`: La dirección IP del servidor.
- `port`: El puerto de escucha del servidor.
