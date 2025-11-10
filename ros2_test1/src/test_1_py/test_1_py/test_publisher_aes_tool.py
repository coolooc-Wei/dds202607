import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from nav_msgs.msg import Odometry
from sros_package.AES_tools import AES_tools


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0
        self.AES_tools = AES_tools('kyber_keys/server/shared_secret_server_0.key')

    def timer_callback(self):

        tmp_msg = Odometry()
        real_datas,fake_datas = self.AES_tools.encrypt_obj_gcm_multi(tmp_msg,fake_num=4)
        print(f"{real_datas = } {fake_datas = }")
        


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