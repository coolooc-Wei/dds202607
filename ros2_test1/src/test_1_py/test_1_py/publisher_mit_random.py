import rclpy
from rclpy.node import Node

import random
from nav_msgs.msg import Odometry

x = 0
y = 0 
z = 0

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('random_publisher')
        self.publisher_ = self.create_publisher(Odometry, 'odom', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):

        global x
        global y
        global z
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.child_frame_id = 'base_link'
        x=msg.pose.pose.position.x = x+random.uniform(0.0, 0.2)
        y=msg.pose.pose.position.y = y+random.uniform(0.0, 0.2)
        z=msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.x = 0.0
        msg.pose.pose.orientation.y = 0.0
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg)
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()