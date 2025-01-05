from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64


def aes_encrypt(plain_text, key):
    iv = get_random_bytes(16)  # 生成隨機初始化向量
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建加密對象
    encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
    return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）


def aes_decrypt(encrypted_text, key):
    encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
    iv = encrypted_bytes[:16]  # 提取IV
    encrypted_data = encrypted_bytes[16:]  # 提取加密資料
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建解密對象
    decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
    return decrypted


def main():
    key = get_random_bytes(32)  # 128位元密鑰
    print(key)
    print(len(key))
    plain_text = "Happy Birthday!"  # 要加密的明文

    print(f"明文: {plain_text}")

    encrypted = aes_encrypt(plain_text, key)  # 加密
    print(f"加密後: {encrypted}")

    decrypted = aes_decrypt(encrypted, key)  # 解密
    print(f"解密後: {decrypted}")


if __name__ == "__main__":
    main()