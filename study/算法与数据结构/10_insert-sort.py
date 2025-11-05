def insert_sort(alist):
    """插入排序"""
    n = len(alist)
    for j in range(1,n):
        i=j
        while i>0:
            if alist[i]<alist[i-1]:
                alist[i],alist[i-1]=alist[i-1],alist[i]
                i-=1
            else:
                break


if __name__ == '__main__':
    li=[1,5,3,8,72,63,59,84]
    insert_sort(li)
    print(li)