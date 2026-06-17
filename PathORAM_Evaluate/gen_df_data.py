import os
import random
import time
import shutil
import numpy as np
from multiprocessing import Pool, current_process
from tqdm import tqdm
from pathORAM_test import ORAM


# ==========================================
# 1. 子進程的資料生成核心任務 (Worker)
# ==========================================
def worker_gen_sub_data(args):
    """
    args: (target_num, rounds_per_group, node_num, times_each_round, real_communication_ratio, dummy_trans_ratio, USE_ORAM, temp_dir)
    """
    (target_num, rounds_per_group, node_num, times_each_round,
     real_communication_ratio, dummy_trans_ratio, USE_ORAM, temp_dir) = args

    # 💡 關鍵：每個子進程必須依據自己的 PID 重新初始化隨機種子，避免生成重複資料
    process_seed = int(time.time_ns() % 1e9) + os.getpid()
    random.seed(process_seed)
    np.random.seed(process_seed)

    sim_res = []
    gts = []

    target_num_tmp = target_num

    for _ in range(rounds_per_group):
        oram_list = []
        oram_num_list = []

        for i in range(node_num):
            oram_list.append(ORAM(node_num - 1, DEBUG_MODE=False, PATH_DEBUG=False))
            oram_num_list.append(i)

        target_node = random.randint(0, node_num - 1)  # 選擇目標節點
        gts.append(target_node)
        sim_tmp = []

        for _ in range(times_each_round):

            target_num = random.randint(0, node_num - 1) # for test

            # 🌟 修復 1：決定這回合的全域目標
            is_real_round = (random.random() < real_communication_ratio)
            should_dummy = (random.random() < dummy_trans_ratio)

            # if is_real_round:
            #     global_target = target_node
            # else:
            #     available_targets = [n for n in range(node_num) if n != target_node]
            #     global_target = random.choice(available_targets)

            # 🌟 修復 2：直接隨機挑選發送端 (絕對不要刻意排除 target_node)
            primary_senders = random.sample(range(node_num), target_num)

            background_traffic_ratio = 0.20

            res = []
            for num in range(node_num):
                tmp = [0] * node_num

                is_primary_sender = (num in primary_senders)
                should_send = False
                current_target = -1

                if is_primary_sender and is_real_round:

                    should_send = True

                    # 🌟 修復 3：發送端反射機制
                    # 如果我被選為發送端，但我剛好就是要接收的 global_target (不能發給自己)
                    # 我必須維持「發送量」，所以我把這發封包隨機打給別人當作 Dummy！
                    if target_node == num:
                        current_target = random.choice([n for n in range(node_num) if n != num])
                    else:
                        current_target = target_node
                elif random.random() < background_traffic_ratio or random.random() < dummy_trans_ratio:
                        should_send = True
                        current_target = random.choice([n for n in range(node_num) if n != num])

                # === ORAM 發送區塊維持原樣 ===
                if should_send:
                    if USE_ORAM:
                        oram = oram_list[num]
                        mapped_target = current_target if current_target <= num else current_target - 1
                        path_1, path_2 = oram.random_choose_two_path(mapped_target)
                        choose_nodes = oram.get_ros_node_from_path(path_1, path_2)
                        oram.shuffle_path(choose_nodes)
                        for node in choose_nodes:
                            if node >= num:
                                node += 1
                            tmp[node] = 1
                    else:
                        tmp[current_target] = 1

                res.append(tmp)
            sim_tmp.append(res)
        sim_res.append(sim_tmp)

    # 在本分組（目前這個 target_num）內部進行獨立打亂與 8:1:1 平均切分

    target_num = target_num_tmp
    if len(sim_res) > 0:
        combined = list(zip(sim_res, gts))
        random.shuffle(combined)
        sim_res[:], gts[:] = zip(*combined)

        n_total = len(sim_res)
        idx_80 = int(0.8 * n_total)
        idx_90 = int(0.9 * n_total)

        # 轉成 numpy array 後直接存到硬碟暫存區，避免跨進程的大型記憶體搬移
        np.save(os.path.join(temp_dir, f"t_{target_num}_train_x.npy"), np.array(sim_res[:idx_80]))
        np.save(os.path.join(temp_dir, f"t_{target_num}_train_y.npy", ), np.array(gts[:idx_80]))
        np.save(os.path.join(temp_dir, f"t_{target_num}_val_x.npy"), np.array(sim_res[idx_80:idx_90]))
        np.save(os.path.join(temp_dir, f"t_{target_num}_val_y.npy"), np.array(gts[idx_80:idx_90]))
        np.save(os.path.join(temp_dir, f"t_{target_num}_test_x.npy"), np.array(sim_res[idx_90:]))
        np.save(os.path.join(temp_dir, f"t_{target_num}_test_y.npy"), np.array(gts[idx_90:]))

    return target_num


