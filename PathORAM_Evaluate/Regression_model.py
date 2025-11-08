import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib  # 用於儲存和載入模型
import time


def calculate_approximate_accuracy(y_true, y_pred, tolerance):
    """
    計算在給定容忍度下的可接受準確率。
    y_true: 真實值
    y_pred: 預測值
    tolerance: 容忍的絕對誤差範圍
    """
    # 計算真實值與預測值之間的絕對差異
    absolute_errors = np.abs(y_true - y_pred)

    # 判斷哪些預測的誤差在容忍度之內 (結果為 True/False 陣列)
    correct_predictions = absolute_errors <= tolerance

    # 計算準確率 (True 會被當作 1，False 當作 0)
    accuracy = np.mean(correct_predictions)

    return accuracy


# --- 1. 載入您的數據 ---
print("正在從 .npy 檔案載入數據...")
try:
    X = np.load('datas/matrices_train_data.npy')
    y = np.load('datas/matrices_ans_data.npy')
    print(f"成功載入資料！")
    print(f"輸入資料 X 的形狀: {X.shape}")
    print(f"目標資料 y 的形狀: {y.shape}")
except FileNotFoundError:
    print("錯誤：找不到 'matrices_train_data.npy' 或 'matrices_ans_data.npy'。")
    print("請確認這兩個檔案與您的 Python 腳本在同一個資料夾中。")
    exit()

# --- 2. 資料預處理 ---
# 將 8x8 矩陣攤平成 64 維的向量
print("\n正在進行資料預處理（攤平矩陣）...")
n_samples = X.shape[0]
X_flat = X.reshape(n_samples, -1)  # -1 會自動計算為 64
y_flat = y.reshape(n_samples, -1)
print(f"攤平後的資料形狀: X_flat={X_flat.shape}, y_flat={y_flat.shape}")

# --- 3. 分割訓練集與測試集 ---
# 抽樣 20% 的數據作為測試集，以評估模型從未見過數據時的表現
X_train, X_test, y_train, y_test = train_test_split(
    X_flat, y_flat, test_size=0.2, random_state=42
)
print(f"訓練集大小: {X_train.shape[0]} 筆")
print(f"測試集大小: {X_test.shape[0]} 筆")

# --- 4. 建立與訓練模型 ---
print("\n正在建立 MLPRegressor 模型...")
# 建立模型實例
# verbose=True 會在訓練過程中印出損失函數的變化，讓你知道訓練進度
model = MLPRegressor(
    hidden_layer_sizes=(256, 128, 64),  # 兩個隱藏層，每層128個神經元
    activation='relu',
    solver='adam',
    learning_rate_init=0.0005,
    max_iter=500,
    n_iter_no_change=20,
    random_state=42,
    verbose=True,
    early_stopping=True  # 當驗證分數沒有提升時，提前停止訓練，防止過擬合
)

print("開始訓練模型... (這可能需要幾分鐘的時間)")
start_time = time.time()
model.fit(X_train, y_train)
end_time = time.time()
print(f"模型訓練完成！ 總耗時: {end_time - start_time:.2f} 秒")

# --- 5. 評估模型 ---
print("\n正在使用測試集評估模型...")
y_pred = model.predict(X_test)

# 計算各項指標
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)  # 或者使用 mean_squared_error(y_test, y_pred, squared=False)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n--- 模型效能評估指標 ---")
print(f"均方誤差 (MSE):     {mse:.6f}")
print(f"均方根誤差 (RMSE):   {rmse:.6f}  <-- (主要觀察這個)")
print(f"平均絕對誤差 (MAE): {mae:.6f}")
print(f"R 平方 (R-squared): {r2:.6f}   <-- (越高越好，滿分是 1.0)")
print("--------------------------")
# MSE 越小，代表模型的預測值與真實值的差距越小，模型越準確。
# 容忍度設為 0.1 (誤差在 ±10% 範圍內就算對)
acc_tolerance_10_percent = calculate_approximate_accuracy(y_test, y_pred, tolerance=0.1)

# 容忍度設為 0.05 (標準更嚴格，誤差在 ±5% 範圍內就算對)
acc_tolerance_05_percent = calculate_approximate_accuracy(y_test, y_pred, tolerance=0.05)


print("\n--- 可接受準確率 (自定義指標) ---")
print(f"容忍度為 0.10 時的準確率: {acc_tolerance_10_percent:.2%}")
print(f"容忍度為 0.05 時的準確率: {acc_tolerance_05_percent:.2%}")
print("---------------------------------")
print("(解讀：例如，容忍度為 0.10 的準確率達到 90%，代表模型有 90% 的預測值與真實值的差距在 0.1 以內。)")

# --- 6. 儲存訓練好的模型 ---
model_filename = './model/Regression/mlp_model_8x8.joblib'
joblib.dump(model, model_filename)
print(f"\n模型已成功儲存至 '{model_filename}'")

# --- 7. 展示單一樣本的預測結果 ---
# 示範如何載入模型並用它來預測
print("\n--- 載入模型並進行單一樣本預測 ---")
loaded_model = joblib.load(model_filename)

sample_index = 0
input_sample_flat = X_test[sample_index].reshape(1, -1)
true_output_flat = y_test[sample_index]

# 進行預測
predicted_output_flat = loaded_model.predict(input_sample_flat)

# 將結果轉換回 8x8 矩陣以便觀察
input_matrix = X_test[sample_index].reshape(8, 8)
true_output_matrix = true_output_flat.reshape(8, 8)
predicted_output_matrix = predicted_output_flat.reshape(8, 8)

# 為了方便閱讀，設定 numpy 的列印格式
np.set_printoptions(precision=4, suppress=True)

print("\n【輸入 8x8 矩陣範例】:")
print(input_matrix)

print("\n【真實輸出 (Ground Truth) 8x8 矩陣】:")
print(true_output_matrix)

print("\n【模型預測的 8x8 矩陣】:")
print(predicted_output_matrix)
