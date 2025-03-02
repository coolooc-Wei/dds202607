from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
import time


def aes_encrypt_cbc(plain_text, key):
    iv = get_random_bytes(16)  # 生成隨機初始化向量
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建加密對象
    encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
    return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）


def aes_decrypt_cbc(encrypted_text, key):
    encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
    iv = encrypted_bytes[:16]  # 提取IV
    encrypted_data = encrypted_bytes[16:]  # 提取加密資料
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建解密對象
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
    return decrypted

def aes_encrypt_gcm(plain_text, key):
    cipher = AES.new(key, AES.MODE_GCM)  # 創建加密對象
    encrypted, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))  # 加密

    return encrypted, cipher.nonce, tag


def aes_decrypt_gcm(encrypted_text, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # 創建解密對象
    decrypted = cipher.decrypt_and_verify(encrypted_text, tag)  # 解密
    return decrypted


def time_test_cbc():

    encrypt_time = 0
    decrypt_time = 0
    tmp_time = 0

    for _ in range(100000):
        key = get_random_bytes(32)  # 128位元密鑰
        # print(key)
        # print(len(key))
        plain_text = "Happy Birthday!"  # 要加密的明文

        # print(f"明文: {plain_text}")

        tmp_time = time.time()
        encrypted = aes_encrypt_cbc(plain_text, key)  # 加密
        encrypt_time += time.time() - tmp_time
        # print(f"加密後: {encrypted}")

        tmp_time = time.time()
        decrypted = aes_decrypt_cbc(encrypted, key)  # 解密
        decrypt_time += time.time() - tmp_time
        # print(f"解密後: {decrypted}")

    print(f"加密時間: {encrypt_time}")
    print(f"解密時間: {decrypt_time}")

def time_test_gcm():
    key = get_random_bytes(32)  # 256位元密鑰
    # print(key)
    # print(len(key))

    encrypt_time = 0
    decrypt_time = 0
    tmp_time = 0

    for _ in range(100000):
        plain_text = "Happy Birthday!"  # 要加密的明文

        # print(f"明文: {plain_text}")
        tmp_time = time.time()
        encrypted, nonce, tag = aes_encrypt_gcm(plain_text, key)
        # print(f"加密後:\nencrypted: {base64.b64encode(encrypted).decode('utf-8')}\nnonce: {base64.b64encode(nonce).decode('utf-8')}\ntag: {base64.b64encode(tag).decode('utf-8')}")
        encrypt_time += time.time() - tmp_time

        tmp_time = time.time()
        decrypted = aes_decrypt_gcm(encrypted, key, nonce, tag)  # 解密
#         print(f"解密後: {decrypted.decode('utf-8')}")
        decrypt_time += time.time() - tmp_time

    print(f"加密時間: {encrypt_time}")
    print(f"解密時間: {decrypt_time}")

if __name__ == "__main__":

    time_test_cbc()
    time_test_gcm()