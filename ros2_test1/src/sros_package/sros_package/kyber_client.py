import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs
import base64
from std_msgs.msg import String

class KyberClient(Node):

    def __init__(self,topic_name,key_path):
        super().__init__('minimal_client_async')
        self.key_path = key_path
        self.cli = self.create_client(Kyber, topic_name)
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

        # self.get_logger().info(f"Shared secret: {shared_secret_client}")
        # self.get_logger().info(f'Shared secret: {base64.b64encode(shared_secret_client).decode("utf-8")}')

        f = open(self.key_path, "bw")
        f.write(shared_secret_client)
        f.close()

        return shared_secret_client

def kyber_client(topic_name,key_path):
    try:
        rclpy.init(args=None)
    except:
        pass
    minimal_client = KyberClient(topic_name,key_path)

    response = minimal_client.send_request()
    return response
