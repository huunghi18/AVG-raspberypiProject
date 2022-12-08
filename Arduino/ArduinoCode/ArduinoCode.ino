#if (ARDUINO >= 100)
#include <Arduino.h>
#else
#include <WProgram.h>
#endif
#include <ros.h>
#include <std_msgs/String.h>
#include <geometry_msgs/Vector3Stamped.h>
#include <geometry_msgs/Twist.h>
#include <ros/time.h>
ros::NodeHandle nh;
int a,b,c,d,e,g;
float m,n;
float demandx; // van toc tu teleop.key
float demandz;

float demand1; // van toc yeu cau cua moi banh xe
float demand2;

unsigned long currentMillis;
unsigned long previousMillis;

#define encoder1 2
#define encoder2 3

// KHAI BAO SAI SO 
volatile long encoder1Pos = 0;
volatile long encoder2Pos = 0;

volatile long encoder1Prev = 0;
volatile long encoder2Prev = 0;

volatile long encoder1Diff = 0;
volatile long encoder2Diff = 0;

volatile long encoder1Error = 0;
volatile long encoder2Error = 0;

double speed_act_left = 0.00;
double speed_act_right = 0.00;
void velCallback( const geometry_msgs::Twist & vel)
{
  demandx = vel.linear.x;
  demandz = vel.angular.z;

  }  
ros::Subscriber<geometry_msgs::Twist> sub("cmd_vel" , velCallback);
std_msgs::String str_msg;  
geometry_msgs::Vector3Stamped speed_msg;
ros::Publisher speed_pub("speed",&speed_msg);
ros::Publisher sensor("sensor", &str_msg);
void setup()
{
  nh.initNode();
  nh.subscribe(sub);
  nh.advertise(speed_pub);
  nh.advertise(sensor);
  Serial.begin(57600);
  pinMode(5,OUTPUT);//PWM
  pinMode(10,OUTPUT);//PWM
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);// cau H dong co
  pinMode(8,OUTPUT);
  pinMode(9,OUTPUT);

  pinMode(4, OUTPUT);//hut + choi quet

  pinMode(encoder1, INPUT_PULLUP);
  pinMode(encoder2, INPUT_PULLUP);

  attachInterrupt(0,doEncoder1,RISING);
  attachInterrupt(1,doEncoder2,RISING);

  pinMode(A5, INPUT);
  pinMode(A4, INPUT);//do cao
  pinMode(A3, INPUT);
  
  pinMode(A1, INPUT);//va cham
  pinMode(13, INPUT);

  pinMode(A2, INPUT);//pin
  
  pinMode(A0, OUTPUT);//LED bao hieu
  }
void doEncoder1()
{
  if (demand1 >= 0.0)
   {encoder1Pos = encoder1Pos + 1;}
  else { encoder1Pos = encoder1Pos - 1;}
  }
void doEncoder2()
{
  if (demand2 >= 0.0)
  {encoder2Pos = encoder2Pos + 1;}
  else { encoder2Pos = encoder2Pos - 1;}
  }  
void publishSpeed(double)
{
  speed_msg.header.stamp = nh.now();
  speed_msg.vector.x = speed_act_left;
  speed_msg.vector.y = speed_act_right;
  speed_msg.vector.z = 0.01;
  speed_pub.publish(&speed_msg);
  nh.spinOnce();
  nh.loginfo("Publishing Odometry");
  }    
void loop()
{
  nh.spinOnce();
  currentMillis = millis();
  if ((currentMillis - previousMillis) >= 10)
  {
    previousMillis =  currentMillis;
    if ((abs(demandx) < 0.02) && (abs(demandz) < 0.02))
    { 
      analogWrite(4,0);
    } else {analogWrite(4,200);}
    demand1 =  demandx + (demandz*0.1);
    demand2 =  demandx - (demandz*0.1);
// tinh toan sai lech
    encoder1Diff = encoder1Pos - encoder1Prev;
    encoder2Diff = encoder2Pos - encoder2Prev;

    encoder1Prev = encoder1Pos;
    encoder2Prev = encoder2Pos;
    if (demand1 >= 0)
    {
    m = abs(demand1*330) + 97;
    speed_act_right = encoder1Diff/38.0;
    }
    else
    {
    m = abs(demand1*280) + 90;
    speed_act_right = encoder1Diff/38.0;
    }
    if (demand2 >= 0)
    {
    n = abs(demand2*460) + 120;
    speed_act_left = encoder2Diff/38.0;
    }
    else
    {
    n = abs(demand2*360) + 110;
    speed_act_left = encoder2Diff/38.0;      
    }
//    speed_act_right = encoder1Diff/38.0;
//    speed_act_left = encoder2Diff/38.0;
//chay motor

   if (demand1 < 0.0)
   {
    digitalWrite(9,HIGH);
    digitalWrite(8,LOW);
    analogWrite(10,m);
    }
   else if (demand1 > 0.0) 
    { digitalWrite(8,HIGH);
      digitalWrite(9,LOW);
      analogWrite(10,m);
    }
   else 
    { digitalWrite(8,LOW);
      digitalWrite(9,LOW);
      analogWrite(10,m);
    } 
   if (demand2 < 0.0)
   {
    digitalWrite(6,HIGH);
    digitalWrite(7,LOW);
    analogWrite(5,n);
    }
   else if (demand2 > 0.0) 
    { digitalWrite(7,HIGH);
      digitalWrite(6,LOW);
      analogWrite(5,n);
    } 
   else
    { digitalWrite(7,LOW);
      digitalWrite(6,LOW);
    }
  a = digitalRead(13);
  b = digitalRead(A1);
  c = digitalRead(A3);
  d = digitalRead(A4);
  e = digitalRead(A5);
  g = analogRead(A2);
  if (g > 600)
  {
    digitalWrite(A0,HIGH);
    }
    else   
  {
    digitalWrite(11,LOW);
    }
    if ((a!=1)&&(b!=1))
  {
    str_msg.data = "4";
    } 
    else if((a==0)&&(b==1))
    {
      str_msg.data = "3";
    }
    else if((a==1)&&(b==0))
    {
      str_msg.data = "2";
    }
    else if(c == 1)
    {
      str_msg.data = "5";
    }
     else if(d == 1)
    {
      str_msg.data = "6";
    }
     else if(e == 1)
    {
      str_msg.data = "7";
    }          
    else 
    str_msg.data = "1";
   sensor.publish( &str_msg );   
   publishSpeed(10);
   delay(1);
  }
}
