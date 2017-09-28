//Motors START
//right motors
const int rightWheelEnable = 8;
const int rightWheelForward = 12;
const int rightWheelBackward = 9;
//Left motors
const int leftWheelEnable = 4;
const int leftWheelForward = 3;
const int leftWheelBackward = 2;
//Motors END

//Wheel encoders
int currentLeft;
int currentRight;
int tempLeft;
int tempRight;
int leftChanged;
int rightChanged;

//IR sensors START
const int leftForwardIR = A13;
const int leftIR = A12;
const int rightIR = A15;
const int forwardIR = A11;
const int rightForwardIR = A14;
//IR sensors END

int last1;
int last2;

int count1;
int count2;

int rightSpeed = 80;
int leftSpeed = 80;
int speedConst = 80;
int maxSpeed = 95;

int val = 0;

int sensor1;
int sensor2;
int sensor3;
int sensor4;
int sensor5;
String inString;
int inChar;

void setup() {

  currentLeft = -1;
  currentRight = -1;
  leftChanged = 0;
  rightChanged = 0;
  inChar = 48;

  pinMode(leftWheelEnable, OUTPUT);
  pinMode(leftWheelForward, OUTPUT);
  pinMode(leftWheelBackward, OUTPUT);

  pinMode(rightWheelEnable, OUTPUT);
  pinMode(rightWheelForward, OUTPUT);
  pinMode(rightWheelBackward, OUTPUT);

  digitalWrite(leftWheelEnable, 1);
  digitalWrite(rightWheelEnable, 1);
  
  pinMode(10, INPUT);     
  pinMode(6, INPUT);     
  
  Serial.begin(9600);

  driveEnable();
  driveStop();

   pinMode(LED_BUILTIN, OUTPUT);
   digitalWrite(LED_BUILTIN, LOW);
}

int turnBool = 0;
int lastChar = 48;
unsigned long beginTime = 0;

// the loop routine runs over and over again forever:
void loop() {

  
  if (Serial.available()) {
    inChar = Serial.read();
      if (inChar == 48) {
        driveStop();
      }
  }

  controlRobot();

  //read sensor Start
  sensor1 = analogRead(leftIR);
  sensor2 = analogRead(leftForwardIR);
  sensor3 = analogRead(forwardIR);
  sensor4 = analogRead(rightForwardIR);
  sensor5 = analogRead(rightIR);
  //read sensor End

  String slanje = "";
  slanje.concat(sensor1);
  slanje.concat(";");
  slanje.concat(sensor2);
  slanje.concat(";");
  slanje.concat(sensor3);
  slanje.concat(";");
  slanje.concat(sensor4);
  slanje.concat(";");
  slanje.concat(sensor5);
  slanje.concat(";");
  Serial.println(slanje);

}

void driveEnable(){
  digitalWrite(leftWheelEnable, 1);
  digitalWrite(rightWheelEnable, 1);
}

void driveStop(){
  analogWrite(leftWheelBackward, 0);
  analogWrite(rightWheelBackward, 0);
  analogWrite(leftWheelForward, 0);
  analogWrite(rightWheelForward, 0);
}

void driveForward(int driveSpeed){
  if(driveSpeed > 220){
    driveSpeed = 220;
  }
  analogWrite(leftWheelBackward, 0);
  analogWrite(rightWheelBackward, 0);
  analogWrite(leftWheelForward, driveSpeed);
  analogWrite(rightWheelForward, driveSpeed);
}

void driveForwardSep(int driveSpeedRight, int driveSpeedLeft){
  if(driveSpeedLeft > 220){
    driveSpeedLeft = speedConst;
  }
  if(driveSpeedRight > 220){
    driveSpeedRight = speedConst;
  }
  analogWrite(leftWheelBackward, 0);
  analogWrite(rightWheelBackward, 0);
  analogWrite(leftWheelForward, driveSpeedLeft);
  analogWrite(rightWheelForward, driveSpeedRight);
}

void driveBackward(int driveSpeed){
  if(driveSpeed > 220){
    driveSpeed = 220;
  }
  analogWrite(leftWheelForward, 0);
  analogWrite(rightWheelForward, 0);
  analogWrite(leftWheelBackward, driveSpeed);
  analogWrite(rightWheelBackward, driveSpeed);
}

void driveBackwardSep(int driveSpeedRight, int driveSpeedLeft){
  if(driveSpeedLeft > 220){
    driveSpeedLeft = 220;
  }
  if(driveSpeedRight > 220){
    driveSpeedRight = 220;
  }
  analogWrite(leftWheelForward, 0);
  analogWrite(rightWheelForward, 0);
  analogWrite(leftWheelBackward, driveSpeedLeft);
  analogWrite(rightWheelBackward, driveSpeedRight);
}

