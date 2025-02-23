import rclpy
from rclpy.node import Node

from std_msgs.msg import String

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from nav_msgs.msg import Odometry
import pickle
from interfaces.srv import Kyber
import oqs

class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(Kyber, 'kyber')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = Kyber.Request()

    def send_request(self):

        client = oqs.KeyEncapsulation('Kyber512')
        public_key_client = client.generate_keypair()


        self.req.public_key = base64.b64encode(public_key_client).decode('utf-8')
        # self.req.public_key = "public_key"
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)

        res =  self.future.result()
        ciphertext = base64.b64decode(res.ciphertext)
        shared_secret_client = client.decap_secret(ciphertext)

        self.get_logger().info(f"Shared secret: {shared_secret_client}")
        self.get_logger().info(f'Shared secret: {base64.b64encode(shared_secret_client).decode("utf-8")}')

        f = open("kyber_keys/client/shared_secret_client.key", "bw")
        f.write(shared_secret_client)
        f.close()

        return shared_secret_client

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.private_key = self.load_private_key()
        self.subscription = self.create_subscription(
            String,
            'aes_pickle',
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
            msg.data = base64.b64decode(msg.data)
            res_data = pickle.loads(msg.data)

            self.get_logger().info(f"Received data: {res_data}")
            with open('data/odom_client.txt', 'a') as f:
                f.write(f"{res_data}\n")
        except Exception as e:
            self.get_logger().warning(f"DecryptionError: {e}")


def main(args=None):
    rclpy.init(args=args)

    minimal_client = MinimalClientAsync()

    response = minimal_client.send_request()

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()