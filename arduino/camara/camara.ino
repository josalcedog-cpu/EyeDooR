#include "esp_camera.h"
#include <WiFi.h>
#include "esp_http_server.h"
#include "freertos/semphr.h"

// ===== CREDENCIALES WIFI =====
const char* ssid = "Antonio";
const char* password = "12345678";

// ===== PINES ESP32-CAM AI THINKER =====
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// MUTEX para evitar conflicto entre el stream y la captura de foto
SemaphoreHandle_t camera_mutex;

// =====================================================
// CONFIGURACIÓN GENERAL DE CÁMARA
// =====================================================
camera_config_t createCameraConfig() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0       = Y2_GPIO_NUM;
    config.pin_d1       = Y3_GPIO_NUM;
    config.pin_d2       = Y4_GPIO_NUM;
    config.pin_d3       = Y5_GPIO_NUM;
    config.pin_d4       = Y6_GPIO_NUM;
    config.pin_d5       = Y7_GPIO_NUM;
    config.pin_d6       = Y8_GPIO_NUM;
    config.pin_d7       = Y9_GPIO_NUM;
    config.pin_xclk     = XCLK_GPIO_NUM;
    config.pin_pclk     = PCLK_GPIO_NUM;
    config.pin_vsync    = VSYNC_GPIO_NUM;
    config.pin_href     = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn     = PWDN_GPIO_NUM;
    config.pin_reset    = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // Ajusta aquí la calidad si lo necesitas
    // FRAMESIZE_QVGA (320x240), FRAMESIZE_VGA (640x480), etc.
    config.frame_size   = FRAMESIZE_QVGA; 
    config.jpeg_quality = 10; // 0-63, menor número = mayor calidad
    config.fb_count     = 2;  // Usar 2 buffers para mejor fluidez en stream

    return config;
}

// =====================================================
// HANDLER STREAM (VIDEO EN VIVO)
// =====================================================
static esp_err_t stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char buf[64];
    size_t _jpg_buf_len = 0;
    uint8_t * _jpg_buf = NULL;

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");
    if (res != ESP_OK) return res;

    while (true) {
        // Tomar el mutex para usar la cámara
        xSemaphoreTake(camera_mutex, portMAX_DELAY);
        fb = esp_camera_fb_get();
        xSemaphoreGive(camera_mutex);

        if (!fb) {
            Serial.println("Error capturando frame para stream");
            res = ESP_FAIL;
        } else {
            _jpg_buf_len = fb->len;
            _jpg_buf = fb->buf;
        }

        if (res == ESP_OK) {
            size_t hlen = snprintf(buf, 64,
                "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
                _jpg_buf_len);

            res = httpd_resp_send_chunk(req, buf, hlen);
        }

        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
        }

        if (fb) {
            esp_camera_fb_return(fb);
            fb = NULL;
            _jpg_buf = NULL;
        } else if (_jpg_buf) {
            free(_jpg_buf);
            _jpg_buf = NULL;
        }

        if (res != ESP_OK) break;

        // ============================================================
        // ⚠️ CAMBIO CRÍTICO: Pausa para dejar respirar al CPU
        // Esto permite que otras tareas (como /capture) se ejecuten
        // ============================================================
        vTaskDelay(pdMS_TO_TICKS(50)); 
    }

    return res;
}

// =====================================================
// HANDLER CAPTURE (OPTIMIZADO - SIN REINICIOS)
// =====================================================
static esp_err_t capture_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;

    Serial.println("📸 Solicitando captura...");

    // 1. Obtener frame protegiendo el acceso con mutex
    xSemaphoreTake(camera_mutex, portMAX_DELAY);
    fb = esp_camera_fb_get();
    xSemaphoreGive(camera_mutex);

    if (!fb) {
        Serial.println("❌ Error: No se pudo capturar el frame");
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    // 2. Configurar headers para respuesta de imagen
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    // Importante para evitar problemas de CORS si accedes desde otro dominio
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    // 3. Enviar el buffer de la imagen
    res = httpd_resp_send(req, (const char *)fb->buf, fb->len);

    // 4. Liberar memoria
    esp_camera_fb_return(fb);
    
    Serial.println(res == ESP_OK ? "✅ Foto enviada correctamente" : "❌ Error enviando foto");
    return res;
}

// =====================================================
// INICIAR SERVIDORES (DUAL PORT)
// =====================================================
void startCameraServer() {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.server_port = 80; // Puerto para STREAM

    httpd_handle_t stream_httpd = NULL;
    httpd_handle_t capture_httpd = NULL;

    // 1. Iniciar Servidor de Stream (Puerto 80)
    if (httpd_start(&stream_httpd, &config) == ESP_OK) {
        httpd_uri_t uri_stream = {
            .uri       = "/",
            .method    = HTTP_GET,
            .handler   = stream_handler,
            .user_ctx  = NULL
        };
        httpd_register_uri_handler(stream_httpd, &uri_stream);
        Serial.println("✅ Stream Server iniciado en puerto 80");
    }

    // 2. Iniciar Servidor de Captura (Puerto 81)
    config.server_port = 81;
    config.ctrl_port = 32769; // IMPORTANTE: Puerto de control diferente para no chocar
    
    if (httpd_start(&capture_httpd, &config) == ESP_OK) {
        httpd_uri_t uri_capture = {
            .uri       = "/capture",
            .method    = HTTP_GET,
            .handler   = capture_handler,
            .user_ctx  = NULL
        };
        httpd_register_uri_handler(capture_httpd, &uri_capture);
        Serial.println("✅ Capture Server iniciado en puerto 81");
    }
}

// =====================================================
// SETUP
// =====================================================
void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();

    // Crear el mutex
    camera_mutex = xSemaphoreCreateMutex();

    // Configurar e iniciar la cámara
    camera_config_t config = createCameraConfig();
    
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("❌ Error iniciando cámara: 0x%x", err);
        return;
    }

    // Conectar a WiFi
    WiFi.begin(ssid, password);
    Serial.print("Conectando WiFi...");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("");
    Serial.println("WiFi conectado!");
    Serial.print("Dirección IP: http://");
    Serial.println(WiFi.localIP());
    Serial.println("Stream en: /");
    Serial.println("Captura en: /capture");

    // Iniciar servidor web
    startCameraServer();
}

// =====================================================
// LOOP
// =====================================================
void loop() {
    // El servidor web maneja todo en segundo plano
    delay(10000); 
}