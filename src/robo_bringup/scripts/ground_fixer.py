#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import math

class WheelOdometrySmartNode(Node):
    def __init__(self):
        super().__init__('wheel_odometry_smart')
        
        # Параметры
        self.declare_parameter('vslam_topic', '/visual_slam/tracking/odometry')
        self.declare_parameter('wheel_topic', '/odom_fixed')
        self.declare_parameter('output_topic', '/odometry/wheel_corrected')
        self.declare_parameter('linear_threshold', 0.05)   
        self.declare_parameter('angular_threshold', 0.1)    
        self.declare_parameter('covariance_stopped', [1.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                                       0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
                                                       0.0, 0.0, 1.0, 0.0, 0.0, 0.0,
                                                       0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                                                       0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                                       0.0, 0.0, 0.0, 0.0, 0.0, 1.0]) 
        self.declare_parameter('covariance_moving', [0.001, 0.0, 0.0, 0.0, 0.0, 0.0,
                                                     0.0, 0.001, 0.0, 0.0, 0.0, 0.0,
                                                     0.0, 0.0, 0.001, 0.0, 0.0, 0.0,
                                                     0.0, 0.0, 0.0, 0.001, 0.0, 0.0,
                                                     0.0, 0.0, 0.0, 0.0, 0.001, 0.0,
                                                     0.0, 0.0, 0.0, 0.0, 0.0, 0.001])  
        
        self.linear_thresh = self.get_parameter('linear_threshold').value
        self.angular_thresh = self.get_parameter('angular_threshold').value
        self.cov_stopped = self.get_parameter('covariance_stopped').value
        self.cov_moving = self.get_parameter('covariance_moving').value
        
        self.robot_stopped = True  
        self.last_vslam_msg = None
        

        self.vslam_sub = self.create_subscription(Odometry, self.get_parameter('vslam_topic').value, self.vslam_callback, 10)
        self.wheel_sub = self.create_subscription(Odometry, self.get_parameter('wheel_topic').value, self.wheel_callback, 10)
        self.pub = self.create_publisher(Odometry, self.get_parameter('output_topic').value, 10)
        
        self.get_logger().info('WheelOdometrySmartNode started')
    
    def vslam_callback(self, msg: Odometry):
        """Определяем, стоит робот по VSLAM"""
        linear_speed = math.sqrt(msg.twist.twist.linear.x**2 + msg.twist.twist.linear.y**2 + msg.twist.twist.linear.z**2)
        angular_speed = abs(msg.twist.twist.angular.z)
        

        if linear_speed < self.linear_thresh and angular_speed < self.angular_thresh:
            self.robot_stopped = True
        else:
            self.robot_stopped = False
        
        self.last_vslam_msg = msg
    
    def wheel_callback(self, msg: Odometry):
        """Корректируем ковариацию в зависимости от состояния VSLAM"""

        if self.last_vslam_msg is None:
            return
        

        if self.robot_stopped:

            wheel_speed = math.sqrt(msg.twist.twist.linear.x**2 + msg.twist.twist.linear.y**2 + msg.twist.twist.linear.z**2)
            if wheel_speed > self.linear_thresh * 2: 
                self.get_logger().debug('Wheel slip detected: increasing covariance')
            

            msg.twist.covariance = self.cov_stopped
        else:
            msg.twist.covariance = self.cov_moving
        

        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = WheelOdometrySmartNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()