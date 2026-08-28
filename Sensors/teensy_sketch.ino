  #include <elapsedMillis.h>
  #include "teensy_functions.h"

  
  uint32_t LOOP_TIME = 10; //how often checks should be run
  static constexpr uint32_t HB_PERIOD_MS  = 50; //how often HB should be send
  static constexpr uint32_t HB_TIMEOUT_MS = 250; //how often controller should wait before assuming other controller is dead
  elapsedMillis sinceHbRx; //how often since last heartbeat received
  unsigned long lastSend = 0; //stores when last send occurred in milliseconds
  static const uint8_t check_array_size = 10;
  static const uint8_t pins_array_size = 4;
  uint8_t volt_total = 0;
  uint8_t  temp_total = 0;
  uint8_t volt_avg = 0;
  uint8_t temp_avg = 0;
  bool volt_error = true;
  bool temp_error = true;
  uint8_t const pins[pins_array_size] = {14, 15, 16, 41}; // 20,21 to control teensy //, A0, A1, A2, A3, 14, 15, 16, 17, 
  uint8_t temp_check_array[pins_array_size][check_array_size] = {0};
  uint8_t volt_check_array[pins_array_size][check_array_size] = {0};
  size_t const NUM_PINS = sizeof(pins);
  float const MIN_VOLT = 0.0f; //minimum acceptable voltage for machine to run
  float const MAX_VOLT = 1000.0f; //maximum acceptable voltage for machine to run
  float const MIN_TEMP = 0.0f; //minimum temperature voltage for machine to run
  float const MAX_TEMP = 100000.0f; //minimum temperature voltage for machine to run
  float const FILTER_MIN = 0.0f;
  float const FILTER_MAX = 100.0f;
  uint8_t const KILL_PIN = 6;        // choose a real pin later
  bool comms_ok = false;             // tracks if heartbeat is occurring
  static bool kill_tripped = true;      // FAIL-SAFE: start killed

void sendHeartbeat() {
  //ack always 0 for now
  String cmd = "HB," + "1" + ",0";

  uint8_t cs = verifyCheckSum(cmd);

  Serial1.print('<');
  Serial1.print(cmd);
  Serial1.print('|');
  Serial1.print(cs);
  Serial1.println('>');
  Serial1.println('\n');

  Serial.print("Sent: ");
  Serial.print('<');
  Serial.print(cmd);
  Serial.print('|');
  Serial.print(cs);
  Serial.println('>');
  Serial.println('\n');
}

void parsePacket(char *cmd, int *command_values){
  int index = 0;
  char *delim = strtok(cmd, ",");
  while(delim != NULL && index < 1){
    command_values[index] = atoi(delim);
    delim = strtok(NULL, ","); // Start where last "," found
    index++;
  }
}

bool verifyCheckSum(String cmd, int received_check_sum){
  int check_sum = 0;
  for(int i = 0; i < static_cast<int>(cmd.length()); i++){
    check_sum ^= cmd[i];
  } 
  return check_sum == received_check_sum;
}

  void setup() {
    Serial1.begin(115200);
    sinceHbRx = HB_TIMEOUT_MS+1;
    analogReadResolution(10);
    
    for (size_t i = 0; i < NUM_PINS; i++) {
      pinMode(pins[i], INPUT);
    }

    pinMode(KILL_PIN, OUTPUT);
    digitalWrite(KILL_PIN, LOW);        // LOW = KILL (recommended)
  }

  void loop() {
    if(Serial1.available() > 0){
      comms_ok = true;
      //Grab our packet
      String packet = Serial1.readStringUntil('\n');

      //Remove delimiters:
      packet.trim();
      if(packet.startsWith("<") && packet.endsWith(">")){
        packet = packet.substring(1, packet.length() - 1); // Grab packet contents minus the start/end frame characters
      }
      else{
        Serial1.println("ERROR: Invalid packet format received");
        return;
      }
      
      //Split into command and checksum
      int cmd_end = packet.indexOf("|");
      if(cmd_end == -1){
        Serial1.println("ERROR: No checksum operator detected");
        return;
      }
      String cmd = packet.substring(0, cmd_end);
      int check_sum = packet.substring(cmd_end + 1).toInt();
      if(verifyCheckSum(cmd, check_sum)){
        //Split command 
        int command_values[1];
        char cmd_buffer[cmd.length() + 1]; //For C-style string processing
        cmd.toCharArray(cmd_buffer, cmd.length() + 1); //For C-style string processing
        parsePacket(cmd_buffer, command_values);
        //uint8_t heartbeat_pin = static_cast<uint8_t>(command_values[0]);
        Serial.print("Received: ");
        Serial.print(command_values[0]);
        Serial.print("\n");

      }
      if (millis() - lastSend >= HB_PERIOD_MS) {
      lastSend = millis();
      sendHeartbeat();
      }

    }

    else if(sinceHbRx > HB_TIMEOUT_MS){
      comms_ok = false;
    }
    bool all_ok = true;
    String errorPin = "";
    for (int i = 0; i < pins_array_size; i++) {
      for(int j = 0; j < check_array_size; j++) {
        uint8_t volt_read = voltCheck(pins[i], MIN_VOLT, MAX_VOLT, FILTER_MIN, FILTER_MAX);
        volt_read += volt_check_array;
        volt_read += volt_total;
        uint8_t temp_read = tempCheck(pins[i], MIN_TEMP, MAX_TEMP, FILTER_MIN, FILTER_MAX);
        temp_check_array += temp_read;
        temp_total += temp_read;
      }
      volt_avg = volt_total/check_array_size;
      temp_avg = temp_total/check_array_size;
      if(volt_avg <= MIN_VOLT){
        Serial.println("ERROR: VOLTAGE UNDERFLOW AT PIN");
        Serial.println(pins[i]);
        volt_error = true;
      }
      if(volt_avg >= MAX_VOLT){
        Serial.println("ERROR: VOLTAGE OVERFLOW AT PIN");
        Serial.println(pins[i]);
        volt_error = true;
      }
      if(temp_avg <= MIN_TEMP){
        Serial.println("ERROR: UNDERHEAT AT PIN");
        Serial.println(pins[i]);
        volt_error = true;
      }
      if(temp_avg >= MAX_TEMP){
        Serial.println("ERROR: OVERHEAT AT PIN");
        Serial.println(pins[i]);
        volt_error = true;
      }
      for(int j = 0; j < pins_array_size; j++ ){
        volt_total = volt_total += volt_check_array[j];
        temp_total = temp_total += temp_check_array[j];
      }
      volt_avg = volt_total/pins_array_size;
      temp_avg = temp_total/pins_array_size;

      if (!volt_error || !temp_error) {
        errorPin += String(pins[i]);   
        errorPin += ",";               
      }
      all_ok = all_ok && volt_ok && temp_ok;
    }

    if (!all_ok) {
      for(int i = 0; i < errorPin.length(); i++){
        Serial.print(errorPin[i]);
      }
      kill_tripped = true;
      // for(;;){
      //   delay(2222);
      // }
    }

    // Later you’ll AND this with comms_ok from UART heartbeat
    digitalWrite(KILL_PIN, kill_tripped ? LOW : HIGH);
    delay(LOOP_TIME);
  }
