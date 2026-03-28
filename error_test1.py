import threading
import time

# 模拟一个全局共享的账户余额
balance = 100

def deposit(amount):
    global balance
    # 模拟从数据库读取余额
    temp = balance
    # 故意制造一个微小的延迟，让两个线程有机会同时进入这一行
    time.sleep(0.01)
    # 计算并写回
    balance = temp + amount

# 创建两个线程，同时往账户存 50 元
thread1 = threading.Thread(target=deposit, args=(50,))
thread2 = threading.Thread(target=deposit, args=(50,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

# 理论上应该是 200，但在没有锁的情况下，结果极大概率是 150
print(f"最终余额: {balance}")