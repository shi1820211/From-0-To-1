

def select_sort(alist):
    """选择排序"""
    n = len(alist)
    for j in range(0,n-1):
        min=j
        for i in range(j+1,n):
            if alist[i]<alist[min]:
                min=i
        alist[j],alist[min]=alist[min],alist[j]


if __name__ == '__main__':
    li = [23, 58, 3, 9, 45, 35]
    select_sort(li)
    print(li)

