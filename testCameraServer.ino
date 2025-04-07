#include "esp_camera.h"
#include "esp_http_server.h"
#include <WiFi.h>
#include <Base64.h>

// Configuración de la red Wi-Fi
const char *ssid = "Sophia 2.4";
const char *password = "Perrito123";

// Definir la configuración de la cámara ESP32-CAM
camera_config_t config;

// Crear el servidor en el puerto 80
httpd_handle_t server = NULL;


esp_err_t stream_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");

  // Bucle infinito para enviar frames
  while (true) {
    camera_fb_t *fb = esp_camera_fb_get(); // Obtener la imagen de la cámara

    if (!fb) {
      Serial.println("Error al capturar la imagen");
      return ESP_FAIL;
    }

    // Enviar cada imagen como parte del stream
    String part = "--frame\r\n";
    part += "Content-Type: image/jpeg\r\n";
    part += "Content-Length: " + String(fb->len) + "\r\n\r\n";

    // Enviar los datos de la imagen
    httpd_resp_send_chunk(req, part.c_str(), part.length());
    httpd_resp_send_chunk(req, (const char*)fb->buf, fb->len);
    httpd_resp_send_chunk(req, "\r\n", 2); // Separador de los frames

    esp_camera_fb_return(fb); // Liberar la memoria de la imagen

    delay(10); // Un pequeño retraso para evitar que el procesador se sobrecargue
  }

  return ESP_OK;
}

esp_err_t index_handler(httpd_req_t *req) {
  const char* html = "<html><body>"
                     "<h1>ESP32-CAM Stream</h1>"
                     "<img src=\"/stream\" width=\"640\" height=\"480\">"
                     "</body></html>";
  httpd_resp_send(req, html, HTTPD_RESP_USE_STRLEN);
  return ESP_OK;
}

void setup() {
  Serial.begin(115200);

  // Configuración de la cámara (ajustar según sea necesario)
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;  // Resolución más baja para mejor rendimiento
  config.pixel_format = PIXFORMAT_JPEG;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  // Inicializar la cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error 0x%x", err);
    return;
  }

  Serial.println("Cámara inicializada correctamente");

  // Conexión a la red Wi-Fi
  Serial.print("Conectando a Wi-Fi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Conectado a Wi-Fi");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Configurar las rutas HTTP
  httpd_uri_t index_uri = {
    .uri = "/",
    .method = HTTP_GET,
    .handler = index_handler,
    .user_ctx = NULL
  };

  httpd_uri_t stream_uri = {
    .uri = "/stream",
    .method = HTTP_GET,
    .handler = stream_handler,
    .user_ctx = NULL
  };

  // Configurar el servidor HTTP
  httpd_config_t config_httpd = HTTPD_DEFAULT_CONFIG();
  if (httpd_start(&server, &config_httpd) == ESP_OK) {
    httpd_register_uri_handler(server, &index_uri);
    httpd_register_uri_handler(server, &stream_uri);
  }

  //Se configura el LED rojo interno
  pinMode(33,OUTPUT);
  digitalWrite(33,LOW);
}

void loop() {

}
