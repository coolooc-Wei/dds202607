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
for topic in range(8):
    file_path = f'datas/topic_{topic}.txt'
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            tmp = line.split()
            # 確保 tmp 有足夠的元素以避免錯誤
            if len(tmp) > 1:
                time = int(tmp[0])
                # 增加一個邊界檢查，防止索引超出範圍
                if 0 <= time < 20000:
                    matrices_train[time, int(tmp[-1]),topic] = 1
                    if tmp[1] == f'real':
                        matrices_ans[time, int(tmp[-1]),topic] = 1

print(matrices_train[100])
print(matrices_ans[100])
# exit()
# --- 程式碼結束，開始進行儲存 ---

# =================================================================
# 方法一：儲存成 .npy 檔案 (方便程式使用)
# =================================================================
# 這是最推薦的程式化儲存方式，速度快、檔案小
train_npy_filename = 'datas/matrices_train_data.npy'
np.save(train_npy_filename, matrices_train)
ans_npy_filename = 'datas/matrices_ans_data.npy'
np.save(ans_npy_filename, matrices_ans)
print(f"陣列已成功儲存至 '{train_npy_filename} & {ans_npy_filename}' (供程式使用)。")

train_txt_filename = 'datas/matrices_readable_train_data.txt'
saveTxtFile(train_txt_filename, matrices_train)

ans_txt_filename = 'datas/matrices_readable_ans_data.txt'
saveTxtFile(ans_txt_filename, matrices_ans)
