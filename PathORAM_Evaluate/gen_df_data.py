from setuptools.sandbox import save_path

from pathORAM_test import ORAM
import numpy as np
import random
import time

random.seed(time.time())


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

    for ratio in range(6):
        if ratio == 1:
            continue
        num_op = 100
        num_data_per_target = 1000
        random_fake_com_ratio = 1/ratio if ratio != 0 else 0.0
        file_name = f"sim_datas/oram_simulation_data_{num_op}_{random_fake_com_ratio : <.2f}_{num_data_per_target}"

        sim_data = []
        sim_labels = []
        for tar in range(7):
            sim_data_tmp = []
            sim_labels_tmp = []
            for _ in range(num_data_per_target):
                sim_res = simulate_oram_operations(num_op, 7, tar, random_fake_com_ratio)
                # print(sim_res)
                sim_data_tmp.append(sim_res)
            sim_labels_tmp = [tar] * num_data_per_target
            sim_data.append(sim_data_tmp)
            sim_labels.append(sim_labels_tmp)
        sim_data = np.array(sim_data)  # Shape: (7, 1000, 7)
        sim_labels = np.array(sim_labels)  # Shape: (7, 1000)

        sim_data = np.array(sim_data)
        sim_labels = np.array(sim_labels)

        num_targets = sim_data.shape[0]  # 7
        num_experiments = sim_data.shape[1]  # 1000
        num_ops = sim_data.shape[2]  # 100
        num_nodes = sim_data.shape[3]  # 7

        # 計算 8:1:1 的切分點索引 (以 1000 筆實驗為基準)
        train_end = int(num_experiments * 0.8)  # 800
        val_end = train_end + int(num_experiments * 0.1)  # 900

        train_x, train_y = [], []
        val_x, val_y = [], []
        test_x, test_y = [], []

        for i in range(num_targets):
            target_x = sim_data[i]  # 形狀 (1000, 7)
            target_y = sim_labels[i]  # 形狀 (1000,)

            # 產生該 target 專屬的隨機索引並打亂
            shuffled_indices = np.random.permutation(num_experiments)

            # 同步打亂數據與標籤，確保對應關係正確
            target_x_shuffled = target_x[shuffled_indices]
            target_y_shuffled = target_y[shuffled_indices]

            # 各自切出 8:1:1 並放入 list
            train_x.append(target_x_shuffled[:train_end])
            train_y.append(target_y_shuffled[:train_end])

            val_x.append(target_x_shuffled[train_end:val_end])
            val_y.append(target_y_shuffled[train_end:val_end])

            test_x.append(target_x_shuffled[val_end:])
            test_y.append(target_y_shuffled[val_end:])

        # 合併所有 target 的資料
        train_set_x = np.concatenate(train_x, axis=0)
        train_set_y = np.concatenate(train_y, axis=0)

        val_set_x = np.concatenate(val_x, axis=0)
        val_set_y = np.concatenate(val_y, axis=0)

        test_set_x = np.concatenate(test_x, axis=0)
        test_set_y = np.concatenate(test_y, axis=0)

        print("\n=== 每個 Target 獨立隨機打亂後平均切分 (8:1:1) ===")
        print(f"Train set - X: {train_set_x.shape}, Y: {train_set_y.shape}")
        print(f"Val set   - X: {val_set_x.shape}, Y: {val_set_y.shape}")
        print(f"Test set  - X: {test_set_x.shape}, Y: {test_set_y.shape}")
        print(file_name)
        np.save(f"{file_name}_train_x.npy", train_set_x)
        np.save(f"{file_name}_train_y.npy", train_set_y)
        np.save(f"{file_name}_val_x.npy", val_set_x)
        np.save(f"{file_name}_val_y.npy", val_set_y)
        np.save(f"{file_name}_test_x.npy", test_set_x)
        np.save(f"{file_name}_test_y.npy", test_set_y)
