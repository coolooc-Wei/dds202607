import sys
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from multiprocessing import Process,pool,Queue
import os
import base64
import time
import json
from sros_package.AES_tools import AES_tools


class MinimalSubscriber(Node):

    def __init__(self, secret_queue_1, secret_queue_2):
        super().__init__('minimal_subscriber')
        self.subscriber_1 = self.create_subscription(
            String,
            'secret_share_1',
            lambda msg: self.listener_callback(msg, secret_queue_1),
            100)
        self.subscriber_2 = self.create_subscription(
            String,
            'secret_share_2',
            lambda msg: self.listener_callback(msg, secret_queue_2),
            100)
        self.subscriptions  # prevent unused variable warning
        
        

    def listener_callback(self, msg, queue):
        # self.get_logger().info(f'I heard: {msg.data}')
        queue.put(msg.data)


def secret_share_receive(secret_queue_1, secret_queue_2):

    combine_dict = {}
    AES_tool = AES_tools('kyber_keys/shared_secret_client.key')
    while True:
        if not secret_queue_1.empty():
            secret_1 = secret_queue_1.get()
            secret_1_dict = json.loads(secret_1)
            timestamp = secret_1_dict['timestamp']
            if timestamp not in combine_dict:
                combine_dict[timestamp] = {'secret_1': secret_1_dict['data']}
            else:
                combine_dict[timestamp]['secret_1'] = secret_1_dict['data']

        if not secret_queue_2.empty():
            secret_2 = secret_queue_2.get()
            secret_2_dict = json.loads(secret_2)
            timestamp = secret_2_dict['timestamp']
            if timestamp not in combine_dict:
                combine_dict[timestamp] = {'secret_2': secret_2_dict['data']}
            else:
                combine_dict[timestamp]['secret_2'] = secret_2_dict['data']

        for key in list(combine_dict.keys()):
            if 'secret_1' in combine_dict[key] and 'secret_2' in combine_dict[key]:
                secret_1 = base64.b64decode(combine_dict[key]['secret_1'])
                secret_2 = base64.b64decode(combine_dict[key]['secret_2'])
                byte_encrypted_msg = AES_tool.byte_xor(secret_1, secret_2)
                decrypted_msg = AES_tool.decrypt_obj_gcm(byte_encrypted_msg.decode('utf-8'))
                print(f"Decrypted message: {decrypted_msg}")
                del combine_dict[key]

    
def main(args=None):


    secret_queue_1, secret_queue_2 = Queue(), Queue()

    p = Process(target=secret_share_receive, args=(secret_queue_1, secret_queue_2))
    p.start()


    rclpy.init(args=None)
    minimal_publisher = MinimalSubscriber(secret_queue_1, secret_queue_2)
    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
