
#include <Arduino.h>
#include "../model_weights.h"

float relu(float x) {
  return x > 0.0f ? x : 0.0f;
}

float predictBatteryLife(const float input[5]) {
  float x[5];

  // Normalize using training-set statistics
  for (int i = 0; i < 5; i++) {
    x[i] = (input[i] - INPUT_MEAN[i]) / INPUT_STD[i];
  }

  float h1[32];
  float h2[32];

  // First hidden layer + ReLU
  for (int i = 0; i < 32; i++) {
    float sum = B1[i];

    for (int j = 0; j < 5; j++) {
      sum += W1[i][j] * x[j];
    }

    h1[i] = relu(sum);
  }

  // Second hidden layer + ReLU
  for (int i = 0; i < 32; i++) {
    float sum = B2[i];

    for (int j = 0; j < 32; j++) {
      sum += W2[i][j] * h1[j];
    }

    h2[i] = relu(sum);
  }

  // Output layer (linear)
  float output = B3[0];

  for (int j = 0; j < 32; j++) {
    output += W3[0][j] * h2[j];
  }

  // Match API's non-negative prediction clipping
  return output > 0.0f ? output : 0.0f;
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("\nESP32-S3 Battery Life Inference");
  Serial.println("Architecture: 5 -> 32 -> 32 -> 1");

  // Example reading; replace with actual sensor readings later
  const float input[5] = {
    3.8f,    // battery_v
    28.0f,   // temp_c
    8.0f,    // rings_per_day
    -65.0f,  // wifi_rssi_dbm
    18.0f    // age_months
  };

  // Warm-up
  predictBatteryLife(input);

  // Measure repeated inference for a more stable timing
  const int repetitions = 1000;

  uint32_t start = micros();

  float prediction = 0.0f;

  for (int i = 0; i < repetitions; i++) {
    prediction = predictBatteryLife(input);
  }

  uint32_t elapsed = micros() - start;

  Serial.print("Predicted battery life: ");
  Serial.print(prediction, 2);
  Serial.println(" days");

  Serial.print("Total time for 1000 inferences: ");
  Serial.print(elapsed);
  Serial.println(" microseconds");

  Serial.print("Average inference time: ");
  Serial.print((float)elapsed / repetitions, 3);
  Serial.println(" microseconds");

  Serial.println("Inference test complete.");
}

void loop() {
  delay(1000);
}
