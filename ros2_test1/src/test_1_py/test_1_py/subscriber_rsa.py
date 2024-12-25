import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import rsa

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.private_key = self.load_private_key()
        self.subscription = self.create_subscription(
            String,
            'topic_rsa',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def load_private_key(self):
        with open('rsa_datas/private.pem', mode='rb') as privatefile:
            keydata = privatefile.read()
        private_key = rsa.PrivateKey.load_pkcs1(keydata)
        return private_key

    def listener_callback(self, msg):
        try:
            msg.data = bytes.fromhex(msg.data)
            msg.data = rsa.decrypt(msg.data, self.private_key).decode()
            self.get_logger().info(f"I heard: {msg.data}")
        except rsa.DecryptionError:
            self.get_logger().warning("DecryptionError")


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