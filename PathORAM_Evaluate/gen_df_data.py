from pathORAM_test import ORAM
import numpy as np
import random
import time
from tqdm import tqdm

random.seed(time.time())  # set seed for reproducibility

def gen_data(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio,USE_ORAM = True):

    if USE_ORAM:
        file_name = f"sim_datas/oram_simulation_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_{dummy_trans_ratio}"
    else:
        file_name = f"sim_datas/sim_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_no_oram"
        dummy_trans_ratio = 0

    target_num = 0  # n nodes to send data to the target node, from 1 to node_num-1
    train_x_set = []
    train_y_set = []
    val_x_set = []
    val_y_set = []
    test_x_set = []
    test_y_set = []
    sim_res = []
    gts = []
    for round_num in tqdm(range(rounds)):
        # if round_num % 10 == 0:
        #     print(f"round {round_num}")
        if round_num % (rounds // (node_num - 1)) == 0:
            if target_num != 0:
                # shuffle sim_res and gt_tmp together
                combined = list(zip(sim_res, gts))
                random.shuffle(combined)
                sim_res[:], gts[:] = zip(*combined)
                train_x_set.extend(sim_res[:int(0.8 * len(sim_res))])
                train_y_set.extend(gts[:int(0.8 * len(gts))])
                val_x_set.extend(sim_res[int(0.8 * len(sim_res)):int(0.9 * len(sim_res))])
                val_y_set.extend(gts[int(0.8 * len(gts)):int(0.9 * len(gts))])
                test_x_set.extend(sim_res[int(0.9 * len(sim_res)):])
                test_y_set.extend(gts[int(0.9 * len(gts)):])

                sim_res = []
                gts = []
            target_num += 1

        oram_list = []
        oram_num_list = []

        for i in range(node_num):
            oram_list.append(ORAM(node_num - 1, DEBUG_MODE=False, PATH_DEBUG=False))
            oram_num_list.append(i)

        target_node = random.randint(0, node_num - 1)  # choose a target
        # print(f"{target_node = }, {target_num = }")
        gts.append(target_node)
        sim_tmp = []
        for time in range(times_each_round):

            random.shuffle(oram_num_list)
            for i in range(target_num):
                if oram_num_list[i] == target_node:  # target can't send data to itself
                    # swap i and target_num-1
                    oram_num_list[i], oram_num_list[target_num] = oram_num_list[target_num], oram_num_list[i]
            # print(f"{oram_num_list[:target_num] = }")
            res = []
            is_real_round = (random.random() < real_communication_ratio)

            for num in range(node_num):
                tmp = [0] * node_num
                current_target = -1
                is_real_sender = (num in oram_num_list[:target_num])
                if is_real_sender and is_real_round:
                    current_target = target_node
                elif random.random() < dummy_trans_ratio:
                    if is_real_sender:
                        # if this node is a real sender, it can't send data to the target node in this round or itself
                        available_nodes = [n for n in range(node_num) if n != num and n != target_node]
                    else:
                        # if this node is not a real sender, it can send data to any node except itself
                        available_nodes = [n for n in range(node_num) if n != num]

                    current_target = random.choice(available_nodes)

                if current_target != -1:
                    if USE_ORAM:
                        oram = oram_list[num]
                        path_1, path_2 = oram.random_choose_two_path(
                            current_target if current_target <= num else current_target - 1)  # if target_node > num, the target node will be num-1 in the oram with num nodes
                        choose_nodes = oram.get_ros_node_from_path(path_1, path_2)
                        oram.shuffle_path(choose_nodes)
                        for node in choose_nodes:
                            if node >= num:
                                node += 1
                            tmp[node] = 1
                    else:
                        tmp[current_target] = 1

                res.append(tmp)
            # print(f"{res = }")
            sim_tmp.append(res)
        sim_res.append(sim_tmp)
        # print(f"{sim_tmp = }")
        # sim_res.append(sim_tmp)

    if len(sim_res) > 0:
        combined = list(zip(sim_res, gts))
        random.shuffle(combined)
        sim_res[:], gts[:] = zip(*combined)
        train_x_set.extend(sim_res[:int(0.8 * len(sim_res))])
        train_y_set.extend(gts[:int(0.8 * len(gts))])
        val_x_set.extend(sim_res[int(0.8 * len(sim_res)):int(0.9 * len(sim_res))])
        val_y_set.extend(gts[int(0.8 * len(gts)):int(0.9 * len(gts))])
        test_x_set.extend(sim_res[int(0.9 * len(sim_res)):])
        test_y_set.extend(gts[int(0.9 * len(gts)):])
    print(f"{len(train_x_set) = }")
    print(f"{len(test_x_set) = }")
    print(f"{len(val_x_set) = }")

    np.save(f"{file_name}_train_x.npy", np.array(train_x_set))
    np.save(f"{file_name}_train_y.npy", np.array(train_y_set))
    np.save(f"{file_name}_val_x.npy", np.array(val_x_set))
    np.save(f"{file_name}_val_y.npy", np.array(val_y_set))
    np.save(f"{file_name}_test_x.npy", np.array(test_x_set))
    np.save(f"{file_name}_test_y.npy", np.array(test_y_set))

if __name__ == "__main__":

    node_num = 8
    rounds = 700 # (node_num-1) * n round,n = 10 or 100
    times_each_round = 100
    real_communication_ratio = 0.3
    dummy_trans_ratio = 0.5

    gen_data(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio,USE_ORAM=False)
