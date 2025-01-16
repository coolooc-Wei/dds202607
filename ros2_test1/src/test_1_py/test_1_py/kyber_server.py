import rclpy
from rclpy.node import Node
from interfaces.srv import Kyber
import oqs


class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(Kyber, 'kyber', self.kyber_server_callback)


        self.kyber_server = oqs.KeyEncapsulation('Kyber512')

    def kyber_server_callback(self, request, response):

        public_key = b''.join(request.public_key)

        response.ciphertext, shared_secret_server = self.kyber_server.encap_secret(public_key)
        # ciphertext = "ciphertext"
        self.get_logger().info(f'Incoming request: {request.public_key}')
        self.get_logger().info(f'Shared secret: {shared_secret_server}')
        print(f"{shared_secret_server = }")
        f = open("kyber_keys/shared_secret_server.txt", "bw")
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