import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from setuptools.sandbox import save_modules
from torch.utils.data import Dataset, DataLoader
from df_model import DeepFingerprinting

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

    datasets = ["oram_simulation_data_100_1000_no_oram"]
    num_op = 100
    ratio_str = "0.00"
    num_data_per_target = 1000
    ratios = ["0.00","0.20","0.25","0.33","0.50"]
    for ratio in ratios:
        file_name = f"oram_simulation_data_{num_op}_{ratio}_{num_data_per_target}"

        print(f"\n=== 開始訓練模型: {file_name} ===")

        # 設定硬體裝置 (有 GPU 就用 GPU)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用裝置: {device}")

        # 填入你實際生成的檔案路徑與名稱 (這裡拿其中一個比率當範例)
        num_op = 100
        ratio_str = "0.00"
        num_data_per_target = 1000
        base_path = f"sim_datas/{file_name}"

        save_model_path = f"models/{file_name}_best_model.pth"

        train_x_path = f"{base_path}_train_x.npy"
        train_y_path = f"{base_path}_train_y.npy"
        val_x_path = f"{base_path}_val_x.npy"
        val_y_path = f"{base_path}_val_y.npy"
        test_x_path = f"{base_path}_test_x.npy"
        test_y_path = f"{base_path}_test_y.npy"

        # 檢查檔案是否存在
        if not os.path.exists(train_x_path):
            raise FileNotFoundError(f"找不到訓練檔案：{train_x_path}，請先確認生成路徑。")

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
        model = DeepFingerprinting(num_classes=7).to(device)

        # 設定損失函數與優化器 (DF 原文推薦 Adamax)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adamax(model.parameters(), lr=0.002, weight_decay=1e-6)

        # 開始訓練
        epochs = 30
        best_val_acc = 0.0

        print("開始訓練...")
        for epoch in range(epochs):
            train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
            val_loss, val_acc = evaluate(model, val_loader, criterion, device)

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