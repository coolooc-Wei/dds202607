import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from setuptools.sandbox import save_modules
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from df_model import DeepFingerprinting
from gen_df_data import gen_data


# ==========================================
# 1. 定義自訂 Dataset 來讀取 .npy 檔案
# ==========================================
class ORAMDataset(Dataset):
    def __init__(self, x_path, y_path):
        # 載入 numpy 檔案
        self.x_data = np.load(x_path).astype(np.float32)
        self.y_data = np.load(y_path).astype(np.int64)

    def __len__(self):
        return len(self.x_data)

    def __getitem__(self, idx):
        x = torch.from_numpy(self.x_data[idx])  # 形狀: (100, 7)
        y = torch.tensor(self.y_data[idx])  # 純量

        # 關鍵：Conv1d 需要 (Channels, Length) -> 將 (100, 7) 轉成 (7, 100)
        x = x.transpose(0, 1)
        return x, y


# ==========================================
# 2. 訓練與驗證函數
# ==========================================
def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in dataloader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total
    return epoch_loss, epoch_acc


# ==========================================
# 3. 主程式
# ==========================================
if __name__ == "__main__":

    node_num = 64
    rounds = (node_num - 1) * 100  # (node_num-1) * n round,n = 10 or 100
    times_each_round = 100
    real_communication_ratio = 0.3
    dummy_trans_ratio = 0.5



    gen_data_flag = True  # False to load existing dataset, True to generate new dataset (which will overwrite existing dataset with the same name)

    USE_ORAM = True

    if USE_ORAM:
        file_name = f"oram_simulation_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_{dummy_trans_ratio}"
    else:
        file_name = f"sim_data_{node_num}_{rounds}_{times_each_round}_{real_communication_ratio}_no_oram"

    epochs = 100
    lr = 0.002

    print(f"=== 模型訓練參數 ===\n")
    print(
        f"{epochs = } \n{lr = } \n{node_num = } \n{rounds = } \n{times_each_round = } \n{real_communication_ratio = } \n{dummy_trans_ratio = }")

    print(f"use {file_name} to train model")

    print(f"\n=== 開始訓練模型: {file_name} ===")

    # 設定硬體裝置 (有 GPU 就用 GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用裝置: {device}")

    base_path = f"sim_datas/{file_name}"

    save_model_path = f"models/{file_name}_best_model.pth"

    train_x_path = f"{base_path}_train_x.npy"
    train_y_path = f"{base_path}_train_y.npy"
    val_x_path = f"{base_path}_val_x.npy"
    val_y_path = f"{base_path}_val_y.npy"
    test_x_path = f"{base_path}_test_x.npy"
    test_y_path = f"{base_path}_test_y.npy"

    if not os.path.exists(train_x_path) or not os.path.exists(train_y_path) or \
            not os.path.exists(val_x_path) or not os.path.exists(val_y_path) or \
            not os.path.exists(test_x_path) or not os.path.exists(test_y_path) or gen_data_flag:
        print("dataset not found, start to generate dataset...")
        gen_data(node_num, rounds, times_each_round, real_communication_ratio, dummy_trans_ratio,USE_ORAM)

    # 建立 Dataset 與 DataLoader
    train_dataset = ORAMDataset(train_x_path, train_y_path)
    val_dataset = ORAMDataset(val_x_path, val_y_path)
    test_dataset = ORAMDataset(test_x_path, test_y_path)

    # 訓練集要 shuffle 打亂（雖然前面 target 內打亂了，但同 target 還是連在一起，這裡再全局 shuffle 一次）
    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False, num_workers=2)

    # 初始化模型（把之前的 DeepFingerprinting 類別放同個檔案或 import 進來）
    # 這裡因為你的序列長度從 1000 縮短成 100，模型依然可以用（因為結尾有 AdaptiveMaxPool1d(1)）
    model = DeepFingerprinting(node_num=node_num, times_each_round=times_each_round).to(device)

    # 設定損失函數與優化器 (DF 原文推薦 Adamax)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adamax(model.parameters(), lr=lr, weight_decay=1e-6)

    # 開始訓練
    train_losses, train_accs = [], []
    val_losses, val_accs = [], []
    best_val_acc = 0.0

    print("開始訓練...")
    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        train_losses.append(train_loss)
        train_accs.append(train_acc)
        val_losses.append(val_loss)
        val_accs.append(val_acc)

        print(f"Epoch [{epoch + 1:02d}/{epochs}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc * 100:.2f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc * 100:.2f}%")

        # 儲存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_model_path)

    print("\n訓練結束！載入最佳權重進行測試...")
    # 載入表現最好的權重
    model.load_state_dict(torch.load(save_model_path))
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)
    print(f"== 最終測試結果 ==\nTest Loss: {test_loss:.4f} | Test Acc: {test_acc * 100:.2f}%")

    plt.figure(figsize=(12, 5))

    # 子圖 1: Loss 變化
    plt.subplot(1, 2, 1)
    plt.plot(range(1, epochs + 1), train_losses, label='Train Loss')
    plt.plot(range(1, epochs + 1), val_losses, label='Val Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Loss Trend')
    plt.legend()
    plt.grid(True)

    # 子圖 2: Accuracy 變化
    plt.subplot(1, 2, 2)
    plt.plot(range(1, epochs + 1), [acc * 100 for acc in train_accs], label='Train Acc')
    plt.plot(range(1, epochs + 1), [acc * 100 for acc in val_accs], label='Val Acc')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.title('Accuracy Trend')
    plt.legend()
    plt.grid(True)

    # 儲存趨勢圖
    chart_path = f"models/figs/{file_name}_trend_epoch_{epochs}_lr_{lr}_test_loss_{test_loss:.4f}_acc_{test_acc * 100:.2f}%.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    print(f"訓練趨勢圖已儲存至: {chart_path}")
