#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class VslamFixer(Node):
    def __init__(self):
        super().__init__('vslam_fixer')
        self.subscription = self.create_subscription(
            Odometry, '/visual_slam/tracking/odometry', self.listener_callback, 10)
        self.publisher = self.create_publisher(Odometry, '/vslam_fixer', 10)

    def listener_callback(self, msg):
        lx = msg.twist.twist.linear.x
        ly = msg.twist.twist.linear.y
        lz = msg.twist.twist.linear.z
        ax = msg.twist.twist.angular.x
        ay = msg.twist.twist.angular.y
        az = msg.twist.twist.angular.z    

        if abs(lx) > 0.7 or abs(ly) > 0.7 or abs(lz) > 0.7 or abs(ax) > 0.7 or abs(ay) > 0.7 or abs(az) > 0.7:
            return

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_footprint'
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VslamFixer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
