import rclpy
import random
from sros_package.publisher_ORAM import ORAM_Node
from sros_package.kyber_client import kyber_client

def main():
    rclpy.init(args=None)
    kyber_client('bot1_kyber','kyber_keys/bot1_client.key')

    topic_list = ["bot1_topic","bot2_topic","bot3_topic"]
    key_path_dict = "kyber_keys/bot1_client.key"
    oram_node = ORAM_Node(topic_list, key_path_dict, target="bot1_topic")

    for i in range(10):
        data = f"hello {i}"
        print(f"sending {data}")
        oram_node.send_data(data)

if __name__ == "__main__":
    main()