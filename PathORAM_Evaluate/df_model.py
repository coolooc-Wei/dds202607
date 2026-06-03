import torch
import torch.nn as nn
import torch.optim as optim


class DeepFingerprinting(nn.Module):
    def __init__(self, node_num=8, times_each_round=100):
        super(DeepFingerprinting, self).__init__()
        
        self.times_each_round = times_each_round
        in_channels = node_num * node_num

        # === Block 1 ===
        # 預期輸入 X 的原始形狀: (Batch, 100, 8, 8)
        # 在 forward 中我們會將其重塑(reshape)為: (Batch, 64, 100)
        # 因此進來的 in_channels = 64，時間序列長度 = 100
        self.block1 = nn.Sequential(
            nn.Conv1d(in_channels=in_channels, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 100 -> 50
        )

        # === Block 2 ===
        self.block2 = nn.Sequential(
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 50 -> 25
        )

        # === Block 3 ===
        self.block3 = nn.Sequential(
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 25 -> 12 (無條件捨去)
        )

        # === Block 4 ===
        self.block4 = nn.Sequential(
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            # 全局最大池化，強制將剩餘的時間序列壓縮為 1，輸出形狀 (Batch, 256, 1)
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

            # 輸出層：分類 8 個目標節點
            nn.Linear(512, node_num)
        )

    def forward(self, x):
        # 1. 處理輸入資料維度
        # x 剛進來的形狀: (Batch, 100, 8, 8)
        batch_size = x.size(0)

        # 2. 將 8x8 攤平成 64 維，形狀變成: (Batch, 100, 64)
        x = x.view(batch_size, self.times_each_round, -1)

        # 3. 轉置維度以符合 Conv1d 的要求 (Batch, Channels, Length) -> (Batch, 64, 100)
        x = x.transpose(1, 2)

        # 4. 餵入卷積與全連接層
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.fc(x)
        return x


# ==========================================
# 測試與驗證模型
# ==========================================
if __name__ == "__main__":
    # 初始化模型，預測 8 個類別
    model = DeepFingerprinting(num_classes=8)
    print(model)

    # 模擬生成新版模擬資料的 Shape
    # Batch Size = 32, 時間序列長度 (rounds/times) = 100, 發送端 = 8, 接收端 = 8
    dummy_input = torch.randn(32, 100, 8, 8)

    # 將資料丟入模型測試
    output = model(dummy_input)

    print(f"\n輸入形狀: {dummy_input.shape}")
    print(f"輸出形狀: {output.shape} (Batch Size, 類別數量)")

    # 設定 Loss 函數與優化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adamax(model.parameters(), lr=0.002)