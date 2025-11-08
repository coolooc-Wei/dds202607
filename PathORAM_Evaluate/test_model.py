import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import os

# --- 1. 設定參數與檔案名稱 ---
FILE_X = 'datas/matrices_train_data.npy'
FILE_Y = 'datas/matrices_ans_data.npy'
MODEL_FILENAME = 'unet_model_on_custom_data.keras'

TEST_SPLIT_RATIO = 0.2
VAL_SPLIT_RATIO = 0.1  # 從訓練集中切分 10% 作為驗證集
RANDOM_STATE = 42
BINARY_THRESHOLD = 0.5  # 用於將您的 y 數據二值化的閾值

# --- 2. 載入並預處理您的數據 ---
print(">>> 步驟 1: 從 .npy 檔案載入數據...")
if not (os.path.exists(FILE_X) and os.path.exists(FILE_Y)):
    print(f"錯誤：找不到必要的數據檔案 '{FILE_X}' 或 '{FILE_Y}'。")
    exit()

# 載入 (20000, 8, 8) 格式的數據
X_loaded = np.load(FILE_X)
y_loaded = np.load(FILE_Y)
print(f"成功載入資料！X shape: {X_loaded.shape}, y shape: {y_loaded.shape}")

print("\n>>> 步驟 2: 預處理數據...")
# 確保數據類型為 float32，適合深度學習
X = X_loaded.astype(np.float32)
y_continuous = y_loaded.astype(np.float32)

# 將目標 y 二值化
y = (y_continuous > BINARY_THRESHOLD).astype(np.float32)
print(f"目標數據 y 已使用閾值 {BINARY_THRESHOLD} 進行二值化。")

# 為數據增加通道維度 (channels_last)，從 (20000, 8, 8) -> (20000, 8, 8, 1)
X = X[..., np.newaxis]
y = y[..., np.newaxis]
print(f"已增加通道維度: X shape={X.shape}, y shape={y.shape}")

# --- 3. 分割訓練集、驗證集與測試集 ---
print("\n>>> 步驟 3: 分割數據...")
X_train_full, X_test, y_train_full, y_test = train_test_split(
    X, y, test_size=TEST_SPLIT_RATIO, random_state=RANDOM_STATE
)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=VAL_SPLIT_RATIO, random_state=RANDOM_STATE
)
print(f"訓練集: {len(X_train)}, 驗證集: {len(X_val)}, 測試集: {len(X_test)}")


# --- 4. 建立微型 U-Net 模型 ---
def build_mini_unet(input_shape=(8, 8, 1)):
    inputs = keras.Input(shape=input_shape)
    # 編碼器
    c1 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(inputs)
    p1 = layers.MaxPooling2D((2, 2))(c1)
    # 瓶頸層
    b = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(p1)
    # 解碼器
    u1 = layers.Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(b)
    u1 = layers.concatenate([u1, c1])  # 跳躍連接
    c2 = layers.Conv2D(16, (3, 3), activation='relu', padding='same')(u1)
    # 輸出層
    outputs = layers.Conv2D(1, (1, 1), activation='sigmoid')(c2)
    model = keras.Model(inputs, outputs)
    return model


print("\n>>> 步驟 4: 建立 U-Net 模型...")
model = build_mini_unet()
model.summary()

# --- 5. 編譯與訓練模型 ---
print("\n>>> 步驟 5: 編譯與訓練模型...")
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
callbacks = [
    keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
]

if os.path.exists(MODEL_FILENAME):
    print(f"找到已訓練的模型 '{MODEL_FILENAME}'，載入權重繼續訓練。")
    model.load_weights(MODEL_FILENAME)
else:
    print("未找到模型，將從頭開始訓練。")

history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=64,
    validation_data=(X_val, y_val),
    callbacks=callbacks
)
model.save(MODEL_FILENAME)
print(f"模型已儲存至 '{MODEL_FILENAME}'")

# --- 6. 全方位評估模型 ---
print("\n" + "=" * 50)
print(">>> 步驟 6: 全方位評估模型...")
print("=" * 50)

loss, accuracy = model.evaluate(X_test, y_test)
print(f"\n測試集基礎評估:")
print(f"  損失 (Loss): {loss:.4f}")
print(f"  像素準確率 (Pixel Accuracy): {accuracy:.2%}")

y_pred_proba = model.predict(X_test)
y_pred = (y_pred_proba > 0.5).astype(np.uint8)

y_test_flat = y_test.flatten()
y_pred_flat = y_pred.flatten()

print("\n詳細分類指標 (逐像素):")
print(f"  精確率 (Precision): {precision_score(y_test_flat, y_pred_flat, zero_division=0):.2%}")
print(f"  召回率 (Recall):    {recall_score(y_test_flat, y_pred_flat, zero_division=0):.2%}")
print(f"  F1-Score:           {f1_score(y_test_flat, y_pred_flat, zero_division=0):.2%}")

# --- 7. 視覺化案例分析 ---
print("\n視覺化案例分析 (隨機選取 5 個測試樣本):")


def visualize_results(n_samples=5):
    sample_indices = np.random.choice(len(X_test), n_samples, replace=False)
    for idx in sample_indices:
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        x_plot = np.squeeze(X_test[idx])
        y_true_plot = np.squeeze(y_test[idx])
        y_pred_plot = np.squeeze(y_pred[idx])

        axes[0].imshow(x_plot, cmap='viridis')
        axes[0].set_title(f'樣本 #{idx}\n輸入矩陣');
        axes[0].axis('off')

        axes[1].imshow(y_true_plot, cmap='gray')
        axes[1].set_title('真實輸出 (Ground Truth)');
        axes[1].axis('off')

        axes[2].imshow(y_pred_plot, cmap='gray')
        axes[2].set_title('U-Net 預測輸出');
        axes[2].axis('off')

        plt.tight_layout();
        plt.show()


visualize_results()
print("\n--- 腳本執行完畢 ---")