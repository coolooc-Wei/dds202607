import numpy as np
from pathORAM_test import ORAM  # 匯入你寫好的核心演算法
import time
import random

random.seed(time.time())


def generate_sliding_window_dataset(total_rounds=25000, window_size=10, num_nodes=8, noise_prob=0.3, max_senders=3):
    print(f"啟動 ORAM 模擬：共 {total_rounds} 回合，8 個 Node 隨機通訊...")

    # 關閉 Debug 模式以加速生成

    orams = []
    for _ in range(num_nodes):
        orams.append(ORAM(num_nodes - 1, DEBUG_MODE=False, PATH_DEBUG=False))

    # 用來記錄完整歷史的 list
    history_observed = []
    history_true_targets = []

    # 1. 產生連續的真實網路通訊 (連續運行 total_rounds 次)
    for r in range(total_rounds):
        # 模擬多 Node 情境：每一回合的 Target 是隨機變動的
        # (如果你想模擬不平衡流量，可以在這裡用 np.random.choice 設定機率權重)
        target = np.random.randint(0, num_nodes)
        choosed_nodes = np.random.choice(num_nodes, size=np.random.randint(1, max_senders + 1), replace=False)

        # ORAM 演算法介入：選出兩條路徑
        obs_list = []
        for i in range(num_nodes):
            obs = np.zeros(num_nodes, dtype=np.int8)

            now_target = -1
            if i in choosed_nodes:
                if i == target:
                    now_target = i
                    while now_target == i:
                        now_target = np.random.randint(0, num_nodes)
                else:
                    now_target = target
            elif np.random.rand() < noise_prob:
                now_target = i
                while now_target == i:
                    now_target = np.random.randint(0, num_nodes)

            if now_target != -1:
                if now_target > i:
                    now_target -= 1
                path_1, path_2 = orams[i].random_choose_two_path(now_target)
                involved_nodes = orams[i].get_ros_node_from_path(path_1, path_2)

                for node in involved_nodes:
                    if node >= i:
                        obs[node + 1] = 1
                    else:
                        obs[node] = 1

            obs_list.append(obs)
        history_observed.append(obs_list)
        history_true_targets.append(target)

        if (r + 1) % 1000 == 0:
            print(f"已模擬 {r + 1} 回合...")

    history_observed = np.array(history_observed)
    history_true_targets = np.array(history_true_targets)

    print("\n開始進行滑動視窗 (Sliding Window) 切割...")
    X = []
    y = []

    # 2. 切割資料集：用過去 window_size 的歷史，預測最後一步的 Target
    for i in range(len(history_observed) - window_size + 1):
        window_traffic = history_observed[i: i + window_size]
        # Label 是視窗中「最後一筆」通訊的真實 Target
        current_target = history_true_targets[i + window_size - 1]

        X.append(window_traffic)
        y.append(current_target)

    X = np.array(X)
    y = np.array(y)

    print(f"資料集生成完畢！")
    print(f"X shape: {X.shape} -> (樣本數, 歷史視窗長度, 節點數)")
    print(f"y shape: {y.shape} -> (樣本數, )")

    np.save(f'sim_datas/X_oram_seq_multi_{total_rounds}_{window_size}_{num_nodes}_{noise_prob}_{max_senders}.npy', X)
    np.save(f'sim_datas/y_oram_seq_multi_{total_rounds}_{window_size}_{num_nodes}_{noise_prob}_{max_senders}.npy', y)


if __name__ == "__main__":
    generate_sliding_window_dataset(total_rounds=25000, window_size=10, num_nodes=8, noise_prob=0.3, max_senders=3)
