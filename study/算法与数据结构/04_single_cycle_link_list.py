from sqlalchemy import false


class Node(object):
    def  __init__ (self,elem):
        self.elem = elem
        self.next = None
    pass

class SingleCycleLinkedList(object):
    """单向循环链表"""
    def __init__ (self,node=None):
        self._head = node
        if node!=None:
            node.next=node


    def is_empty(self):
        """判断链表是否为空"""
        return self._head is None


    def length(self):
        """<链表长度>"""
        if self._head is None:
            return 0
        cur = self._head
        count = 1
        while cur.next is not self._head:
            count += 1
            cur = cur.next
        return count


    def travel(self):
        """<<遍历整个链表>>"""
        if self._head is None:
            return
        cur = self._head
        while cur.next is not self._head:
            print(cur.elem ,end=" ")
            cur = cur.next
        print(cur.elem)

    def append(self,item):
        """<<添加尾部元素,尾插法>>"""
        node = Node(item)
        if self.is_empty():
            self._head = node
            node.next = self._head
        else:
            cur = self._head
            while cur.next is not self._head:
                cur = cur.next
            node.next = self._head
            cur.next = node


    def add(self,item):
        """<<添加头部元素，头插法>>"""
        node = Node(item)
        if self.is_empty():
            self._head = node
            node.next = node
        else:
            cur = self._head
            while cur.next is not self._head:
                cur = cur.next
            cur.next = node
            node.next = self._head
            self._head = node


    def remove(self,item):
        """<<删除节点>>"""
        if self.is_empty():
            return
        cru =self._head
        pre = None
        while cru != self._head:
            if cru.elem == item:
                if item == self._head.elem:
                    # 头部
                    rear=self._head
                    while rear.next is not self._head:
                        rear = rear.next
                    self._head = cru.next
                    rear.next = self._head
                else:
                    # 中间
                    pre.next = cru.next
                return
            else:
                pre=cru
                cru =cru.next
        if cru.elem==item:
            if cru==self._head:
                self._head=None
            else:
                pre.next=cru.next
                pre.next=self._head




    def search(self,item):
        """<<查找节点是否存在>>"""
        cur = self._head
        if self.is_empty():
            return False
        while cur != self._head:
            if cur.elem == item:
                return True
            else :
                cur = cur.next
        if cur.elem == item:
            return True
        return False

    def insert(self,pos,item):
        """<<<指定位置添加元素>>>"""




if __name__ == '__main__':
    ll = SingleCycleLinkedList()
    print(ll.length())
    print(ll.travel())
    print(ll.is_empty())

    ll.append(1)
    print(ll.length())
    print(ll.is_empty())
    ll.add(2)
    ll.append(3)
    ll.add(4)
    ll.add(5)
    ll.append(6)
    ll.append(7)