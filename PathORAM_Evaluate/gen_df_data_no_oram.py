from pathORAM_test import ORAM
import numpy as np


if __name__ == "__main__":

    for ratio in range(6):
        num_op = 100
        num_data_per_target = 1000
        file_name = f"sim_datas/oram_simulation_data_{num_op}_{num_data_per_target}_no_oram"

        sim_data = []
        sim_labels = []
        for tar in range(7):
            sim_data_tmp = []
            sim_labels_tmp = []
            for _ in range(num_data_per_target):
                tmp = [0]*7
                tmp[tar] = 1
                sim_res = [tmp]*num_op
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

        np.save(f"{file_name}_train_x.npy", train_set_x)
        np.save(f"{file_name}_train_y.npy", train_set_y)
        np.save(f"{file_name}_val_x.npy", val_set_x)
        np.save(f"{file_name}_val_y.npy", val_set_y)
        np.save(f"{file_name}_test_x.npy", test_set_x)
        np.save(f"{file_name}_test_y.npy", test_set_y)
