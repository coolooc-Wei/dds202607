class Aes:
    def __init__(self,key_path):
        self.key_path = key_path
        self.key = None
        self.load_private_key()

    def load_private_key(self):
        with open(self.key_path, mode='rb') as key_file:
            self.key = key_file.read()
    

    def decrypt_string(self,encrypted_text):
        encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
        iv = encrypted_bytes[:16]  # 提取IV
        encrypted_data = encrypted_bytes[16:]  # 提取加密資料
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # 創建解密對象
        decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
        return decrypted
        