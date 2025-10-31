import numpy as np


def saveTxtFile(filename, data):
    print(f"正在將所有資料寫入 '{filename}'...")
    with open(filename, 'w') as f:
        for i, single_matrix in enumerate(data):
            f.write(f"--- Matrix Index: {i} ---\n")
            np.savetxt(f, single_matrix, fmt='%d')
            f.write("\n\n")
    print(f"所有內容已儲存至 '{filename}'。")


# --- 您計算 matrices_zeros 的原始程式碼 ---
matrices_train = np.zeros((20000, 8, 8), dtype=int)
matrices_ans = np.zeros((20000, 8, 8), dtype=int)
# 假設您的資料檔放在跟 python 腳本同一個目錄下的 Multi_node_datas 資料夾
for t in range(8):
    file_path = f'./multi_node_datas/topic_{t}.txt'
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                tmp = line.split()
                # 確保 tmp 有足夠的元素以避免錯誤
                if len(tmp) > 1:
                    row_index = int(tmp[0])
                    # 增加一個邊界檢查，防止索引超出範圍
                    if 0 <= row_index < 20000:
                        matrices_train[row_index, t, int(tmp[-1])] = 1
                        if tmp[3] == f'{(t**2 + t + 1) % 8}':
                            matrices_ans[row_index, t, int(tmp[-1])] = 1
    except FileNotFoundError:
        print(f"警告：找不到檔案 {file_path}")

print(matrices_train[0])
print(matrices_ans[0])
exit()
# --- 程式碼結束，開始進行儲存 ---

# =================================================================
# 方法一：儲存成 .npy 檔案 (方便程式使用)
# =================================================================
# 這是最推薦的程式化儲存方式，速度快、檔案小
train_npy_filename = 'matrices_train_data.npy'
np.save(train_npy_filename, matrices_train)
ans_npy_filename = 'matrices_ans_data.npy'
np.save(ans_npy_filename, matrices_ans)
print(f"陣列已成功儲存至 '{train_npy_filename} & {ans_npy_filename}' (供程式使用)。")

train_txt_filename = 'matrices_readable_train_data.txt'
saveTxtFile(train_txt_filename, matrices_train)

ans_txt_filename = 'matrices_readable_ans_data.txt'
saveTxtFile(ans_txt_filename, matrices_ans)
