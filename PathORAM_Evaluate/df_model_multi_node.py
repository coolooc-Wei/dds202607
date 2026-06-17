import torch
import torch.nn as nn
import torch.optim as optim


class DeepFingerprinting(nn.Module):
    def __init__(self, node_num=8, window_size=10):
        super(DeepFingerprinting, self).__init__()

        self.window_size = window_size
        self.node_num = node_num

        # 輸入特徵通道數 (因為我們每個時間步有 8 個 Node 的特徵，所以 in_channels = node_num)
        in_channels = node_num*node_num

        # === Block 1 ===
        self.block1 = nn.Sequential(
            nn.Conv1d(in_channels=in_channels, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=2, stride=2)
        )

        # === Block 2 ===
        self.block2 = nn.Sequential(
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)
        )

        # === Block 3 ===
        self.block3 = nn.Sequential(
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)
        )

        # === Block 4 ===
        self.block4 = nn.Sequential(
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            # 全局最大池化，不管前面的 window_size 剩下多少，強制壓縮長度為 1
            nn.AdaptiveMaxPool1d(1)
        )

        # === 全連接層 (Classification) ===
        self.fc = nn.Sequential(
            nn.Flatten(),  # 展開成 (Batch, 256)

            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.7),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.5),

            # 輸出層：分類 N 個目標節點
            nn.Linear(512, node_num)
        )

    def forward(self, x):
        batch_size = x.size(0)

        # 目前 x 剛進來的形狀: (Batch, window_size, node_num, node_num)
        # 例如: (128, 10, 8, 8)

        # 2. 將每個時間步的 8x8 矩陣攤平成 64 維特徵 (node_num * node_num)
        # 形狀變成: (Batch, window_size, 64) -> (128, 10, 64)
        x = x.view(batch_size, self.window_size, -1)

        # 3. 轉置維度以符合 PyTorch Conv1d 的要求 (Batch, Channels, Length)
        # 轉置後形狀變成: (Batch, 64, window_size) -> (128, 64, 10)
        x = x.transpose(1, 2)

        # 3. 餵入卷積與全連接層
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.fc(x)
        return x


# ==========================================
# 測試與驗證模型維度
# ==========================================
if __name__ == "__main__":
    # 初始化模型，8 個類別，滑動視窗長度 10
    model = DeepFingerprinting(node_num=8, window_size=10)
    print(model)

    # 模擬 DataLoader 取出的 Batch Data
    # Batch Size = 32, Window Size = 10, Node 數 = 8
    dummy_input = torch.randn(32, 10, 8*8)
    output = model(dummy_input)

    print(f"\n輸入形狀: {dummy_input.shape} (Batch Size, Window Size, Node Num)")
    print(f"輸出形狀: {output.shape} (Batch Size, 預測類別數量)")