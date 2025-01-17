import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.private_key = self.load_private_key()
        self.subscription = self.create_subscription(
            String,
            'topic_aes',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def load_private_key(self):
        with open('kyber_keys/shared_secret_client_fail.key', mode='rb') as privatefile:
            private_key = privatefile.read()
        return private_key
    
    def aes_decrypt(self,encrypted_text, key):
        encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
        iv = encrypted_bytes[:16]  # 提取IV
        encrypted_data = encrypted_bytes[16:]  # 提取加密資料
        cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建解密對象
        decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
        return decrypted

    def listener_callback(self, msg):
        try:
            # msg.data = bytes.fromhex(msg.data)
            msg.data = self.aes_decrypt(msg.data, self.private_key)
            self.get_logger().info(f"I heard: {msg.data}")
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