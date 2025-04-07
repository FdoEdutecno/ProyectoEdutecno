#include "esp_camera.h"
#include "esp_http_server.h"
#include <WiFi.h>
#include <Base64.h>
#include <Arduino_JSON.h>
#include <HTTPClient.h>

//APIKEY
const char *apiKey = "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";

// Configuración de la red Wi-Fi
const char *ssid = "Sophia 2.4";
const char *password = "Perrito123";

//Variables de apoyo
bool flag = false;
unsigned long startTime;
unsigned long endTime;

// Definir la configuración de la cámara ESP32-CAM
camera_config_t config;

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
  config.jpeg_quality = 10;  // Calidad de imagen
  config.fb_count = 1;       // Usar solo un frame buffer para evitar problemas de memoria

  // Inicializar la cámara
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error al inicializar la cámara: 0x%x\n", err);
    return;
  }

  Serial.println("Cámara inicializada correctamente");

  // Conexión a la red Wi-Fi
  Serial.print("Conectando a Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado a Wi-Fi");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// Esta función toma una imagen y la convierte en base64 para su integración con OpenAI
void faceDetection() {
  camera_fb_t *fb = esp_camera_fb_get();  // Obtener la imagen de la cámara

  if (!fb) {
    Serial.println("Error al capturar la imagen");
    return;  // No continuamos si la captura falló
  }

  // Se codifica la imagen en base64
  String base64Image = base64::encode((const uint8_t *)fb->buf, fb->len);

  Serial.println(base64Image);

  // Se libera la memoria de la imagen
  esp_camera_fb_return(fb);

  //Se envía la imagen a OpenAI para la detección facial
  String result;

  String data = "data:image/jpeg;base64," + base64Image;

  //Se arma el request para OpenAI
  String payload = "{"
                   "\"model\": \"gpt-4o-mini\","
                   "\"messages\": ["
                   "{"
                   "\"role\": \"user\","
                   "\"content\": \"If you detect a face or person in this photo, respond with 'true'. Otherwise reply with 'false'.\""
                   "},"
                   "{"
                   "\"role\": \"user\","
                   "\"content\": \"data:image/jpeg;base64,"
                   + base64Image + "\""
                                   "}"
                                   "]"
                                   "}";

  //Ahora se envía a OpenAI el payload con un cliente HTTP
  HTTPClient http;
  http.begin("https://api.openai.com/v1/chat/completions");

  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + apiKey);
  http.setTimeout(20000);

  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0) {
    result = http.getString();
    http.end();
  } else {
    result = "HTTP request failed, response code: " + String(httpResponseCode);
    Serial.println("Error Code: " + String(httpResponseCode));
    Serial.println("Error Message: " + http.errorToString(httpResponseCode));
    http.end();
  }

  JSONVar doc = JSON.parse(result);

  // Verificar si hubo un error al parsear el JSON
  if (JSON.typeof(doc) == "undefined") {
    Serial.println("Error al parsear el JSON");
    return;
  }

  // Acceder al valor de 'content' en el JSON
  const char *content = doc["choices"][0]["message"]["content"];

  // Verificar el valor de "content" y asignarlo a la variable booleana
  if (content != nullptr && strcmp(content, "true") == 0) {
    Serial.println("Cara detectada");
  } else {
    Serial.println("Cara no detectada");
  }

  
}

void loop() {
  //Rutina de inicio de dispositivo
  //Busca una cara en el feed de la camara pasando los datos a OpenAI

  while (!flag) {
    startTime = millis();
    faceDetection();
    endTime = millis();  // Obtener el tiempo después de ejecutar la función

    // Calcular el tiempo que se tardó en milisegundos
    unsigned long duration = endTime - startTime;

    // Imprimir el tiempo que tardó la función
    Serial.print("Tiempo de ejecución de la función: ");
    Serial.print(duration);
    Serial.println(" milisegundos.");
  }
}
