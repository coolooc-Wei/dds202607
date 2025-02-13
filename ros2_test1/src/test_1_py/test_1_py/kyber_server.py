import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs
import base64

class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(Kyber, 'kyber', self.kyber_server_callback)


        self.kyber_server = oqs.KeyEncapsulation('Kyber512')

    def kyber_server_callback(self, request, response):

        public_key = base64.b64decode(request.public_key)

        ciphertext, shared_secret_server = self.kyber_server.encap_secret(public_key)
        response.ciphertext = base64.b64encode(ciphertext).decode('utf-8')
        # ciphertext = "ciphertext"
        # self.get_logger().info(f'Incoming request: {request.public_key}')
        self.get_logger().info(f'Shared secret: {shared_secret_server}')
        self.get_logger().info(f'Shared secret: {base64.b64encode(shared_secret_server).decode("utf-8")}')
        f = open("kyber_keys/server/shared_secret_server.key", "bw")
        f.write(shared_secret_server)
        f.close()
        return response


def main(args=None):
    rclpy.init(args=args)

    minimal_service = MinimalService()

    rclpy.spin(minimal_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()