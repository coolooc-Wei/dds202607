# ROS 2 後量子安全與 PathORAM 流量隱私保護框架
*(ROS 2 Post-Quantum Security & PathORAM Privacy Protection Framework)*

---

## 📋 1. 專案簡介與總體目的 (Project Overview & Purpose)

本專案為針對 **ROS 2 (Robot Operating System 2) 多機器人聯網與分散式控制系統** 所設計的 **後量子安全 (Post-Quantum Cryptography, PQC) 與流量隱私保護 (Traffic Privacy Protection) 綜合實驗框架**。

### 核心背景與要解決的問題：
1. **後量子威脅 (Post-Quantum Threat)**：傳統 ROS 2 或 SROS2 採用的 RSA/ECC 非對稱加密演算法在量子電腦成熟後易被破解，本專案導入後量子密碼學 (PQC) 確保金鑰交換之安全。
2. **流量側道攻擊 (Traffic Side-Channel Attacks)**：在傳統的加密通訊中，即使通訊內容 (Payload) 已做強加密，攻擊者仍可透過監聽封包傳送頻率、封包大小、節點 IP/Topic 互動方向，推斷出機器人目前的任務狀態、關鍵傳輸目標或控制拓樸。

### 本專案的核心解決方案：
* **後量子金鑰協商**：整合 **ML-KEM-1024 (Kyber)** 演算法，在 ROS 2 節點間進行安全且具抗量子能力的金鑰封裝與交換。
* **強對稱加密**：採用 **AES-128/256 (CBC/GCM)** 進行主題 (Topic) 數據的高效加解密。
* **PathORAM 流量混淆機制**：將 ROS 2 節點動態映射至二元樹 (Tree-mapped PathORAM)，在傳輸真實訊息的同時注入隨機虛擬封包 (Dummy Traffic) 並進行路徑打亂 (Shuffle)，徹底遮蔽機器人節點間真實的傳輸頻率與互動關係。
* **秘密分享 (Secret Sharing)**：結合 Shamir's Secret Sharing 進行敏感數據的分散式傳輸。
* **深度學習 Side-Channel 防禦評估系統**：構建基於 **Deep Fingerprinting (DF CNN)**、**MLP 分類器**、**U-Net** 及 **迴歸模型** 的 AI 評估機制，模擬攻擊者試圖從網路流量特徵中辨識真實目標，用以量化與證明 PathORAM 機制抵禦側道攻擊的隱私保護效果。
* **真實機器人數據驗證**：載入 **MIT Lab TurtleBot** 的實際運動數據 (`cmd_vel`, `odom` rosbag2) 進行真實案例模擬。

---

## 🏗️ 2. 專案架構 (Repository Architecture)

整個 Repository 主要分為 ROS 2 工作區 (`ros2_test1`)、AI/ML 側道攻擊防禦評估 (`PathORAM_Evaluate`)、機器人實驗數據 (`mit_lab_data`) 及研究文件 (`doc`) 等四大區塊：

