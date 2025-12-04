<h3> REQUERIMIENTOS DEL DISPOSITIVO EyEDooR </h3>
El proyecto EyeDooR consta de 3 componentes principales:
1. Backend (Python/Flask)
2. Frontend (HTML/CSS/JavaScript)
3. Hardware (Arduino/ESP32)


═══════════════════════════════════════════════════════════════════════════════
                    🐍 PARTE 1: BACKEND (PYTHON/FLASK)
═══════════════════════════════════════════════════════════════════════════════

📦 Instalación de Dependencias
------------------------------
Ejecutar en la terminal/PowerShell:

    pip install flask firebase-admin werkzeug requests


📚 Descripción de Cada Paquete
--------------------------------

1. Flask (~3.0.0)
   ├─ Propósito: Framework web principal para el servidor
   ├─ Funciones: Rutas HTTP, renderizado de templates, sesiones
   └─ Uso: Base del servidor que maneja /login, /registro, /bienvenido, /capturar

2. firebase-admin (~6.0.0)
   ├─ Propósito: SDK oficial de Google para Firebase desde Python
   ├─ Funciones: Autenticación, Realtime Database, almacenamiento
   ├─ Uso: Gestiona usuarios, códigos de producto, metadatos de fotos
   └─ Requiere: Archivo "eyedoor-firebase.json" con credenciales

3. Werkzeug (~3.0.0)
   ├─ Propósito: Librería de utilidades WSGI (incluida con Flask)
   ├─ Funciones: Hash de contraseñas con bcrypt, seguridad
   ├─ Uso: generate_password_hash(), check_password_hash()
   └─ Seguridad: Nunca almacena contraseñas en texto plano

4. requests (~2.31.0)
   ├─ Propósito: Cliente HTTP para hacer peticiones a servidores externos
   ├─ Funciones: GET, POST, manejo de timeouts, headers
   ├─ Uso: Se conecta al ESP32-CAM en http://10.154.150.123:81/capture
   └─ Timeout: 15 segundos para evitar bloqueos


🔧 Requisitos del Sistema
--------------------------
- Python 3.8 o superior
- pip actualizado: python -m pip install --upgrade pip
- Sistema operativo: Windows, Linux, macOS
- Puerto 5000 disponible para Flask


