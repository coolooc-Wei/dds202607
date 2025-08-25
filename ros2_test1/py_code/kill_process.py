import os

tar = 'sros_kyber_aes_oram_client_test'

l = os.popen('ps -aux | grep python').read()

for s in l.split('\n'):
    # print(s)
    if tar in s:
        num = s.split()[1]
        print(num)
        os.popen(f'kill {num}')