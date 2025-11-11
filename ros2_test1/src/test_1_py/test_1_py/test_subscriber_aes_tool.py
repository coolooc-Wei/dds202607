import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from std_msgs.msg import String
from sros_package.AES_tools import AES_tools


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.AES_tools = AES_tools('kyber_keys/client/shared_secret_client_0.key')

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
        try:
            data = self.AES_tools.decrypt_obj_gcm(msg.data)
            self.get_logger().info(f'Decrypted data: {data} type: {type(data)}')
        except Exception as e:
            self.get_logger().warning(f"DecryptionError: {e}")


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()