from multiprocessing import Process,pool,Queue
import time

a = 10
def test(name,q):
    print(type(q))
    while(True):
        if !q.empty():
            print(f"{name}: {q.get()}")


if __name__ == '__main__':
    q1 = Queue()
    q2 = Queue()
    q = [q1,q2]


    for i in range(2):
        print(q[i])
        p = Process(target=test,args={f'{i}',q[i],})
        p.start()

    for i in range(10):
        q1.put(i*10)
        q2.put(i*100)

