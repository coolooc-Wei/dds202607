import sys
import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs


class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(Kyber, 'kyber')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = Kyber.Request()

    def send_request(self, kyber_public_key):
        self.req.public_key = kyber_public_key
        # self.req.public_key = "public_key"
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main(args=None):
    rclpy.init(args=args)

    minimal_client = MinimalClientAsync()

    client = oqs.KeyEncapsulation('Kyber512')
    public_key_client = client.generate_keypair()

    response = minimal_client.send_request(public_key_client)

    ciphertext = b''.join(response.ciphertext)
    shared_secret_client = client.decap_secret(ciphertext)
    # shared_secret_client = response.ciphertext
    minimal_client.get_logger().info(f"Shared secret: {shared_secret_client}")
    # print(f"{shared_secret_client =}")

    f = open("kyber_keys/shared_secret_client.txt", "bw")
    f.write(shared_secret_client)
    f.close()

    minimal_client.destroy_node()
    rclpy.shutdown()
    

if __name__ == '__main__':
    main()