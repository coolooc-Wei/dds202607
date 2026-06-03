from pathORAM_test import ORAM
import numpy as np
import random
import time

random.seed(time.time())  # set seed for reproducibility


def simulate_oram_operations(num_operations, num_ros_nodes, target_ros_node, ramdom_fake_com_ratio=0.0):
    oram = ORAM(num_ros_nodes, DEBUG_MODE=False, PATH_DEBUG=False)
    res = []
    count_random = 0
    for _ in range(num_operations):
        path = oram.get_path_from_ros_node(target_ros_node)
        # print(f"{path = }")
        path_1, path_2 = oram.random_choose_two_path(target_ros_node)
        # print(f"{path_1 = }, {path_2 = }")
        if random.random() < ramdom_fake_com_ratio:
            # print("random")
            count_random += 1
            path_1 = random.choice(oram.path_list)
            path_2 = random.choice(oram.path_list)
            while path_2 == path_1:
                path_2 = random.choice(oram.path_list)

        ros_nodes = oram.get_ros_node_from_path(path_1, path_2)
        # print(f"{ros_nodes = }")
        oram.shuffle_path(ros_nodes)
        # print('-' * 20)

        tmp = [0 for _ in range(num_ros_nodes)]
        for i in ros_nodes:
            tmp[i] = 1
        res.append(tmp)

    # print(f"{count_random = }")

    return res


if __name__ == "__main__":

    node_num = 8
    rounds = 700

    oram_list = []
    oram_num_list = []

    for i in range(node_num):
        oram_list.append(ORAM(node_num - 1, DEBUG_MODE=False, PATH_DEBUG=False))
        oram_num_list.append(i)

    target_num = 0
    train_x_set = []
    train_y_set = []
    val_x_set = []
    val_y_set = []
    test_x_set = []
    test_y_set = []
    sim_tmp = []
    gt_tmp = []
    for round_num in range(rounds):
        if round_num % (rounds // (node_num - 1)) == 0:
            if target_num!=0:
                # shuffle sim_tmp and gt_tmp together
                combined = list(zip(sim_tmp, gt_tmp))
                random.shuffle(combined)
                sim_tmp[:], gt_tmp[:] = zip(*combined)
                train_x_set.extend(sim_tmp[:int(0.8*len(sim_tmp))])
                train_y_set.extend(gt_tmp[:int(0.8*len(gt_tmp))])
                val_x_set.extend(sim_tmp[int(0.8*len(sim_tmp)):int(0.9*len(sim_tmp))])
                val_y_set.extend(gt_tmp[int(0.8*len(gt_tmp)):int(0.9*len(gt_tmp))])
                test_x_set.extend(sim_tmp[int(0.9*len(sim_tmp)):])
                test_y_set.extend(gt_tmp[int(0.9*len(gt_tmp)):])

                sim_tmp = []
                gt_tmp = []
            target_num += 1
        target_node = random.randint(0, node_num - 1)  # choose a target
        print(f"{target_node = }, {target_num = }")
        random.shuffle(oram_num_list)
        for i in range(target_num):
            if oram_num_list[i] == target_node:  # target can't send data to itself
                # swap i and target_num-1
                oram_num_list[i], oram_num_list[target_num] = oram_num_list[target_num], oram_num_list[i]
        print(f"{oram_num_list[:target_num] = }")
        res = []
        for num in range(node_num):
            tmp = [0] * node_num
            if num in oram_num_list[:target_num]:
                oram = oram_list[num]
                path_1, path_2 = oram.random_choose_two_path(target_node if target_node <= num else target_node - 1) # if target_node > num, the target node will be num-1 in the oram with num nodes
                choose_nodes = oram.get_ros_node_from_path(path_1, path_2)
                oram.shuffle_path(choose_nodes)
                for node in choose_nodes:
                    if node >= num:
                        node += 1
                    tmp[node] = 1
            res.append(tmp)
        print(f"{res = }")
        sim_tmp.append(res)
        gt_tmp.append(target_node)

    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_train_x.npy", np.array(train_x_set))
    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_train_y.npy", np.array(train_y_set))
    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_val_x.npy", np.array(val_x_set))
    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_val_y.npy", np.array(val_y_set))
    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_test_x.npy", np.array(test_x_set))
    np.save(f"sim_datas/oram_simulation_data_{node_num}_{rounds}_test_y.npy", np.array(test_y_set))