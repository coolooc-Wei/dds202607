import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from nav_msgs.msg import Odometry
import pickle
from sros_package.AES_tools import AES_tools

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.AES_tools = AES_tools('kyber_keys/client/shared_secret_client.key')
        self.subscription = self.create_subscription(
            String,
            'aes_pickle',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning


    def listener_callback(self, msg):
        try:
            # msg.data = bytes.fromhex(msg.data)
            msg.data = self.AES_tools.decrypt_obj_gcm(msg.data)
            self.get_logger().info(f"I heard: {msg.data}")
            res_data = pickle.loads(msg.data)

            self.get_logger().info(f"Received data: {res_data}")
            # with open('data/odom_client.txt', 'a') as f:
            #     f.write(f"{res_data}\n")
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