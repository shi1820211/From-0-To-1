def merge_sort(arr):
    """归并算法"""
    n=len(arr)
    if n<2:
        return arr
    middle=n//2
    left_li=merge_sort(arr[:middle])
    right_li=merge_sort(arr[middle:])


    


    left_index=0
    right_index=0
    result=[]
    while left_index<len(left_li) and right_index<len(right_li):
        if left_li[left_index]<right_li[right_index]:
            result.append(arr[left_index])
            left_index=left_index+1
        else :
            result.append(arr[right_index])
            right_index=right_index+1
    result+=left_li[left_index:]
    result+=right_li[right_index:]
    return result