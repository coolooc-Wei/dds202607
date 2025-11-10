from sys import byteorder
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import json
import base64
import pickle
import sys

class AES_tools:
    def __init__(self,key_path:str):
        self.key_path = key_path
        self.key = None
        self.load_private_key()

    def load_private_key(self):
        with open(self.key_path, mode='rb') as key_file:
            self.key = key_file.read()

    def byte_xor(self,var_1, var_2, byteorder=sys.byteorder):
        var_2, var_1 = var_2[:len(var_1)], var_1[:len(var_2)]
        int_var_1 = int.from_bytes(var_1, byteorder)
        int_var_2 = int.from_bytes(var_2, byteorder)
        int_enc = int_var_1 ^ int_var_2
        return int_enc.to_bytes(len(var_1), byteorder)
    
    def encrypt_obj_cbc(self,data):
        data = pickle.dumps(data)
        plain_text = base64.b64encode(data).decode('utf-8')
        iv = get_random_bytes(16)  # 生成隨機初始化向量
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # 創建加密對象
        encrypted = cipher.encrypt(pad(plain_text, AES.block_size))  # 加密並補位
        return base64.b64encode(iv + encrypted).decode('utf-8')  # 返回加密後的資料（含IV）

    def decrypt_obj_cbc(self,encrypted_text):
        encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
        iv = encrypted_bytes[:16]  # 提取IV
        encrypted_data = encrypted_bytes[16:]  # 提取加密資料
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # 創建解密對象
        decrypted = unpad(cipher.decrypt(encrypted_data), AES.block_size).decode('utf-8')  # 解密並去補位
        return decrypted

    def encrypt_obj_gcm(self,data):
        data = pickle.dumps(data)
        plain_text = base64.b64encode(data)
        cipher = AES.new(self.key, AES.MODE_GCM)  # 創建加密對象
        encrypted, tag = cipher.encrypt_and_digest(plain_text)  # 加密
        tmp_dict =  {'encrypted':encrypted, 'nonce':cipher.nonce, 'tag':tag}
        res_json = json.dumps(tmp_dict, default=lambda x: base64.b64encode(x).decode('utf-8'))
        return res_json
    
    def encrypt_obj_gcm_multi(self,data,fake_num=0):
        data = pickle.dumps(data)
        plain_text = base64.b64encode(data)
        cipher = AES.new(self.key, AES.MODE_GCM)  # 創建加密對象
        encrypted, tag = cipher.encrypt_and_digest(plain_text)  # 加密
        tmp_dict =  {'encrypted':encrypted, 'nonce':cipher.nonce, 'tag':tag}
        res_json = json.dumps(tmp_dict, default=lambda x: base64.b64encode(x).decode('utf-8'))
        fake_list = []
        for _ in range(fake_num):
            tmp_encrypted = self.byte_xor(encrypted, get_random_bytes(len(encrypted)))
            tmp_nonce = self.byte_xor(cipher.nonce, get_random_bytes(len(cipher.nonce)))
            tmp_tag = self.byte_xor(tag, get_random_bytes(len(tag)))
            tmp_dict_fake =  {'encrypted':tmp_encrypted, 'nonce':tmp_nonce, 'tag':tmp_tag}
            res_json_fake = json.dumps(tmp_dict_fake, default=lambda x: base64.b64encode(x).decode('utf-8'))
            print(f"{res_json_fake = }")
            fake_list.append(res_json_fake)
        return [res_json, fake_list]

        
    def decrypt_obj_gcm(self,input_json):
        input_dict = json.loads(input_json)
        # print(input_dict)
        encrypted_text = input_dict['encrypted']
        nonce = input_dict['nonce']
        tag = input_dict['tag']
        encrypted_text = base64.b64decode(encrypted_text)
        nonce = base64.b64decode(nonce)
        tag = base64.b64decode(tag)
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)  # 創建解密對象
        decrypted = cipher.decrypt_and_verify(encrypted_text, tag)  # 解密
        decrypted = base64.b64decode(decrypted)
        decrypted = pickle.loads(decrypted)
        return decrypted