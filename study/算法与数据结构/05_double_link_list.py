from itertools import count


class Node(object):
    def __init__(self,item):
        self.elem = item
        self.next = None
        self.prev = None


    class Double_link_list(object):
        """双链表"""
        def __init__(self,node=None):
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
                print(cur.elem, end=" ")
                cur = cur.next

        def append(self, item):
            """<<添加尾部元素,尾插法>>"""
            node = Node(item)
            if self.is_empty():
                self._head = node
            else:
                cur = self._head
                while cur.next is not None:
                    cur = cur.next
                cur.next = node
                node.prev = cur

        def add(self, item):
            """<<添加头部元素，头插法>>"""
            if self.is_empty():
                self._head = Node(item)
            else:
                node = Node(item)
                node.next = self._head
                self._head = node
                node.next.prev = node

        def remove(self, item):
            """<<删除节点>>"""
            cru = self._head
            pre = None
            while cru != None:
                if cru.elem == item:
                    if item == self._head.elem:
                        self._head = cru.next
                    else:
                        pre.next = cru.next
                        break
                else:
                    pre = cru
                    cru = cru.next

        def search(self, item):
            """<<查找节点是否存在>>"""
            cur = self._head
            while cur != None:
                if cur.elem == item:
                    return True
                else:
                    cur = cur.next
            return False

        def insert(self, pos, item):
            """<<<指定位置添加元素>>>"""
            if pos <= 0:
                self.add(item)
            elif pos >(self.length()-1):
                self.append(item)
            else:
                cur = self._head
                count =0
                while count < pos:
                    cur = cur.next
                    count += 1
                node = Node(item)
                node.next = cur.next
                cur.next = node