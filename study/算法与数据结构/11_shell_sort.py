def shell_sort(alist):
    """希尔排序"""
    n=len(alist)
    gap=n//2
    while gap>0:
    # 在这串代码当中n和2*gap-1有什么区别
        for j in [gap,n]:
            i=j
            while i>0:
                if alist[i]<alist[i-gap]:
                    alist[i],alist[i-gap]=alist[i-gap],alist[i]
                    i-=gap
                else:
                    break
        gap//=2



if __name__ == '__main__':
    li=[1,5,3,8,72,63,59,84]
    shell_sort(li)
    print(li)