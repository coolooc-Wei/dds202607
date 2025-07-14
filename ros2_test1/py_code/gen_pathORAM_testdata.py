import random
import json
import time

random.seed(time.time())

class NodeData:
    def __init__(self, node_id,id_list):

        self.node_id = node_id
        self.id_list = id_list
        self.sends = []
        print(f"{self.id_list = }")

    def random_send(self, times):
        send_list = self.id_list.copy()
        for _ in range(len(send_list)):
            send_list.append(None)
        for _ in range(times):
            r = random.randint(0, len(send_list) - 1)
            print(f"Node {self.node_id} sends to {send_list[r]}")
            self.sends.append(send_list[r])

    def save(self,path):
        data = {
            "node_id": self.node_id,
            "id_list": self.id_list,
            "sends": self.sends
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {path}")



if __name__ == "__main__":
    nodes = 8
    for node_id in range(nodes):
        id_list = [i for i in range(nodes) if i != node_id]
        node = NodeData(node_id,id_list)
        node.random_send(20000)
        node.save(f"../multi_node_datas/test_data_{node_id}.json")