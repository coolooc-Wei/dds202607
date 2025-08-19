import json

class Aes:
    def __init__(self,key_path):
        self.key_path = key_path
        self.key = None
        self.load_private_key()

    def load_private_key(self):
        with open(self.key_path, mode='rb') as key_file:
            self.key = key_file.read()
    
    def aes_encrypt_cbc(self,plain_text):
        iv = get_random_bytes(16)  # 生成隨機初始化向量
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # 創建加密對象
        encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
        return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）

    def decrypt_string_cbc(self,encrypted_text):
        encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
        iv = encrypted_bytes[:16]  # 提取IV
        encrypted_data = encrypted_bytes[16:]  # 提取加密資料
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # 創建解密對象
        decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
        return decrypted

    def aes_encrypt(plain_text, key):
        cipher = AES.new(key, AES.MODE_GCM)  # 創建加密對象
        encrypted, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))  # 加密

        tmp_dict =  {'encrypted':encrypted, 'nonce':cipher.nonce, 'tag':tag}
        res_json = json.dumps(tmp_dict)
        return res_json
        
    def decrypt_string_gcm(self,input_json):
        input_dict = json.loads(input_json)
        encrypted_text = input_dict['encrypted_text']
        nonce = input_dict['nonce']
        tag = input_dict['tag']
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)  # 創建解密對象
        decrypted = cipher.decrypt_and_verify(encrypted_text, tag)  # 解密
        return decrypted