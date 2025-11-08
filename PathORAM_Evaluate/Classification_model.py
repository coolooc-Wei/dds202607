# -------------------------------------------------------------------
# MLPClassifier 完整且深入的評估腳本
# -------------------------------------------------------------------

# --- 1. 導入所需函式庫 ---
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             roc_curve, roc_auc_score)
import joblib
import time
import os

# --- 2. 設定參數與檔案名稱 ---
# (與前一版本相同)
train_data = 'datas/matrices_train_data.npy'
ans_data = 'datas/matrices_ans_data.npy'
MODEL_FILENAME = './model/Classification/mlp_classifier_model.joblib'
TEST_SPLIT_RATIO = 0.2
RANDOM_STATE = 42
BINARY_THRESHOLD = 0.5

# --- 3. 載入 & 4. 預處理 & 5. 分割數據 ---
# (與前一版本相同，此處省略以保持簡潔，請參考前一版本程式碼)
print(">>> 步驟 1-3: 載入、預處理並分割數據...")
X = np.load(train_data)
y = np.load(ans_data)
X_flat = X.reshape(X.shape[0], -1)
y_flat_binary = (y.reshape(y.shape[0], -1) > BINARY_THRESHOLD).astype(int)
X_train, X_test, y_train, y_test = train_test_split(
    X_flat, y_flat_binary, test_size=TEST_SPLIT_RATIO, random_state=RANDOM_STATE
)
print("數據準備完成！")

print(f"未找到模型，開始新的訓練...")
model = MLPClassifier(hidden_layer_sizes=(128, 128), activation='relu', solver='adam',
                      max_iter=20000, random_state=RANDOM_STATE, verbose=True,n_iter_no_change=20000 )
start_time = time.time()
model.fit(X_train, y_train)
end_time = time.time()
print(f"模型訓練完成！總耗時: {end_time - start_time:.2f} 秒")
joblib.dump(model, MODEL_FILENAME)
print(f"模型已儲存至 '{MODEL_FILENAME}'")

# --- 7. 進行預測 ---
# 獲取硬性預測 (0/1) 和軟性預測 (機率)
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)  # 用於 ROC/AUC 計算

# ###############################################################
# --- 8. 全方位深度評估 ---
# ###############################################################
print("\n" + "=" * 50)
print(">>> 步驟 5: 開始進行全方位深度評估...")
print("=" * 50)

# --- 8.1. 分類報告 (精確率、召回率、F1) ---
print("\n--- 8.1. 分類報告 (Classification Report) ---")

# 步驟 1: 單獨計算準確率
accuracy = accuracy_score(y_test, y_pred)
print(f"整體像素準確率 (Overall Accuracy): {accuracy:.2%}")  # <--- 修改後的程式碼

# 步驟 2: 產生報告字典 (用於後續的 Precision/Recall)
report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

print("\n微觀平均 (Micro Avg) - (所有像素點一視同仁):")
print(f"  精確率 (Precision): {report['micro avg']['precision']:.2f}")
print(f"  召回率 (Recall):    {report['micro avg']['recall']:.2f}")
print(f"  F1-Score:           {report['micro avg']['f1-score']:.2f}")

print("\n宏觀平均 (Macro Avg) - (公平對待每個像素分類器):")
print(f"  精確率 (Precision): {report['macro avg']['precision']:.2f}")
print(f"  召回率 (Recall):    {report['macro avg']['recall']:.2f}")
print(f"  F1-Score:           {report['macro avg']['f1-score']:.2f}")

# --- 8.2. 聚合混淆矩陣 ---
print("\n--- 8.2. 聚合混淆矩陣 (Aggregated Confusion Matrix) ---")
# 將所有 64 個像素的混淆矩陣加總
aggregated_cm = np.zeros((2, 2), dtype=int)
for i in range(y_test.shape[1]):  # y_test.shape[1] is 64
    aggregated_cm += confusion_matrix(y_test[:, i], y_pred[:, i], labels=[0, 1])

plt.figure(figsize=(6, 5))
sns.heatmap(aggregated_cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=['預測 0', '預測 1'], yticklabels=['真實 0', '真實 1'])
plt.title('所有像素的聚合混淆矩陣', fontsize=16)
plt.ylabel('真實類別', fontsize=12)
plt.xlabel('預測類別', fontsize=12)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
plt.savefig('./model/Classification/ConfusionMatrix.png')

# --- 8.3. ROC 曲線與 AUC 分數 ---
# --- 8.3. ROC 曲線與 AUC 分數 ---
print("\n--- 8.3. ROC 曲線與 AUC 分數 ---")

# y_pred_proba 是一個包含 64 個 (樣本數,) 陣列的 list，每個陣列已是類別 1 的機率。
# 我們直接使用 np.stack 將它們沿著欄（axis=1）堆疊成一個 (樣本數, 64) 的陣列。
y_pred_proba_class1 = np.stack(y_pred_proba, axis=1)

# 現在 y_pred_proba_class1 的 shape (樣本數, 64) 與 y_test 完全一致
# 可以安全地計算 ROC
fpr, tpr, _ = roc_curve(y_test.ravel(), y_pred_proba_class1.ravel())
auc_score = roc_auc_score(y_test, y_pred_proba_class1, average='micro')

# (後續的 print 和繪圖程式碼維持不變)
print(f"微觀平均 AUC 分數 (Micro-Average AUC): {auc_score:.4f}")
print("(AUC 越接近 1，代表模型區分 0 和 1 的內在能力越強)")

plt.figure(figsize=(7, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Micro-Average ROC curve (area = {auc_score:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假正率 (False Positive Rate)')
plt.ylabel('真正率 (True Positive Rate)')
plt.title('微觀平均 ROC 曲線')
plt.legend(loc="lower right")
plt.savefig('./model/Classification/ROC.png')

# --- 8.4. 視覺化案例分析 ---
print("\n--- 8.4. 視覺化案例分析 ---")


def visualize_predictions(X_data, y_true, y_pred, n_samples=5):
    sample_indices = np.random.choice(X_data.shape[0], n_samples, replace=False)

    for i, idx in enumerate(sample_indices):
        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        # 繪製輸入
        axes[0].imshow(X_data[idx].reshape(8, 8), cmap='viridis')
        axes[0].set_title(f'樣本 #{idx}\n輸入矩陣')
        axes[0].axis('off')

        # 繪製真實輸出
        axes[1].imshow(y_true[idx].reshape(8, 8), cmap='gray')
        axes[1].set_title(f'真實輸出 (Ground Truth)')
        axes[1].axis('off')

        # 繪製預測輸出
        axes[2].imshow(y_pred[idx].reshape(8, 8), cmap='gray')
        axes[2].set_title(f'模型預測')
        axes[2].axis('off')

        plt.tight_layout()
        plt.show()


# 隨機挑選幾個樣本進行視覺化
visualize_predictions(X_test, y_test, y_pred, n_samples=5)
print("\n--- 全方位評估結束 ---")
