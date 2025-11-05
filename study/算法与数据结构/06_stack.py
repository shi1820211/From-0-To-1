class Stack(object):
    """栈"""
    def __init__(self):
        self._list=[]


    def push(self,item):
        """添加一个新元素到栈顶"""
        self._list.append(item)


    def pop(self):
        """弹出栈顶元素"""
        return self._list.pop()




    def  peek(self):
        """返回栈顶元素"""
        if self.is_empty():
            return None
        else:
            return self._list[-1]



    def is_empty(self):
        """判断栈是否为空"""
        return self._list == []




    def size(self):
        """返回栈的元素个数"""
        return len(self._list)




if __name__=="__main__":
    s=Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    s.push(4)
    s.push(5)
    print(s.size())
    print(s.pop())
    print(s.pop())
    print(s.pop())
    print(s.pop())
    print(s.pop())
    