#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty

class EkfWatchdog(Node):
    def __init__(self):
        super().__init__('ekf_watchdog')


        self.global_loc_client = self.create_client(Empty, '/global_localization')

        self.global_loc_client.wait_for_service(timeout_sec=1.0)

        self.last_reset_time = self.get_clock().now().seconds_nanoseconds()[0]

    def odom_callback(self, msg):
        cov = msg.pose.covariance
        cov_xx = cov[0]
        cov_yy = cov[7]  
        cov_yaw = cov[35]

        if cov_xx > self.pos_threshold or cov_yy > self.pos_threshold or cov_yaw > self.yaw_threshold:
            now = self.get_clock().now().seconds_nanoseconds()[0]
            if now - self.last_reset_time > self.min_interval:
                self.get_logger().warn(f'EKF covariance high: xx={cov_xx:.3f}, yy={cov_yy:.3f}, yaw={cov_yaw:.3f}. Triggering global localization via AMCL.')
                req = Empty.Request()
                self.global_loc_client.call_async(req)
                self.last_reset_time = now

def main(args=None):
    rclpy.init(args=args)
    node = EkfWatchdog()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()