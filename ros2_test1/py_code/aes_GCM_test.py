from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64


def aes_encrypt(plain_text, key):
    cipher = AES.new(key, AES.MODE_GCM)  # 創建加密對象
    encrypted, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))  # 加密

    return encrypted, cipher.nonce, tag


def aes_decrypt(encrypted_text, key, nonce, tag):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # 創建解密對象
    decrypted = cipher.decrypt_and_verify(encrypted_text, tag)  # 解密
    return decrypted


def main():
    key = get_random_bytes(32)  # 256位元密鑰
    print(key)
    print(len(key))

    for _ in range(5):
        plain_text = "Happy Birthday!"  # 要加密的明文

        print(f"明文: {plain_text}")

        encrypted,nonce,tag = aes_encrypt(plain_text, key)
        print(f"加密後:\nencrypted: {base64.b64encode(encrypted).decode('utf-8')}\nnonce: {base64.b64encode(nonce).decode('utf-8')}\ntag: {base64.b64encode(tag).decode('utf-8')}")

        decrypted = aes_decrypt(encrypted, key, nonce, tag)  # 解密
        print(f"解密後: {decrypted.decode('utf-8')}")


if __name__ == "__main__":
    main()