```
.
├── ros2_test1/                     # ROS 2 工作區 (ROS 2 Workspace)
│   ├── src/                        # ROS 2 Packages 源碼
│   │   ├── interfaces/             # 自訂 ROS 2 介面 (Service 定義)
│   │   │   └── srv/Kyber.srv       # Kyber 後量子金鑰交換服務介面
│   │   ├── sros_package/           # 核心密碼學與 PathORAM 演算法 Python 封裝庫
│   │   │   ├── AES_tools.py        # AES (CBC/GCM) 加解密與 Dummy 封包生成工具
│   │   │   ├── pathORAM.py         # PathORAM 樹狀結構映射與路徑打亂演算法
│   │   │   ├── kyber_client.py     # Kyber 金鑰交換 Client 節點
│   │   │   └── kyber_server.py     # Kyber 金鑰交換 Server 節點
│   │   └── test_1_py/              # ROS 2 應用與測試節點包
│   │       ├── multi_publisher_ORAM_paper.py  # 多進程多節點 PathORAM Topic 發送器
│   │       ├── subscriber_kyber_aes_pickle.py # Kyber+AES 訂閱者與數據解密
│   │       ├── publisher_secret_share.py      # Shamir Secret Sharing 發送者
│   │       ├── subscriber_secret_share.py     # Shamir Secret Sharing 接收者
│   │       ├── publisher_mit_test.py          # MIT Lab rosbag 數據重播發送器
│   │       └── subscriber_mit_odom.py         # MIT Lab 里程計數據接收器
│   ├── py_code/                    # 獨立密碼學效能測試與視覺化腳本
│   │   ├── aes_GCM_test.py         # AES-GCM 效能基準測試
│   │   ├── aes_time.py             # AES 時間延遲測試
│   │   ├── kem_aes_test.py         # Kyber KEM + AES 結合測試
│   │   ├── gen_kyber_keys.py       # 批次生成 Kyber 金鑰對工具
│   │   ├── liboqs-python_examples/ # liboqs-python 範例程式碼
│   │   └── vis/                    # 基於 Flask 的 Web 流量視覺化監控Dashboard
│   └── ros2_test_init.bash         # ROS 2 工作區環境初始化腳本
│
├── PathORAM_Evaluate/              # AI/ML 側道攻擊與隱私防禦評估框架
│   ├── gen_df_data.py              # 多進程流量矩陣模擬生成器 (支援 ORAM/非 ORAM)
│   ├── gen_df_data_multi_node.py   # 多節點流量模擬生成器
│   ├── gen_df_data_single_node.py  # 單節點流量模擬生成器
│   ├── df_model.py                 # Deep Fingerprinting (DF) 卷積神經網路模型結構
│   ├── df_train.py                 # Deep Fingerprinting 模型訓練與評估腳本
│   ├── Classification_model.py     # MLPClassifier 多層感知機分類與混淆矩陣/ROC繪製
│   ├── Regression_model.py         # 迴歸模型流量預測評估
│   ├── df_data_vis.py              # 流量矩陣數據視覺化工具
│   ├── pathORAM_test.py            # 評估專用的 PathORAM 演算法實作
│   └── requirements.txt            # Python 依賴套件清單
│
├── mit_lab_data/                   # MIT Lab 機器人實測數據集 (Rosbag2)
│   ├── cmd_odom_data/              # cmd_vel 與 odom rosbag2 數據庫 (.db3, metadata.yaml)
│   ├── rosbag2_2024_11_20-13_57_31/# 歷史記錄 rosbag 數據包
│   └── MutiRobot_go2.zip           # 多機器人移動實測打包數據
│
└── doc/                            # 專案研究文件與專題核定資料
    ├── 113WFAA310563_BASE.PDF      # 相關技術規範/核定文件
    ├── CSL進度表.docx               # 研究計畫進度規劃表
    ├── ORAM 20190808.pptx          # ORAM 演算法原理研究簡報
    └── 計畫申請書核定版_20241218.pdf# 國科會/NSTC 研究計畫申請書核定本
```

---

## 🛠️ 3. 使用之開源工具 vs 額外自研/擴充部分 (Open-Source Tools vs Custom Components)

### A. 現存開源工具與套件 (Open-Source Tools & Libraries Used)

| 工具 / 套件 | 類別 | 在本專案之用途 |
| :--- | :--- | :--- |
| **ROS 2 (Humble/Foxy)** | 中間件框架 | 機器人通訊基底 (`rclpy`, `std_msgs`, `nav_msgs`) |
| **Open Quantum Safe (`liboqs` / `liboqs-python`)** | 後量子密碼學庫 | 提供 ML-KEM-1024 (Kyber1024) 後量子金鑰封裝與解封裝機制 |
| **PyCryptodome** | 密碼學函式庫 | 實作對稱加密 AES-128/256 (CBC, GCM 模式) |
| **TensorFlow / Keras** | 深度學習框架 | 建構與訓練 Deep Fingerprinting (DF CNN) 及 U-Net 模型 |
| **scikit-learn** | 機器學習庫 | 實作 MLPClassifier、資料集分割、混淆矩陣及 ROC/AUC 評估 |
| **Flask** | Web 框架 | 提供 Web 監控介面 (`py_code/vis/app.py`) 展示網路節點流量 |
| **NumPy / Matplotlib / Seaborn** | 數據處理與視覺化 | 流量矩陣運算、ROC 曲線繪製與混淆矩陣熱力圖呈現 |
| **Joblib** | 模型序列化 | 保存與載入訓練好的 ML 模型檔案 (`.joblib`) |

