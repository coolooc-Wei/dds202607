import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Queue
from nav_msgs.msg import Odometry
import pickle
import base64
from sros_package.AES_tools import AES_tools


class AES_publisher(Node):

    def __init__(self, topic_name: str, queue: Queue):
        super().__init__(topic_name + '_publisher')
        self.publisher_ = self.create_publisher(String, topic_name, 10)
        self.queue = queue
        self.timer_period = 0.5  # seconds
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    def timer_callback(self):
        if self.queue.empty():
            return
        msg = String()
        msg.data = self.queue.get()
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")


class AES_subscriber(Node):

    def __init__(self, topic_name: str, key_path: str):
        super().__init__(topic_name + '_subscriber')
        self.aes = AES_tools(key_path)
        self.subscription = self.create_subscription(String,topic_name,self.listener_callback,10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        try:
            res_data = self.aes.decrypt_obj_gcm(msg.data)
            print(res_data)
        except Exception as e:
            self.get_logger().warning(f"DecryptionError: {e}")