void driveLeft(int driveSpeedRight, int driveSpeedLeft){
  if(driveSpeedLeft > 220){
    driveSpeedLeft = 220;
  }
  if(driveSpeedRight > 220){
    driveSpeedRight = 220;
  }
  analogWrite(leftWheelForward, 0);
  analogWrite(rightWheelForward, driveSpeedRight);
  analogWrite(leftWheelBackward, 1.15*driveSpeedLeft);
  analogWrite(rightWheelBackward, 0);
}

void driveRight(int driveSpeedRight, int driveSpeedLeft){
  if(driveSpeedLeft > 220){
    driveSpeedLeft = 220;
  }
  if(driveSpeedRight > 220){
    driveSpeedRight = 220;
  }
  analogWrite(leftWheelForward, 1.15*driveSpeedLeft);
  analogWrite(rightWheelForward, 0);
  analogWrite(leftWheelBackward, 0);
  analogWrite(rightWheelBackward, driveSpeedRight);
}

void turnLeft(){
  digitalWrite(LED_BUILTIN, HIGH);
  voziNpredNazad(1);
  delay(1500);
  voziNpredNazad(3);
  delay(1000);
  driveStop();
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}

void turnRight(){
  digitalWrite(LED_BUILTIN, HIGH);
  voziNpredNazad(1);
  delay(1500);
  voziNpredNazad(7);
  delay(1000);
  driveStop();
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
}

void controlRobot() {
  switch (inChar) {
    case 49: // 1 - forward
      voziNpredNazad(1);
      break;
    case 50: // 2
      voziNpredNazad(2);
      break;
    case 51: // 3 - left
      voziNpredNazad(3);
      break;
    case 52: // 4
      voziNpredNazad(4);
      break;
    case 53: // 5 - backward
      voziNpredNazad(5);
      break;
    case 54: // 6
      voziNpredNazad(6);
      break;
    case 55: // 7 - right
      voziNpredNazad(7);
      break;
    case 56: // 8
      voziNpredNazad(8);
      break;
    case 108: // 108 turn left on junction
      turnBool = 1;
      turnLeft();
      break;
    case 114: // 114 turn right on junction
      turnBool = 1;
      turnRight();
      break;
    default:
      driveStop();
      break;
  }
  
}

void voziNpredNazad(int param){
  leftChanged = 0;
  rightChanged = 0;

  if(param == 1){ //forward
    driveForwardSep(leftSpeed, rightSpeed);  
  } else if (param == 5){ //baskward
    driveBackwardSep(leftSpeed, rightSpeed);  
  } else if (param == 3){ //left
    driveLeft(leftSpeed, rightSpeed);  
  } else if (param == 7){ //right
    driveRight(leftSpeed, rightSpeed);  
  } else if (param == 8){ //forward-left
    rightSpeed = leftSpeed * 1.75;
    driveForwardSep(leftSpeed, rightSpeed);  
  } else if (param == 2){ //forward-right
    leftSpeed = rightSpeed * 1.45;
    driveForwardSep(leftSpeed, rightSpeed);  
  } else if (param == 4){ //backward-right
    leftSpeed = rightSpeed * 1.45;
    driveBackwardSep(leftSpeed, rightSpeed);  
  } else if (param == 6){ //back-left
    rightSpeed = leftSpeed * 1.6;
    driveBackwardSep(leftSpeed, rightSpeed);  
  }  else { //default
    driveForwardSep(leftSpeed, rightSpeed);  
  }
  


  tempLeft = digitalRead(10);   // read the input pin
  tempRight = digitalRead(6);   // read the input pin

  if (tempLeft != currentLeft){
    currentLeft = tempLeft;
    leftChanged = 1;
  }
  if (tempRight != currentRight){
    currentRight = tempLeft;
    rightChanged = 1;
  }
  

  if (leftChanged == rightChanged){
    return;
  }

  if (leftChanged == 0){ //left wheel is slower then right
    if( rightSpeed >= leftSpeed){
      if( rightSpeed >= maxSpeed ){
        rightSpeed = speedConst;
        leftSpeed = speedConst;
      }else{
        leftSpeed++;
      }
    }
  }
  if (rightChanged == 0){ //right wheel is slower then left
    if( leftSpeed >= rightSpeed){
      if( leftSpeed >= maxSpeed ){
        rightSpeed = speedConst;
        leftSpeed = speedConst;
      }else{
        rightSpeed++;
      }
    }
  }
}
