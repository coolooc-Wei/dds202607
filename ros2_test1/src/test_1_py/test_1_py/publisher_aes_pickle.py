import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import random
from nav_msgs.msg import Odometry
import numpy as np
import pickle

from sros_package.AES_tools import AES_tools

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'aes_pickle', 10)
        timer_period = 0.5  # seconds
        self.i = 0
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.AES_tools = AES_tools('kyber_keys/server/shared_secret_server.key')


    

    def timer_callback(self):
        msg = Odometry()

        msg_str = String()
        msg_str.data = self.AES_tools.encrypt_obj_gcm(msg)

        self.publisher_.publish(msg_str)
        # self.get_logger().info('Publishing: "%s"' % quaternion)
        self.get_logger().info('Publishing: "%s"' % msg)
        self.get_logger().info('Publishing: "%s"' % msg_str)
        self.i += 1

        # with open('data/odom_server.txt', 'a') as f:
        #     f.write(f"{msg}\n")


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