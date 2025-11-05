class Node(object):
    def __init__(self, data):
        self.elem = data
        self.left = None
        self.right = None

class Tree(object):
    def __init__(self):
        self.root = None

    def add (self, data):
        node = Node(data)
        if self.root is None:
            self.root = node
            return
        queue = [self.root]
        while queue:
            cur_node = queue.pop(0)
            if cur_node.left is None:
                cur_node.left = node
                return
            else:
                queue.append(cur_node.left)
            if cur_node.right is None:
                cur_node.right = node
                return
            else:
                queue.append(cur_node.right)



    def bredth_travel(self):
        queue = [self.root]
        while queue:
            cur_node = queue.pop(0)
            print(cur_node.elem)
            if cur_node.left is not None:
                queue.append(cur_node.left)
            if cur_node.right is not None:
                queue.append(cur_node.right)



    def preorder(self,node):
        if node is None:
            return
        print(node.elem)

        self.preorder(node.left)

        self.preorder(node.right)



    def midorder(self,node):
        if node is None:
            return
            self.midorder(node.left)
            print(node.elem,end=" ")
            self.midorder(node.right)



    def postorder(self,node):
        if node is None:
            return
            self.midorder(node.left)
            self.midorder(node.right)
            print(node.elem,end=" ")









