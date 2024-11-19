# Command and Control (C2) con Backdoor versión 2

## Descripción
Este proyecto implementa un sistema Command and Control (C2) con un backdoor en Python. Consiste en dos componentes principales:
- Un servidor (listener) que controla las conexiones entrantes
- Un cliente (backdoor) que se ejecuta en la máquina objetivo

## Características

### Servidor (listener2 no color.py)
- Escucha conexiones entrantes en un puerto específico
- Envía comandos al backdoor
- Recibe y guarda archivos del cliente
- Captura pantallas remotamente
- Envía resultados por email
- Extrae contraseñas de navegadores (Firefox, Chrome, Brave)
- Interfaz de línea de comandos interactiva

### Cliente (backdoor.py)
- Se conecta al servidor C2
- Ejecuta comandos recibidos
- Persistencia mediante registro de Windows
- Toma capturas de pantalla
- Transfiere archivos
- Verifica privilegios de administrador
- Reconexión automática si pierde conexión

## Comandos Disponibles

```
screenshot:      Toma captura y envía por email
screenshot2:     Toma captura y guarda en servidor
upload [file]:   Sube archivo al cliente
download [file]: Descarga archivo del cliente
cd [directory]:  Cambia directorio actual
geturl [url]:    Descarga archivo de internet
start:           Inicia aplicación sin esperar
checkadmin:      Verifica privilegios admin
get users:       Lista usuarios del sistema
get firefox:     Extrae contraseñas Firefox
get chrome:      Extrae contraseñas Chrome
get brave:       Extrae contraseñas Brave
help:            Muestra ayuda
exit:            Cierra conexión
```

## Requisitos
- Python 3.x
- Módulos: socket, mss, requests, smtplib

## Configuración
1. En 

listener2 no color.py

 configurar:
```python
sender = "email@ejemplo.com"
recipients = ["destino@ejemplo.com"]
password = "contraseña"
ip_server = "IP_SERVIDOR"
port = PUERTO
```

2. En 

backdoor.py

 configurar:
```python
server_ip = 'IP_SERVIDOR'
server_port = PUERTO
```

## Uso
1. Ejecutar servidor:
```bash
python listener2_no_color.py
```

2. Ejecutar backdoor en objetivo:
```bash
python backdoor.py
```

## Agradecimientos

Este proyecto hace uso de las siguientes herramientas de terceros:

### Lazagne
- Creador: AlessandroZ
- Repositorio: https://github.com/AlessandroZ/LaZagne
- Descripción: Una herramienta de código abierto para recuperar contraseñas almacenadas en una computadora local.

### Firefox Decrypt
- Creador: Unode
- Repositorio: https://github.com/unode/firefox_decrypt
- Descripción: Una herramienta para extraer contraseñas de los perfiles de Firefox.

Agradecemos especialmente a estos desarrolladores por crear y mantener estas herramientas que han hecho posible algunas funcionalidades de este proyecto.

## Advertencia
Este software es solo para fines educativos y de pruebas autorizadas.

## Nota Legal
Este software debe usarse solo con fines educativos y en entornos controlados con los permisos adecuados. No nos hacemos responsables del mal uso de estas herramientas.

## Licencia
Este proyecto es para uso educativo únicamente. Las herramientas de terceros mencionadas tienen sus propias licencias que deben respetarse.