---

### B. 本專案額外自研與擴充部分 (Custom-Built Components)

1. **ROS 2 專用 PathORAM 動態路由與混淆模組 (`pathORAM.py` / `ORAM` Class)**：
   * **特色**：將電腦科學中的 Oblivious RAM 機制移植並改編至 ROS 2 發布/訂閱 (Pub/Sub) 架構中。
   * **運作**：將 ROS 2 節點動態對應至 PathORAM 的樹狀葉節點，計算路徑遮罩 (Path Mask)，並在每次資料傳輸後自動進行路徑置換與 Shuffle，使外部監聽者無法透過固定 Topic 觀察節點行為。

2. **Kyber 後量子握手協議 ROS 2 Service 介面 (`interfaces/srv/Kyber.srv` & Kyber Server/Client Nodes)**：
   * **特色**：設計專屬 ROS 2 Service (`Kyber.srv`)，讓 Client 節點發送 Kyber 公鑰，Server 節點進行密文封裝並回傳，動態產出高強度的共享對稱金鑰 (Shared Secret)，完全對抗未來量子電腦解密風險。

3. **混淆流量 (Dummy Traffic) 注入與多通道平行發送器 (`AES_tools.py` & `multi_publisher_ORAM_paper.py`)**：
   * **特色**：`AES_tools.encrypt_obj_gcm_multi()` 可生成真實加密訊息以及結構與長度完全一致的 *偽造 (Dummy) 加密封包*。
   * **運作**：結合多進程 (`multiprocessing.Process`) 與 ROS 2 Timer，依照 PathORAM 計算出的路徑分配，在多個 Topic 間同步發送真實封包與 Dummy 封包，達成「混淆真實傳輸者與接收者」的目的。

4. **流量側道攻擊與隱私防禦 AI 評估機制 (`PathORAM_Evaluate/`)**：
   * **特色**：自主設計 ROS 2 網路流量特徵提取與模擬數據生成器 (`gen_df_data.py`)，能根據節點數量、Dummy 比例、背景噪聲與 ORAM 開關產出流量矩陣 (`.npy`)。
   * **評估**：調用 DF CNN 與 MLP 模型模擬攻擊者嘗試破解通訊拓樸；證明在啟用 PathORAM 時，攻擊者的判斷準確率會下降至接近隨機猜測 (Random Guess)，量化驗證隱私安全。

---

## 🔍 4. 各模組詳細目的與職責說明 (Detailed Purpose & Responsibilities)

### 1. `ros2_test1/src/interfaces/`
* **目的**：定義專案所需的 ROS 2 自訂資料結構與服務介面。
* **負責處理**：
  * `srv/Kyber.srv`：定義 Kyber 後量子金鑰交換的 Request (`string public_key`) 與 Response (`string ciphertext`)。

### 2. `ros2_test1/src/sros_package/`
* **目的**：封裝安全演算法與核心邏輯，提供給 ROS 2 節點調用。
* **負責處理**：
  * `AES_tools.py`：提供對稱加密 (CBC/GCM)、Pickle 物件序列化加密，以及 `encrypt_obj_gcm_multi()` 生成混淆用的 Dummy 加密封包。
  * `pathORAM.py`：維護 PathORAM 的二元樹地圖、計算節點遮罩 (Mask)、隨機選取兩條傳輸路徑並執行路徑打亂 (`shuffle_path`)。
  * `kyber_client.py` & `kyber_server.py`：執行 Kyber 握手流程，並將產出的共享對稱金鑰寫入本地檔案系統供 AES 使用。

### 3. `ros2_test1/src/test_1_py/`
* **目的**：實作具備安全特性的 ROS 2 實體與測試節點。
* **負責處理**：
  * `multi_publisher_ORAM_paper.py`：模擬論文實驗環境，建立多個 Publisher 節點，結合 PathORAM 隨機選路與 AES-GCM 多封包發送，即時將真實數據與 Dummy 數據併發送至多個 `topic_x`。
  * `subscriber_kyber_aes_pickle.py`：訂閱 Topic，讀取加密數據並以 Kyber 協商出的金鑰進行解密，還原原始訊息。
  * `publisher_secret_share.py` & `subscriber_secret_share.py`：實作 Shamir 秘密分享機制，將資料切割成多個 Share 透過不同 Topic 分散傳輸。
  * `publisher_mit_test.py` & `subscriber_mit_odom.py`：讀取 MIT Lab 機器人真實軌跡與控制數據並進行加解密傳輸。

