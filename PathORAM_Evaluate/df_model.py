import torch
import torch.nn as nn
import torch.optim as optim


class DeepFingerprinting(nn.Module):
    def __init__(self, num_classes=7):
        super(DeepFingerprinting, self).__init__()

        # === Block 1 ===
        # 輸入形狀: (Batch, 7, 1000) -> 已將 in_channels 從 8 改為 7
        self.block1 = nn.Sequential(
            nn.Conv1d(in_channels=7, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=8, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=8, stride=8)  # 1000 -> 125
        )

        # === Block 2 ===
        self.block2 = nn.Sequential(
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=8, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=8, stride=8, padding=3)  # 125 -> 16
        )

        # === Block 3 ===
        self.block3 = nn.Sequential(
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=8, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=8, stride=8, padding=3)  # 16 -> 2
        )

        # === Block 4 ===
        self.block4 = nn.Sequential(
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=8, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.AdaptiveMaxPool1d(1)  # 2 -> 1
        )

        # === 全連接層 (Classification) ===
        self.fc = nn.Sequential(
            nn.Flatten(),  # 展開後維度為 256 * 1 = 256

            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.7),

            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.5),

            # 輸出層：預測 7 個類別。
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
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
    # 初始化模型
    model = DeepFingerprinting(num_classes=7)
    print(model)

    # 模擬生成資料
    # Batch Size = 32, 通道數 (節點數) = 7, 序列長度 (Rounds) = 1000
    dummy_input = torch.randn(32, 7, 1000)

    # 將資料丟入模型測試
    output = model(dummy_input)

    print(f"\n輸入形狀: {dummy_input.shape}")
    print(f"輸出形狀: {output.shape} (Batch Size, 類別數量)")

    # 設定 Loss 函數與優化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adamax(model.parameters(), lr=0.002)