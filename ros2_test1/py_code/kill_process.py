import os

tar = 'multi_publisher_ORAM'

l = os.popen('ps -aux | grep python').read()

for s in l.split('\n'):
    # print(s)
    if tar in s:
        num = s.split()[1]
        print(num)
        os.popen(f'kill {num}')