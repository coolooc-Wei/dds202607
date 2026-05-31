import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from nav_msgs.msg import Odometry
from multiprocessing import Process,pool,Queue
from sros_package.AES_tools import AES_tools
from Crypto.Random import get_random_bytes
import base64
import time
import json


class MinimalPublisher(Node):

    def __init__(self, secret_queue_1, secret_queue_2):
        super().__init__('minimal_publisher')

        self.publisher_1 = self.create_publisher(String, 'secret_share_1', 100)
        self.publisher_2 = self.create_publisher(String, 'secret_share_2', 100)

        timer_period = 0.1  # seconds

        self.timer_1 = self.create_timer(timer_period, lambda: self.timer_callback(self.publisher_1, secret_queue_1))
        self.timer_2 = self.create_timer(timer_period, lambda: self.timer_callback(self.publisher_2, secret_queue_2))

    def timer_callback(self, publisher, queue):

        if queue.empty():
            return

        msg = String()
        msg.data = queue.get()
        publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def secret_share_send(secret_queue_1, secret_queue_2):
    
    AES_tool = AES_tools('kyber_keys/shared_secret_server.key')
    id = 0
    while True:
        msg = Odometry()
        timestamp = time.time()
        msg.header.stamp.sec = int(timestamp)
        msg.header.frame_id = str(id)
        id += 1 
        encrypted_msg = AES_tool.encrypt_obj_gcm(msg)
        byte_encrypted_msg = encrypted_msg.encode('utf-8')
        '''
        use xor to split the encrypted message into two shares
        one is random bytes, the other is the xor of the encrypted message and the random bytes
        this strategy is faster than using secret sharing schemes like Shamir's Secret Sharing
        '''
        random_bytes = get_random_bytes(len(byte_encrypted_msg))
        secret_1_msg = AES_tool.byte_xor(byte_encrypted_msg, random_bytes)
        secret_1 = base64.b64encode(secret_1_msg).decode('utf-8')
        secret_2 = base64.b64encode(random_bytes).decode('utf-8')
        secret_1 = {'timestamp': timestamp, 'data': secret_1}
        secret_2 = {'timestamp': timestamp, 'data': secret_2}
        secret_queue_1.put(json.dumps(secret_1))
        secret_queue_2.put(json.dumps(secret_2))
        time.sleep(0.1)


def main(args=None):

    secret_queue_1, secret_queue_2 = Queue(), Queue()

    p = Process(target=secret_share_send, args=(secret_queue_1, secret_queue_2))
    p.start()

    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher(secret_queue_1, secret_queue_2)

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()