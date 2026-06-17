import numpy as np
from pathORAM_test import ORAM  # 匯入你寫好的核心演算法


def generate_sliding_window_dataset(total_rounds=25000, window_size=10, num_nodes=8):
    print(f"啟動 ORAM 模擬：共 {total_rounds} 回合，8 個 Node 隨機通訊...")

    # 關閉 Debug 模式以加速生成
    oram = ORAM(num_nodes, DEBUG_MODE=False, PATH_DEBUG=False)

    # 用來記錄完整歷史的 list
    history_observed = []
    history_true_targets = []

    # 1. 產生連續的真實網路通訊 (連續運行 total_rounds 次)
    for r in range(total_rounds):
        # 模擬多 Node 情境：每一回合的 Target 是隨機變動的
        # (如果你想模擬不平衡流量，可以在這裡用 np.random.choice 設定機率權重)
        target = np.random.randint(0, num_nodes)

        # 升級寫法（模擬真實世界的不平衡流量）：
        # 假設 Node 0 是核心節點（佔 40% 流量），Node 1 佔 20%...
        probabilities = [0.40, 0.20, 0.10, 0.10, 0.05, 0.05, 0.05, 0.05]

        # 根據我們設定的機率分佈來隨機選擇 Target
        # target = np.random.choice(num_nodes, p=probabilities)

        # ORAM 演算法介入：選出兩條路徑
        path_1, path_2 = oram.random_choose_two_path(target)
        involved_nodes = oram.get_ros_node_from_path(path_1, path_2)

        # 紀錄外部觀察者看到的封包特徵 (有亮起的 Node 設為 1)
        obs = np.zeros(num_nodes, dtype=np.int8)
        for node in involved_nodes:
            obs[node] = 1

        history_observed.append(obs)
        history_true_targets.append(target)

        if (r + 1) % 5000 == 0:
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

    np.save(f'sim_datas/X_oram_seq_{total_rounds}_{window_size}_{num_nodes}.npy', X)
    np.save(f'sim_datas/y_oram_seq_{total_rounds}_{window_size}_{num_nodes}.npy', y)
    print("已儲存為 X_oram_seq.npy 與 y_oram_seq.npy")


if __name__ == "__main__":
    generate_sliding_window_dataset(total_rounds=25000, window_size=10, num_nodes=8)