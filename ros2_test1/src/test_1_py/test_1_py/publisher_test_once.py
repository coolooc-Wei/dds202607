import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello World once"
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)
        
        subscription_count = self.publisher_.get_subscription_count()
        self.get_logger().info(f'Matched subscriptions count: {subscription_count}')


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    minimal_publisher.timer_callback()

    # rclpy.spin_once(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()
    exit(0)


if __name__ == '__main__':
    main()