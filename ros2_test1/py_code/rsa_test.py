import rsa

# 生成密钥
(pubkey, privkey) = rsa.newkeys(1024)

# 明文
message = 'hello,world!'
print('明文:', message)

# 加密
crypto = rsa.encrypt(message.encode(), pubkey)
print('加密:', crypto)
print(f"{type(crypto) = }")
# 解密
message = rsa.decrypt(crypto, privkey).decode()

print('解密:', message)
