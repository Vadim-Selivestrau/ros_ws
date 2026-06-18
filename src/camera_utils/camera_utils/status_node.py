#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import numpy as np

class VslamCovFilter(Node):
    def __init__(self):
        super().__init__('vslam_cov_filter')

        self.sub_odom = self.create_subscription(
            Odometry,
            '/visual_slam/tracking/odometry',
            self.odom_callback,
            10
        )

        self.pub_odom = self.create_publisher(
            Odometry,
            '/vslam/odom_for_ekf',
            10
        )

        self.last_good = None

    def odom_callback(self, msg):
        cov = np.array(msg.pose.covariance).reshape(6, 6)


        if cov[0, 0] < 0.1 and cov[1, 1] < 0.1:
            # TRACKING
            self.last_good = msg
            self.pub_odom.publish(msg)
        else:

            if self.last_good:
                self.pub_odom.publish(self.last_good)

def main():
    rclpy.init()
    node = VslamCovFilter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
