import sys
import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs
import base64
from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(Kyber, 'kyber')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = Kyber.Request()

    def send_request(self, kyber_public_key):
        self.req.public_key = base64.b64encode(kyber_public_key).decode('utf-8')
        # self.req.public_key = "public_key"
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()

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
        with open('kyber_keys/client/shared_secret_client.key', mode='rb') as privatefile:
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

    minimal_client = MinimalClientAsync()

    client = oqs.KeyEncapsulation('Kyber512')
    public_key_client = client.generate_keypair()

    response = minimal_client.send_request(public_key_client)

    ciphertext = base64.b64decode(response.ciphertext)
    shared_secret_client = client.decap_secret(ciphertext)
    # shared_secret_client = response.ciphertext
    minimal_client.get_logger().info(f"Shared secret: {shared_secret_client}")
    minimal_client.get_logger().info(f'Shared secret: {base64.b64encode(shared_secret_client).decode("utf-8")}')
    # print(f"{shared_secret_client =}")

    f = open("kyber_keys/client/shared_secret_client.key", "bw")
    f.write(shared_secret_client)
    f.close()

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    minimal_client.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':
    main()