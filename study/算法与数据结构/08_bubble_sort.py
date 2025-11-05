def bubble_sort(alist):
    """冒泡算法,从小到大"""
    n = len(alist)
    for j in range (n-1):
        count=0
        for i in range(0,n-j-1):
            if alist[i] > alist[i+1]:
                alist[i], alist[i+1] = alist[i+1], alist[i]
                count+=1
        if count == 0:
            break




if __name__ == '__main__':
    li1=[1,2,5,86,76,89,8]
    li2=[1,2,3,4,5,6]
    bubble_sort(li1)
    bubble_sort(li2)
    print(li1,li2)

