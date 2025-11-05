
def binary_search(alist,item):
    """二分法 递归"""
    n=len(alist)
    if n>0:
        mid=n//2
        if alist[mid]==item:
            return True
        elif alist[mid]<item:
            return binary_search(alist[mid+1:],item)
        else:
            return binary_search(alist[:mid],item)
        return False
    return None


def binary_search(alist,item):
    """非递归"""
    n=len(alist)
    mid = n // 2
    first = 0
    last = n - 1
    while first <= last:
        if alist[mid]==item:
            return True
        elif alist[mid]<item:
            first = mid+1
            return binary_search(alist[mid+1:],item)
        else:
            last = mid-1
            return binary_search(alist[:mid],item)
    return None


if __name__=='__main__':
    li = [17,20,26,31,44,54,55,77,93]