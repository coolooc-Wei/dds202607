import torch
import torch.nn as nn
import torch.optim as optim


class DeepFingerprinting(nn.Module):
    def __init__(self, num_classes=8):
        super(DeepFingerprinting, self).__init__()

        # === Block 1 ===
        # 新輸入形狀預期: (Batch, 8, 8) -> in_channels=8, 序列長度=8
        self.block1 = nn.Sequential(
            nn.Conv1d(in_channels=8, out_channels=32, kernel_size=3, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=3, padding='same'),
            nn.BatchNorm1d(32),
            nn.ELU(),
            # 因為輸入長度只有 8，我們把池化核改小 (例如 2)，否則維度會直接歸零
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 8 -> 4
        )

        # === Block 2 ===
        self.block2 = nn.Sequential(
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, padding='same'),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 4 -> 2
        )

        # === Block 3 ===
        self.block3 = nn.Sequential(
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3, padding='same'),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2, stride=2)  # 長度 2 -> 1
        )

        # === Block 4 ===
        self.block4 = nn.Sequential(
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=3, padding='same'),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            # Global Max Pooling，確保輸出序列長度固定為 1
            nn.AdaptiveMaxPool1d(1)  # 長度 1 -> 1
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

            # 輸出層：預測 8 個類別
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
    # 初始化模型 (預測 8 個類別)
    model = DeepFingerprinting(num_classes=8)
    print(model)

    # 模擬生成資料
    # Batch Size = 32, 節點通道數 = 8, 每個特徵長度 = 8
    dummy_input = torch.randn(32, 8, 8)

    # 將資料丟入模型測試
    output = model(dummy_input)

    print(f"\n輸入形狀: {dummy_input.shape}")
    print(f"輸出形狀: {output.shape} (Batch Size, 類別數量)")

    # 設定 Loss 函數與優化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adamax(model.parameters(), lr=0.002)