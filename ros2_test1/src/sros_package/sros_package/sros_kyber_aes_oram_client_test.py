import rclpy
import random
from sros_package.publisher_ORAM import ORAM_Node
from sros_package.kyber_client import kyber_client
from multiprocessing import Process,pool,Queue
import time


def main(args=None):
    p = Process(target=kyber_client,args=("bot1_kyber","kyber_keys/bot1_client.key"))
    p.start()
    p.join()

    topic_list = ["bot1_topic","bot2_topic","bot3_topic"]
    key_path_dict = "kyber_keys/bot1_client.key"
    oram_node = ORAM_Node(topic_list, key_path_dict, target="bot1_topic")

    time.sleep(5)

    for i in range(10):
        data = f"hello {i}"
        oram_node.send_data(data)

if __name__ == "__main__":
    main()