


class Queue(object):
    """队列"""
    def __init__(self):
        self._list = []



    def enqueue(self, item):
        """添加元素"""
        self._list.append(item)


    def dequeue(self):
        """删除元素"""
        return self._list.pop(0)



    def is_empty(self):
        """判断队列是否为空"""
        return self._list == []



    def size(self):
        """判断队列大小"""
        return len(self._list)




if __name__ == '__main__':
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
print(q.dequeue())
print(q.dequeue())
print(q.dequeue())


