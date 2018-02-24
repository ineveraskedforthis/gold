class Stack:
    def __init__(self):
        self.length = 0
        self.data = []

    def push(self, item):
        if self.length == len(self.data):
            self.data.append(item)
        else:
            self.data[self.length] = item
        self.length += 1

    def top(self):
        return self.data[self.length - 1]

    def pop(self):
        self.length -= 1
        return self.data[self.length]

    def get_len(self):
        return self.length


class TreeNode:
    def __init__(self, parent = None):
        self.parent = parent
        self.childs = set()

    def add_node(self, node):
        self.childs.add(node)
        node.parent = self

    def get_len(self):
        return len(self.childs)

    def del_child(self, node):
        self.childs.discard(node)

    def clear(self):
        self.childs.clear()

class Queue:
    def __init__(self):
        self.left = 0
        self.right = 0
        self.max_right = 0
        self.data = []

    def push(self, x):
        if self.right > self.max_right:
            self.data.append(x)
            self.right += 1
            self.max_right += 1
        else:
            self.data[right] = x
            self.right += 1

    def get(self):
        if self.left == self.right:
            return None
        return self.data[self.left]

    def pop(self):
        if self.get() == None:
            return None
        else:
            return self.get()
            self.left += 1
