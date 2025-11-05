from timeit import Timer

def t1():
    li=[]
    for i in range(1001):
        li.append(i)

def t2():
    li=[]
    for i in range(1001):
        li += [i]

def t3():
    li=[i for i in range(1001)]

def t4():
    li=list(range(1001))


timer1=Timer('t1()',f"from {__name__} import t1")
time=timer1.timeit(number=1000)
print(f"用时：{time:.32}")

timer2=Timer('t2()',f"from {__name__} import t2")
time2=timer2.timeit(number=1000)
print(f"用时:{time2:.32}")

timer3=Timer("t3()",f"from {__name__} import t3")
time3=timer3.timeit(number=1000)
print(f"用时:{time3:.32}")

timer4=Timer("t4()",f"from {__name__} import t4")
time4=timer4.timeit(number=1000)
print(f"用时:{time4:.32}")