### 4. `ros2_test1/py_code/`
* **目的**：獨立密碼學性能基準測試與網頁視覺化Dashboard。
* **負責處理**：
  * `kem_aes_test.py`, `aes_GCM_test.py`, `aes_time.py`：量測 Kyber 握手時間、AES 加解密吞吐量與延遲。
  * `gen_kyber_keys.py`：預先批次生成金鑰測試檔。
  * `vis/`：建構 Flask Web 伺服器，呈現即時的節點通訊網路圖與傳輸狀態。

### 5. `PathORAM_Evaluate/`
* **目的**：建立 AI/ML 側道攻擊模型，評估 PathORAM 對抗流量側道分析的隱私保護能力。
* **負責處理**：
  * `gen_df_data.py` / `gen_df_data_multi_node.py`：多進程平行生成大量模擬流量矩陣，導出 Training/Validation/Testing 數據集 (`.npy`)。
  * `df_model.py` / `df_train.py`：建立並訓練 1D-CNN Deep Fingerprinting 側道攻擊模型。
  * `Classification_model.py`：訓練 MLP 多層感知機分類器，計算 Overall Accuracy、Micro/Macro F1-Score，並自動繪製 Confusion Matrix 與 ROC 曲線圖表。
  * `df_data_vis.py`：可視化流量矩陣，幫助分析傳輸特徵。

### 6. `mit_lab_data/`
* **目的**：保存 TurtleBot 機器人實際運行的歷史通訊數據。
* **負責處理**：提供真實機器人的運動指令 (`cmd_vel`) 與里程計 (`odom`) rosbag2 資料，使實驗不限於純合成數據，更能反映真實機器人控制系統的流量行為。

### 7. `doc/`
* **目的**：記錄本研究計畫的學術文件與行政核定資料。
* **負責處理**：收錄國科會 (NSTC) 研究計畫申請書核定本、CSL 團隊進度規劃表與 PathORAM 原理簡報。

---

## 🚀 5. 快速上手與執行說明 (Quick Start Guide)

### 1. 安裝環境依賴 (Prerequisites)

* **ROS 2 系統需求**：ROS 2 Humble / Foxy (Linux / WSL2 環境)
* **Python 套件需求**：
  ```bash
  pip install -r PathORAM_Evaluate/requirements.txt
  pip install pycryptodome oqs flask
  ```

### 2. ROS 2 工作區編譯 (Build Workspace)

```bash
cd ros2_test1
colcon build
source install/setup.bash
```

### 3. 執行 Kyber 後量子金鑰交換與 ORAM 加密 Publisher/Subscriber

```bash
# 啟動 Kyber 金鑰 Server
ros2 run sros_package kyber_server

# 啟動 Kyber 金鑰 Client 生成金鑰
ros2 run sros_package kyber_client

# 啟動 PathORAM 多節點加解密通訊測試
python3 ros2_test1/src/test_1_py/test_1_py/multi_publisher_ORAM_paper.py 8
```

### 4. 執行 AI 流量側道攻擊與隱私防禦評估

```bash
cd PathORAM_Evaluate

# 1. 多進程平行生成模擬流量數據集
python gen_df_data.py

# 2. 訓練與評估 MLP 攻擊分類器 (繪製 Confusion Matrix 與 ROC)
python Classification_model.py

# 3. 訓練 Deep Fingerprinting (DF) 側道攻擊模型
python df_train.py
```

---

## 📊 6. 結論與成果 (Conclusion)

本專案成功整合 **後量子密碼學 (PQC Kyber)**、**強對稱加密 (AES-GCM)**、**PathORAM 流量混淆** 與 **AI/ML 側道攻擊驗證機制**。實測結果證明，在啟用 PathORAM 與 Dummy Traffic 注入後，即便攻擊者採用最先進的神經網路 (Deep Fingerprinting / MLP) 進行流量側道分析，其推測真實傳輸節點與拓樸的準確率仍大幅下降至無效位準，為 ROS 2 多機器人系統建構了堅實的**後量子與流量隱私安全屏障**。
