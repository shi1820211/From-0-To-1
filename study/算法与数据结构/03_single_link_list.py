from sqlalchemy import false


class Node(object):
    def  __init__ (self,elem):
        self.elem = elem
        self.next = None
    pass

class SingleLinkedList(object):
    def __init__ (self,node=None):
        self._head = node


    def is_empty(self):
        """判断链表是否为空"""
        return self._head is None


    def length(self):
        """<链表长度>"""
        cur = self._head
        count = 0
        while cur is not None:
            count += 1
            cur = cur.next
        return count


    def travel(self):
        """<<遍历整个链表>>"""
        cur = self._head
        while cur is not None:
            print(cur.elem ,end=" ")
            cur = cur.next

    def append(self,item):
        """<<添加尾部元素,尾插法>>"""
        node = Node(item)
        if self.is_empty():
            self._head = node
        else:
            cur = self._head
            while cur.next is not None:
                cur = cur.next
            cur.next = node


    def add(self,item):
        """<<添加头部元素，头插法>>"""
        if self.is_empty():
            self._head = Node(item)
        else:
            node = Node(item)
            node.next = self._head
            self._head = node

    def remove(self,item):
        """<<删除节点>>"""
        cru =self._head
        pre = None
        while cru != None:
            if cru.elem == item:
                if item == self._head.elem:
                    self._head = cru.next
                else:
                    pre.next = cru.next
                    break
            else:
                pre=cru
                cru =cru.next





    def search(self,item):
        """<<查找节点是否存在>>"""
        cur = self._head
        while cur != None:
            if cur.elem == item:
                return True
            else :
                cur = cur.next
        return False

    def insert(self,pos,item):
        """<<<指定位置添加元素>>>"""




if __name__ == '__main__':
    ll = SingleLinkedList()
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