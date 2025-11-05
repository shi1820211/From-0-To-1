# a+b+c=1000  且 a**2加b**2等于c**2

import time
star_time = time.time()
for a in range(0,1001):
    for b in range(0,1001):
        for c in range(0,1001):
            if a+b+c == 1000 and a**2+b**2==c**2:
                print(a,b,c)
end_time = time.time()
finish_time = end_time - star_time
print(f"用时：{finish_time:.2f}")
star_time = time.time()

for a in range(0,1001):
    for b in range(0,1001):
        c = 1000-b-a
        if c< 0:
            continue
        if  a**2+b**2==c**2:
                print(a,b,c)
end_time = time.time()
finish_time = end_time - star_time
print(f"改进后用时：{finish_time:.2f}")