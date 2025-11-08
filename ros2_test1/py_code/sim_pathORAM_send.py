from pathORAM_test import ORAM
import json
import os

save_files = []

for node in range(8):
    if os.path.exists(save_path := f'../multi_node_datas/topic_{node}.txt'):
        os.remove(save_path)
    save_files.append(open(save_path, 'w'))

for topic in range(8):
    with open(f'../multi_node_datas/test_data_{topic}.json') as json_file:
        data = json.load(json_file)
        ROS_node_to_ORAM_node = {}
        ORAM_node_to_ROS_node = {}
        for ORAM_node, ROS_node in enumerate(data['id_list']):
            print(ORAM_node, ROS_node)
            ROS_node_to_ORAM_node[ROS_node] = ORAM_node
            ORAM_node_to_ROS_node[ORAM_node] = ROS_node
        print(f"{ROS_node_to_ORAM_node = }")
        print(f"{ORAM_node_to_ROS_node = }")
        oram = ORAM(7)
        for t, receiver_node in enumerate(data['sends']):
            if receiver_node is None:
                continue
            print(f"{topic = }, {t = }, {receiver_node = }")
            receiver_node_ORAM_node = ROS_node_to_ORAM_node[receiver_node]
            paths = oram.random_choose_two_path(receiver_node_ORAM_node)
            nodes = oram.get_ros_node_from_path(paths[0], paths[1])
            print(nodes)
            for node in nodes:
                node = ORAM_node_to_ROS_node[node]
                msg = f"{t} {'real' if node == receiver_node else 'fake'} from {topic}"
                print(f"to topic {node} : {msg}")
                save_files[node].write(msg)
                save_files[node].write('\n')
