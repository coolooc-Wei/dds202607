import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, f1_score
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import train_test_split

# 匯入自訂的模型與生成資料函數
from df_model_multi_node import DeepFingerprinting
from gen_df_data_multi_node import generate_sliding_window_dataset


# ==========================================
# 1. 訓練與驗證函數
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


def get_test_metrics(model, dataloader, device):
    model.eval()
    all_labels = []
    all_preds = []
    all_probs = []

    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)

            # 取得各類別的預測機率 (ROC 需要)
            probs = F.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(predicted.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    return np.array(all_labels), np.array(all_preds), np.array(all_probs)


# ==========================================
# 2. 主訓練流程
# ==========================================
def train(node_num, total_rounds, window_size,noise_prob,max_senders, epochs, lr, gen_data_flag=False):
    time_str = datetime.now().strftime("%Y%m%d-%H%M")
    file_name = f"oram_seq_{total_rounds}_{window_size}_{node_num}_{noise_prob}_{max_senders}"
    folder_name = f"{time_str}_{file_name}"

    # 建立所需的資料夾
    os.makedirs(f"res/{folder_name}", exist_ok=True)
    os.makedirs("sim_datas", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    print(f"=== 模型訓練參數 ===")
    print(f"{epochs = } \n{lr = } \n{node_num = } \n{total_rounds = } \n{window_size = }")
    print(f"\n=== 開始流程: {file_name} ===")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用訓練裝置: {device}")

    x_path = f"sim_datas/X_oram_seq_multi_{total_rounds}_{window_size}_{node_num}_{noise_prob}_{max_senders}.npy"
    y_path = f"sim_datas/y_oram_seq_multi_{total_rounds}_{window_size}_{node_num}_{noise_prob}_{max_senders}.npy"
    save_model_path = f"models/{file_name}_best_model.pth"

    # 如果要求重新產生資料或找不到資料，就呼叫生成腳本
    if not os.path.exists(x_path) or not os.path.exists(y_path) or gen_data_flag:
        print("資料集不存在或要求重新生成，開始啟動 ORAM 模擬...")
        generate_sliding_window_dataset(total_rounds=total_rounds, window_size=window_size, num_nodes=node_num, noise_prob=noise_prob, max_senders=max_senders)

    # 1. 讀取 Numpy 資料
    print("正在載入與切割資料集...")
    X_data = np.load(x_path).astype(np.float32)
    y_data = np.load(y_path).astype(np.int64)

    # 2. 自動切分資料集：80% Train, 10% Val, 10% Test
    X_temp, X_test, y_temp, y_test = train_test_split(X_data, y_data, test_size=0.1, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=1 / 9,
                                                      random_state=42)  # 0.9 * (1/9) = 0.1

    print(f"資料切割完畢: 訓練集 {len(X_train)} 筆, 驗證集 {len(X_val)} 筆, 測試集 {len(X_test)} 筆")

    # 3. 建立 TensorDataset 與 DataLoader
    train_dataset = TensorDataset(torch.tensor(X_train), torch.tensor(y_train))
    val_dataset = TensorDataset(torch.tensor(X_val), torch.tensor(y_val))
    test_dataset = TensorDataset(torch.tensor(X_test), torch.tensor(y_test))

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

    # 4. 初始化模型、損失函數與優化器
    model = DeepFingerprinting(node_num=node_num, window_size=window_size).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adamax(model.parameters(), lr=lr, weight_decay=1e-6)

    train_losses, train_accs = [], []
    val_losses, val_accs = [], []
    best_val_acc = 0.0

    print("\n開始訓練 CNN 模型...")
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

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), save_model_path)

    print("\n訓練結束！載入最佳權重進行最終測試...")
    model.load_state_dict(torch.load(save_model_path))
    test_loss, test_acc = evaluate(model, test_loader, criterion, device)

    y_true, y_pred, y_probs = get_test_metrics(model, test_loader, device)
    macro_f1 = f1_score(y_true, y_pred, average='macro')

    print(f"\n==============================================")
    print(f"== 最終深度學習攻擊測試結果 ==")
    print(f"Test Loss: {test_loss:.4f} | Test Acc: {test_acc * 100:.2f}% | Macro F1: {macro_f1:.4f}")
    print(f"==============================================\n")

    with open(f"res/{folder_name}/{file_name}_test_metrics.txt", "w") as f:
        f.write(f"Test Loss: {test_loss:.4f}\n")
        f.write(f"Test Accuracy: {test_acc * 100:.2f}%\n")
        f.write(f"Macro F1 Score: {macro_f1:.4f}\n")

    # ==========================================
    # 繪圖區塊
    # ==========================================
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(1, epochs + 1), train_losses, label='Train Loss')
    plt.plot(range(1, epochs + 1), val_losses, label='Val Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Loss Trend')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(range(1, epochs + 1), [acc * 100 for acc in train_accs], label='Train Acc')
    plt.plot(range(1, epochs + 1), [acc * 100 for acc in val_accs], label='Val Acc')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.title('Accuracy Trend')
    plt.legend()
    plt.grid(True)

    chart_path = f"res/{folder_name}/{file_name}_trend.png"
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    # 繪製混淆矩陣
    cm = confusion_matrix(y_true, y_pred, labels=range(node_num))

    # 動態決定圖片大小：節點大於 16 時，把畫布拉大
    fig_size = (10, 8) if node_num <= 16 else (14, 12)
    fig, ax = plt.subplots(figsize=fig_size)

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=range(node_num))

    # 關鍵：節點數大於 16 時，徹底關閉格子內的數字顯示 (include_values=False)
    show_values = True if node_num <= 16 else False
    disp.plot(cmap=plt.cm.Blues, ax=ax, include_values=show_values, values_format='d' if show_values else None)

    # 處理軸標籤擁擠問題：如果節點很多，每隔幾步才顯示一次標籤
    if node_num > 16:
        step = 4 if node_num <= 32 else 8  # 依據節點數量決定標籤間隔
        ax.set_xticks(np.arange(0, node_num, step))
        ax.set_yticks(np.arange(0, node_num, step))
        ax.set_xticklabels(np.arange(0, node_num, step))
        ax.set_yticklabels(np.arange(0, node_num, step))
        # 讓 X 軸標籤轉 45 度，更好閱讀
        plt.xticks(rotation=45)

    plt.title(f'Confusion Matrix ({node_num} Nodes)')
    cm_path = f"res/{folder_name}/{file_name}_confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(cm_path)
    plt.close()

    # 繪製 ROC
    y_true_bin = label_binarize(y_true, classes=range(node_num))
    fpr, tpr, roc_auc = dict(), dict(), dict()
    for i in range(node_num):
        if np.sum(y_true_bin[:, i]) > 0:
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_probs[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(node_num) if i in fpr]))
    mean_tpr = np.zeros_like(all_fpr)
    valid_classes = 0
    for i in range(node_num):
        if i in fpr:
            mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])
            valid_classes += 1

    if valid_classes > 0:
        mean_tpr /= valid_classes
        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

    plt.figure(figsize=(10, 8))
    if "macro" in fpr:
        plt.plot(fpr["macro"], tpr["macro"],
                 label=f'Macro-average ROC curve (area = {roc_auc["macro"]:.3f})',
                 color='navy', linestyle=':', linewidth=4)

    if node_num <= 10:
        colors = plt.cm.get_cmap('tab10', node_num)
        for i in range(node_num):
            if i in fpr:
                plt.plot(fpr[i], tpr[i], color=colors(i), lw=1.5,
                         label=f'ROC of Node {i} (area = {roc_auc[i]:.3f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve for Deep Learning Attack')
    plt.legend(loc="lower right" if node_num <= 10 else "lower right", fontsize='small')

    roc_path = f"res/{folder_name}/{file_name}_roc.png"
    plt.savefig(roc_path)
    plt.close()

    print(f"所有圖表已儲存至 res/{folder_name}/ 資料夾內！")