📁 Archivos Necesarios
----------------------
- eyedoor-firebase.json (credenciales de Firebase)
- app.py (servidor backend)
- /templates/*.html (plantillas HTML)
- /static/logo.png (logo del proyecto)
- /fotos_eyedoor/ (carpeta se crea automáticamente)


🚀 Ejecución del Backend
-------------------------
    python app.py

El servidor estará disponible en: http://localhost:5000 o http://0.0.0.0:5000


═══════════════════════════════════════════════════════════════════════════════
🎨 PARTE 2: FRONTEND (HTML/CSS/JAVASCRIPT)
═══════════════════════════════════════════════════════════════════════════════

📦 Librerías JavaScript (CDN - No Requiere Instalación)
--------------------------------------------------------

1. Firebase JavaScript SDK v8.10.0
   ├─ Archivo: firebase-app.js
   ├─ Propósito: Núcleo de Firebase para navegadores web
   ├─ CDN: https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js
   └─ Uso: Inicialización de Firebase en el cliente

2. Firebase Realtime Database v8.10.0
   ├─ Archivo: firebase-database.js
   ├─ Propósito: Base de datos en tiempo real
   ├─ CDN: https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js
   └─ Uso: Escucha eventos del timbre en /timbres


📄 Archivos del Frontend
-------------------------
- templates/login.html (página de inicio de sesión)
- templates/registro.html (registro de usuarios)
- templates/recuperar.html (recuperación de contraseña)
- templates/bienvenido.html (panel principal con cámara)
- static/logo.png (logo de la aplicación)


🌐 Navegadores Compatibles
---------------------------
- Google Chrome 90+
- Mozilla Firefox 88+
- Microsoft Edge 90+
- Safari 14+


═══════════════════════════════════════════════════════════════════════════════
🔌 PARTE 3: HARDWARE (ARDUINO/ESP32)
═══════════════════════════════════════════════════════════════════════════════

El proyecto utiliza 2 dispositivos ESP32:
1. ESP32 con botón de timbre (arduino/boton/boton.ino)
2. ESP32-CAM para video y fotos (arduino/camara/camara.ino)


📦 Instalación de Placa ESP32 en Arduino IDE
---------------------------------------------

Paso 1: Agregar URL del Gestor de Placas
   ├─ Abrir: Arduino IDE > Archivo > Preferencias
   ├─ En "Gestor de URLs Adicionales de Tarjetas":
   └─ Agregar: https://dl.espressif.com/dl/package_esp32_index.json

Paso 2: Instalar Soporte ESP32
   ├─ Abrir: Herramientas > Placa > Gestor de placas
   ├─ Buscar: "esp32"
   ├─ Instalar: "esp32" by Espressif Systems (versión 2.0.11 o superior)
   └─ Reiniciar Arduino IDE


📚 Librerías para ESP32 con Botón (boton.ino)
----------------------------------------------

1. WiFi.h (Incluida con ESP32)
   ├─ Autor: Espressif Systems
   ├─ Propósito: Conectividad WiFi para ESP32
   ├─ Versión: Incluida en el paquete ESP32
   └─ Uso: WiFi.begin(), WiFi.status()

2. time.h (Librería estándar de C)
   ├─ Propósito: Manejo de tiempo, NTP, timestamps
   ├─ Versión: Estándar
   ├─ Funciones: configTime(), getLocalTime(), strftime()
   └─ Uso: Sincronización con servidores NTP (pool.ntp.org, time.google.com)

3. FirebaseESP32 (Requiere Instalación Manual)
   ├─ Autor: Mobizt
   ├─ Instalación: Sketch > Incluir biblioteca > Gestionar bibliotecas
   ├─ Buscar: "Firebase ESP32 Client"
   ├─ Instalar: "Firebase Arduino Client Library for ESP8266 and ESP32" by Mobizt
   ├─ Versión recomendada: 4.3.0 o superior
   ├─ Componentes:
   │  ├─ FirebaseESP32.h (core)
   │  ├─ addons/RTDBHelper.h (Realtime Database)
   │  └─ addons/TokenHelper.h (autenticación)
   └─ Uso: Firebase.begin(), Firebase.setJSON()

Configuración del ESP32 con Botón:
   ├─ Placa: "ESP32 Dev Module"
   ├─ Puerto: Seleccionar puerto COM correspondiente
   ├─ Upload Speed: 115200
   ├─ CPU Frequency: 240MHz
   └─ Flash Frequency: 80MHz


📚 Librerías para ESP32-CAM (camara.ino)
-----------------------------------------

1. esp_camera.h (Incluida con ESP32)
   ├─ Autor: Espressif Systems
   ├─ Propósito: Driver oficial para cámara OV2640
   ├─ Versión: Incluida en el paquete ESP32
   ├─ Funciones: esp_camera_init(), esp_camera_fb_get(), esp_camera_fb_return()
   └─ Uso: Captura de fotos y streaming de video

2. WiFi.h (Incluida con ESP32)
   ├─ Mismo uso que en el ESP32 con botón
   └─ Conectividad WiFi para ESP32-CAM

3. esp_http_server.h (Incluida con ESP32)
   ├─ Autor: Espressif Systems
   ├─ Propósito: Servidor HTTP nativo de ESP-IDF
   ├─ Versión: Incluida en el paquete ESP32
   ├─ Funciones: httpd_start(), httpd_register_uri_handler(), httpd_resp_send()
   └─ Uso: Crea 2 servidores HTTP (puerto 80 para stream, puerto 81 para captura)

4. freertos/semphr.h (Incluida con ESP32)
   ├─ Autor: FreeRTOS
   ├─ Propósito: Semáforos y sincronización de tareas
   ├─ Versión: Incluida en el paquete ESP32
   ├─ Funciones: xSemaphoreCreateMutex(), xSemaphoreTake(), xSemaphoreGive()
   └─ Uso: Evita conflictos entre stream y captura usando mutex

Configuración del ESP32-CAM:
   ├─ Placa: "AI Thinker ESP32-CAM"
   ├─ Puerto: Seleccionar puerto COM correspondiente
   ├─ Upload Speed: 115200
   ├─ CPU Frequency: 240MHz
   ├─ Flash Frequency: 80MHz
   ├─ Flash Mode: QIO
   ├─ Partition Scheme: "Huge APP (3MB No OTA/1MB SPIFFS)"
   └─ Programador FTDI: Necesario para subir código (conectar GPIO0 a GND)


🔧 Configuración de Red WiFi
-----------------------------
Ambos ESP32 deben estar en la misma red WiFi:
   ├─ SSID: "Antonio"
   ├─ Contraseña: "12345678"
   ├─ Tipo: 2.4 GHz (ESP32 no soporta 5 GHz)
   └─ IP del ESP32-CAM: 10.154.150.123 (puede variar)


📡 Endpoints del ESP32-CAM
---------------------------
Una vez programado y conectado:
   ├─ Stream de video: http://10.154.150.123/
   └─ Captura de foto: http://10.154.150.123:81/capture


🔌 Conexiones Físicas
----------------------

ESP32 con Botón:
   ├─ Botón físico conectado a GPIO 4
   ├─ Configuración: INPUT_PULLUP (activo en LOW)
   └─ Debounce: 2000 ms entre pulsaciones

ESP32-CAM AI-Thinker:
   ├─ Modelo de cámara: OV2640
   ├─ Resolución configurada: QVGA (320x240)
   ├─ Calidad JPEG: 10 (alta calidad)
   └─ Frame buffers: 2 (para streaming fluido)


═══════════════════════════════════════════════════════════════════════════════
🗄️ PARTE 4: BASE DE DATOS (FIREBASE REALTIME DATABASE)
═══════════════════════════════════════════════════════════════════════════════

Estructura de la Base de Datos:
--------------------------------
/users/{uid}
   ├─ email: String
   ├─ password_hash: String (bcrypt)
   ├─ product_code: String (formato: XXXXX-XXXXX-XXXXX)
   ├─ security_question: String
   └─ security_answer_hash: String (bcrypt)

/timbres
   ├─ evento: "Timbre presionado"
   └─ timestamp: "YYYY-MM-DD HH:MM:SS"

/fotos_eyedoor/{photo_id}
   ├─ file: String (nombre del archivo .jpg)
   ├─ timestamp: String (ISO format)
   └─ uploader: String (email del usuario)


Configuración de Firebase:
---------------------------
   ├─ Proyecto: eyedoor-49c27
   ├─ Database URL: https://eyedoor-49c27-default-rtdb.firebaseio.com/
   ├─ API Key: AIzaSyDQ9Vq0xYg_e82XKOKajuLtlt8YRanxVdw
   └─ Archivo de credenciales: eyedoor-firebase.json


═══════════════════════════════════════════════════════════════════════════════
🚀 GUÍA DE INICIO RÁPIDO
═══════════════════════════════════════════════════════════════════════════════

Paso 1: Configurar Backend
   1. Instalar Python 3.8+
   2. pip install flask firebase-admin werkzeug requests
   3. Colocar eyedoor-firebase.json en la carpeta del proyecto
   4. python app.py

Paso 2: Programar Hardware
   1. Instalar Arduino IDE
   2. Agregar soporte para ESP32
   3. Instalar librería "Firebase ESP32 Client" by Mobizt
   4. Subir boton.ino al ESP32 con botón
   5. Subir camara.ino al ESP32-CAM

Paso 3: Verificar Funcionamiento
   1. Abrir navegador en http://localhost:5000
   2. Registrarse con un código de producto válido
   3. Iniciar sesión
   4. Verificar que el stream de video funciona
   5. Presionar el botón físico o web para tomar una foto


═══════════════════════════════════════════════════════════════════════════════
⚠️ SOLUCIÓN DE PROBLEMAS COMUNES
═══════════════════════════════════════════════════════════════════════════════

Backend no inicia:
   └─ Verificar que el puerto 5000 no esté en uso
   └─ Verificar que eyedoor-firebase.json existe

ESP32 no conecta a WiFi:
   └─ Verificar SSID y contraseña
   └─ Asegurarse de usar red 2.4 GHz (no 5 GHz)
   └─ Revisar Monitor Serial (115200 baudios)

ESP32-CAM no se puede programar:
   └─ Conectar GPIO0 a GND durante la carga
   └─ Usar programador FTDI de 5V o 3.3V
   └─ Desconectar GPIO0 después de cargar

Firebase no actualiza:
   └─ Verificar reglas de seguridad en Firebase Console
   └─ Verificar credenciales en eyedoor-firebase.json
   └─ Revisar internet del ESP32

Fotos no se capturan:
   └─ Verificar IP del ESP32-CAM (puede cambiar)
   └─ Actualizar CAMERA_CAPTURE_URL en app.py
   └─ Revisar que el puerto 81 esté respondiendo


═══════════════════════════════════════════════════════════════════════════════
📞 INFORMACIÓN ADICIONAL
═══════════════════════════════════════════════════════════════════════════════

Para una documentación técnica completa con diagramas y explicaciones
detalladas de cada componente, consulta el archivo:
   documentacion_eyedoor.md

═══════════════════════════════════════════════════════════════════════════════
                            Fin del Documento
═══════════════════════════════════════════════════════════════════════════════
