# Key encapsulation Python example

import oqs
from pprint import pprint

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


print("liboqs version:", oqs.oqs_version())
print("liboqs-python version:", oqs.oqs_python_version())
print("Enabled KEM mechanisms:")
kems = oqs.get_enabled_kem_mechanisms()
pprint(kems, compact=True)

# Create client and server with sample KEM mechanisms
kemalg = "Kyber1024"
with oqs.KeyEncapsulation(kemalg) as client:
    with oqs.KeyEncapsulation(kemalg) as server:
        print("\nKey encapsulation details:")
        pprint(client.details)

        # Client generates its keypair
        public_key_client = client.generate_keypair()

        print(type(public_key_client))

        # Optionally, the secret key can be obtained by calling export_secret_key()
        # and the client can later be re-instantiated with the key pair:
        # secret_key_client = client.export_secret_key()
        #
        # # Store key pair, wait... (session resumption):
        # client = oqs.KeyEncapsulation(kemalg, secret_key_client)

        # The server encapsulates its secret using the client's public key
        ciphertext, shared_secret_server = server.encap_secret(public_key_client)

        # The client decapsulates the server's ciphertext to obtain the shared secret
        shared_secret_client = client.decap_secret(ciphertext)

        print(
            "\nShared secretes coincide:", shared_secret_client == shared_secret_server
        )

        print(f"{shared_secret_client = }")
        print(f"{shared_secret_server = }")

        # test for aes with shared secret in kem

        key = shared_secret_client
        print(len(key))

        plain_text = "Happy Birthday!"  # 要加密的明文

        print(f"明文: {plain_text}")

        encrypted = aes_encrypt(plain_text, key)  # 加密
        print(f"加密後: {encrypted}")

        decrypted = aes_decrypt(encrypted, key)  # 解密
        print(f"解密後: {decrypted}")

