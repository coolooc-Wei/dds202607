import sys
import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs
import base64

class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(Kyber, 'kyber')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = Kyber.Request()

    def send_request(self):

        client = oqs.KeyEncapsulation('ML-KEM-1024')
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


def main(args=None):
    rclpy.init(args=args)

    minimal_client = MinimalClientAsync()
    response = minimal_client.send_request()

    minimal_client.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':
    main()