# ==========================================
# 3. 啟動區塊
# ==========================================
if __name__ == "__main__":
    # --- 參數設定區 ---
    NODE_NUM = 32
    TOTAL_ROUNDS = 20000  # 要生成的通訊總回合數 (對應 24991 筆有效樣本)
    WINDOW_SIZE = 100  # 滑動視窗長度 (駭客一次觀察連續幾次回合)

    NOISE_PROB = 0.3  # 每回合有 30% 機率會加入隨機噪聲 (模擬真實環境中其他通訊)
    MAX_SENDERS = int(NODE_NUM*0.8)  # 每回合最多有幾個節點傳東西給目標節點 (模擬多重通訊情境)

    # 訓練超參數
    EPOCHS = 100  # 因為這份數據特徵早就被徹底抹除，大概 20 Epoch 就會確認 Loss 下不去
    LR = 0.002

    # 如果 True，會覆蓋現有資料重新透過 ORAM 生成新的通訊軌跡
    GEN_DATA_FLAG = True

    train(node_num=NODE_NUM,
          total_rounds=TOTAL_ROUNDS,
          window_size=WINDOW_SIZE,
          noise_prob=NOISE_PROB,
          max_senders=MAX_SENDERS,
          epochs=EPOCHS,
          lr=LR,
          gen_data_flag=GEN_DATA_FLAG)