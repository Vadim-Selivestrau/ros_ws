from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty


class LocalizationManager(Node):
    def __init__(self):
        super().__init__('localization_manager')
        

        self.declare_parameter('amcl_threshold', 0.4)
        
        self.create_timer(0.5, self.check_state)

        self.state = 'INIT' # MAPPING LOCALIZATION LOCALIZED
        self.cov_sum = float('inf')
        self.start_time = None
        self.timeout = 20.0 
        self.amcl_threshold = self.get_parameter('amcl_threshold').value
        self.global_local = self.create_client(Empty, '/reintialize_global_localization')


        self.amcl_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            10
        )

        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def check_state(self):
        self.get_logger().info('мы в чек стейте')

        if self.state == 'INIT':
            self.get_logger().info('мы в ините')
            self.start_localization()
        elif self.state == 'LOCALIZATION':
            self.get_logger().info('мы локализуемся')
            if self.start_time is None: return
            now = self.get_clock().now().seconds_nanoseconds()[0]
            self.get_logger().info(f'{now}\t{self.start_time}\t{self.cov_sum}\t{self.amcl_threshold}')
            if now - self.start_time > self.timeout:
                self.get_logger().info('мы в маппинге')
                self.stop_rotation()
                self.state = 'MAPPING'
                self.mapping()
            elif self.cov_sum < self.amcl_threshold:
                self.get_logger().info('мы локализованы')
                self.stop_rotation()
                self.state = 'LOCALIZED'
                self.localization()

    def stop_rotation(self):
        twist = Twist()
        twist.angular.z = 0.0
        self.cmd_pub.publish(twist)


    def start_localization(self):
        self.state = 'LOCALIZATION'
        self.start_time = self.get_clock().now().seconds_nanoseconds()[0]
        
        self.cli = self.create_client(Empty, '/reinitialize_global_localization')
        
        req = Empty.Request()

        
        # while not self.global_local.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('Waiting for /global_localization...')
        
        self.future = self.cli.call_async(req)
        self.get_logger().info('Called /global_localization')

        twist = Twist()
        twist.angular.z = 0.66
        self.cmd_pub.publish(twist)

            
    def localization(self):
        pass
    

    def mapping(self):
        pass


    def amcl_callback(self, msg):
        self.cov_sum = msg.pose.covariance[0] + msg.pose.covariance[7] + msg.pose.covariance[35] # x, y, yaw
        



def main(args=None):
    rclpy.init(args=args)
    node = LocalizationManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()