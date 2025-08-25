import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64


class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic_aes', 10)
        timer_period = 0.5  # seconds
        self.i = 0
        self.public_key = self.load_public_key()
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def load_public_key(self):
        with open('kyber_keys/shared_secret_server.key', mode='rb') as publicfile:
            public_key = publicfile.read()
        return public_key
    
    def aes_encrypt(self,plain_text, key):
        iv = get_random_bytes(16)  # 生成隨機初始化向量
        cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建加密對象
        encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
        return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）

    def timer_callback(self):
        msg = String()
        msg.data = f"Hello World: {self.i}" 
        msg.data = self.aes_encrypt(msg.data, self.public_key)
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