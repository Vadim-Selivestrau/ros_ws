import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoyHandler(Node):
    def __init__(self):
        super().__init__('joy_handler')
        self.sub = self.create_subscription(
            Joy, 
            '/joy', 
            self.joy_callback, 
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.cur_twist = Twist()

        self.speed = 0.0
        self.min_speed = -1.0
        self.max_speed = 1.0


    def joy_callback(self, msg: Joy):
        """эта функция считывает кнопки с dualsense 
        и задаёт линейную и угловую скорость"""
        R2 = msg.axes[5]   # 1..-1
        L2 = msg.axes[2]   # 1..-1

        forward = (1 - R2) / 2   # 0..1
        back = (1 - L2) / 2      # 0..1

        accel = forward - back   # -1..1

        accel_rate = 0.009        
        brake_rate = 0.07       

        if accel > 0.0:
            self.speed += accel * accel_rate # V += 0..0.009
        elif accel < 0.0:
            self.speed += accel * accel_rate # V += -0.009..0
        else:
            if self.speed > 0.0:
                self.speed -= brake_rate # V -= 0.07
                if self.speed < 0.0:
                    self.speed = 0.0
            elif self.speed < 0.0:
                self.speed += brake_rate # V += 0.07
                if self.speed > 0.0:
                    self.speed = 0.0


        # ROTATE
        turn_speed = 0.0 
        turn_rate = 0.5 
        if msg.buttons[4] == 1: 
            turn_speed = turn_rate 
        elif msg.buttons[5] == 1: 
            turn_speed = -turn_rate 
        else:
            turn_speed = 0.0    

        

        self.cur_twist.angular.z = turn_speed
        self.cur_twist.linear.x = self.speed

        self.cmd_pub.publish(self.cur_twist)

def main():
    rclpy.init()
    node = JoyHandler()
    rclpy.spin(node)



if __name__ == '__main__':
    main()