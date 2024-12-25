import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import rsa


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic_rsa', 10)
        timer_period = 0.5  # seconds
        self.i = 0
        self.public_key = self.load_public_key()
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def load_public_key(self):
        with open('rsa_datas/public.pem', mode='rb') as publicfile:
            keydata = publicfile.read()
        public_key = rsa.PublicKey.load_pkcs1(keydata)
        return public_key

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello World: {self.i}" 
        msg.data = rsa.encrypt(msg.data.encode(), self.public_key).hex()
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
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