# ==========================================
# 2. 主控制流程
# ==========================================
def gen_data_mp(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio, USE_ORAM=True):
    if USE_ORAM:
        file_name = f"sim_datas/oram_multi_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_{dummy_trans_ratio}"
    else:
        file_name = f"sim_datas/oram_multi_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_no_oram"
        dummy_trans_ratio = 0

    os.makedirs("sim_datas", exist_ok=True)

    # 建立多進程用的臨時暫存資料夾
    temp_dir = f"sim_datas/mp_temp_{int(time.time())}"
    os.makedirs(temp_dir, exist_ok=True)

    # 每個 target_num 分組應該分配到的回合數
    rounds_per_group = rounds // (node_num - 1)

    # 建立進程池任務參數包 (共有 node_num - 1 個分組，例如 7 個)
    tasks = []
    for target_num in range(1, node_num):
        tasks.append((
            target_num, rounds_per_group, node_num, times_each_round,
            real_communication_ratio, dummy_trans_ratio, USE_ORAM, temp_dir
        ))

    # 啟動多進程並搭配 tqdm 顯示進度條
    print(f"=== 啟動多進程平行生成資料 (共 {node_num - 1} 個子進程平行處理) ===")
    # 依你的 CPU 核心數自動調配，通常可以設為和任務數一樣 (node_num - 1)
    num_processes = min(os.cpu_count(), len(tasks))

    with Pool(processes=num_processes) as pool:
        # 使用 imap_unordered 能在子進程一完成時就回傳，方便進度條即時跳動
        for t_num in tqdm(pool.imap_unordered(worker_gen_sub_data, tasks), total=len(tasks)):
            pass

    # ==========================================
    # 3. 合併所有暫存檔並儲存最終結果
    # ==========================================
    print("\n=== 平行生成完畢，正在合併各進程資料... ===")
    train_x, train_y = [], []
    val_x, val_y = [], []
    test_x, test_y = [], []

    for target_num in range(1, node_num):
        train_x.append(np.load(os.path.join(temp_dir, f"t_{target_num}_train_x.npy")))
        train_y.append(np.load(os.path.join(temp_dir, f"t_{target_num}_train_y.npy")))
        val_x.append(np.load(os.path.join(temp_dir, f"t_{target_num}_val_x.npy")))
        val_y.append(np.load(os.path.join(temp_dir, f"t_{target_num}_val_y.npy")))
        test_x.append(np.load(os.path.join(temp_dir, f"t_{target_num}_test_x.npy")))
        test_y.append(np.load(os.path.join(temp_dir, f"t_{target_num}_test_y.npy")))

    # 執行最後的縱向拼接
    train_x_final = np.concatenate(train_x, axis=0)
    train_y_final = np.concatenate(train_y, axis=0)
    val_x_final = np.concatenate(val_x, axis=0)
    val_y_final = np.concatenate(val_y, axis=0)
    test_x_final = np.concatenate(test_x, axis=0)
    test_y_final = np.concatenate(test_y, axis=0)

    print(f"\n== 資料集最終統計 ==")
    print(f"Train_X Shape: {train_x_final.shape} | Train_Y Shape: {train_y_final.shape}")
    print(f"Val_X   Shape: {val_x_final.shape} | Val_Y   Shape: {val_y_final.shape}")
    print(f"Test_X  Shape: {test_x_final.shape} | Test_Y  Shape: {test_y_final.shape}")

    # 儲存為最終大檔
    np.save(f"{file_name}_train_x.npy", train_x_final)
    np.save(f"{file_name}_train_y.npy", train_y_final)
    np.save(f"{file_name}_val_x.npy", val_x_final)
    np.save(f"{file_name}_val_y.npy", val_y_final)
    np.save(f"{file_name}_test_x.npy", test_x_final)
    np.save(f"{file_name}_test_y.npy", test_y_final)

    # 移除暫存資料夾
    shutil.rmtree(temp_dir)
    print("暫存清除完成，全部作業結束！")


if __name__ == "__main__":
    node_num = 8
    rounds = (node_num-1)*10
    times_each_round = 10
    real_communication_ratio = 0.3
    dummy_trans_ratio = 0.5

    gen_data_mp(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio, USE_ORAM=True)