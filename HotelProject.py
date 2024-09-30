
splits = 0
parent_splits = 0
fusions = 0
parent_fusions = 0


class Node(object):
    """Base node object. It should be index node
    Each node stores keys and children.
    Attributes:
        parent
    """

    def __init__(self, parent=None):
        """Child nodes are stored in values. Parent nodes simply act as a medium to traverse the tree.
        :type parent: Node"""
        self.keys: list = []
        self.values: list[Node] = []
        self.parent: Node = parent

    def index(self, key):
        """Return the index where the key should be.
        :type key: str
        """
        for i, item in enumerate(self.keys):
            if key < item:
                return i

        return len(self.keys)

    def __getitem__(self, item):
        return self.values[self.index(item)]

    def __setitem__(self, key, value):
        i = self.index(key)
        self.keys[i:i] = [key]
        self.values.pop(i)
        self.values[i:i] = value

    def split(self):
        """Splits the node into two and stores them as child nodes.
        extract a pivot from the child to be inserted into the keys of the parent.
        @:return key and two children
        """
        global splits, parent_splits
        splits += 1
        parent_splits += 1

        left = Node(self.parent)

        mid = len(self.keys) // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid + 1]
        for child in left.values:
            child.parent = left

        key = self.keys[mid]
        self.keys = self.keys[mid + 1:]
        self.values = self.values[mid + 1:]

        return key, [left, self]

    def __delitem__(self, key):
        i = self.index(key)
        del self.values[i]
        if i < len(self.keys):
            del self.keys[i]
        else:
            del self.keys[i - 1]

    def fusion(self):
        global fusions, parent_fusions
        fusions += 1
        parent_fusions += 1

        index = self.parent.index(self.keys[0])
        # merge this node with the next node
        if index < len(self.parent.keys):
            next_node: Node = self.parent.values[index + 1]
            next_node.keys[0:0] = self.keys + [self.parent.keys[index]]
            for child in self.values:
                child.parent = next_node
            next_node.values[0:0] = self.values
        else:  # If self is the last node, merge with prev
            prev: Node = self.parent.values[-2]
            prev.keys += [self.parent.keys[-1]] + self.keys
            for child in self.values:
                child.parent = prev
            prev.values += self.values

    def borrow_key(self, minimum: int):
        index = self.parent.index(self.keys[0])
        if index < len(self.parent.keys):
            next_node: Node = self.parent.values[index + 1]
            if len(next_node.keys) > minimum:
                self.keys += [self.parent.keys[index]]

                borrow_node = next_node.values.pop(0)
                borrow_node.parent = self
                self.values += [borrow_node]
                self.parent.keys[index] = next_node.keys.pop(0)
                return True
        elif index != 0:
            prev: Node = self.parent.values[index - 1]
            if len(prev.keys) > minimum:
                self.keys[0:0] = [self.parent.keys[index - 1]]

                borrow_node = prev.values.pop()
                borrow_node.parent = self
                self.values[0:0] = [borrow_node]
                self.parent.keys[index - 1] = prev.keys.pop()
                return True

        return False


class Leaf(Node):
    def __init__(self, parent=None, prev_node=None, next_node=None):
        """
        Create a new leaf in the leaf link
        :type prev_node: Leaf
        :type next_node: Leaf
        """
        super(Leaf, self).__init__(parent)
        self.next: Leaf = next_node
        if next_node is not None:
            next_node.prev = self
        self.prev: Leaf = prev_node
        if prev_node is not None:
            prev_node.next = self

    def __getitem__(self, item):
        return self.values[self.keys.index(item)]

    def __setitem__(self, key, value):
        i = self.index(key)
        if key not in self.keys:
            self.keys[i:i] = [key]
            self.values[i:i] = [value]
        else:
            self.values[i - 1] = value

    def split(self):
        global splits
        splits += 1

        left = Leaf(self.parent, self.prev, self)
        mid = len(self.keys) // 2

        left.keys = self.keys[:mid]
        left.values = self.values[:mid]

        self.keys: list = self.keys[mid:]
        self.values: list = self.values[mid:]

        # When the leaf node is split, set the parent key to the left-most key of the right child node.
        return self.keys[0], [left, self]

    def __delitem__(self, key):
        i = self.keys.index(key)
        del self.keys[i]
        del self.values[i]

    def fusion(self):
        global fusions
        fusions += 1

        if self.next is not None and self.next.parent == self.parent:
            self.next.keys[0:0] = self.keys
            self.next.values[0:0] = self.values
        else:
            self.prev.keys += self.keys
            self.prev.values += self.values

        if self.next is not None:
            self.next.prev = self.prev
        if self.prev is not None:
            self.prev.next = self.next

    def borrow_key(self, minimum: int):
        index = self.parent.index(self.keys[0])
        if index < len(self.parent.keys) and len(self.next.keys) > minimum:
            self.keys += [self.next.keys.pop(0)]
            self.values += [self.next.values.pop(0)]
            self.parent.keys[index] = self.next.keys[0]
            return True
        elif index != 0 and len(self.prev.keys) > minimum:
            self.keys[0:0] = [self.prev.keys.pop()]
            self.values[0:0] = [self.prev.values.pop()]
            self.parent.keys[index - 1] = self.keys[0]
            return True

        return False


class BPlusTree(object):
    """B+ tree object, consisting of nodes.
    Nodes will automatically be split into two once it is full. When a split occurs, a key will
    'float' upwards and be inserted into the parent node to act as a pivot.
    Attributes:
        maximum (int): The maximum number of keys each node can hold.
    """
    root: Node

    def __init__(self, maximum=4):
        self.root = Leaf()
        self.maximum: int = maximum if maximum > 2 else 2
        self.minimum: int = self.maximum // 2
        self.depth = 0

    def find(self, key) -> Leaf:
        """ find the leaf
        Returns:
            Leaf: the leaf which should have the key
        """
        node = self.root
        # Traverse tree until leaf node is reached.
        while type(node) is not Leaf:
            node = node[key]

        return node

    def __getitem__(self, item):
        return self.find(item)[item]

    def query(self, key):
        """Returns a value for a given key, and None if the key does not exist."""
        leaf = self.find(key)
        return leaf[key] if key in leaf.keys else None

    def change(self, key, value):
        """change the value
        Returns:
            (bool,Leaf): the leaf where the key is. return False if the key does not exist
        """
        leaf = self.find(key)
        if key not in leaf.keys:
            return False, leaf
        else:
            leaf[key] = value
            return True, leaf

    def __setitem__(self, key, value, leaf=None):
        """Inserts a key-value pair after traversing to a leaf node. If the leaf node is full, split
              the leaf node into two.
              """
        if leaf is None:
            leaf = self.find(key)
        leaf[key] = value
        if len(leaf.keys) > self.maximum:
            self.insert_index(*leaf.split())

    def insert(self, key, value):
        """
        Returns:
            (bool,Leaf): the leaf where the key is inserted. return False if already has same key
        """
        leaf = self.find(key)
        if key in leaf.keys:
            return False, leaf
        else:
            self.__setitem__(key, value, leaf)
            return True, leaf

    def insert_index(self, key, values: list[Node]):
        """For a parent and child node,
                    Insert the values from the child into the values of the parent."""
        parent = values[1].parent
        if parent is None:
            values[0].parent = values[1].parent = self.root = Node()
            self.depth += 1
            self.root.keys = [key]
            self.root.values = values
            return

        parent[key] = values
        # If the node is full, split the  node into two.
        if len(parent.keys) > self.maximum:
            self.insert_index(*parent.split())
        # Once a leaf node is split, it consists of a internal node and two leaf nodes.
        # These need to be re-inserted back into the tree.

    def delete(self, key, node: Node = None):
        if node is None:
            node = self.find(key)
        del node[key]

        if len(node.keys) < self.minimum:
            if node == self.root:
                if len(self.root.keys) == 0 and len(self.root.values) > 0:
                    self.root = self.root.values[0]
                    self.root.parent = None
                    self.depth -= 1
                return

            elif not node.borrow_key(self.minimum):
                node.fusion()
                self.delete(key, node.parent)

    def show(self, node=None, file=None, _prefix="", _last=True):
        """Prints the keys at each level."""
        if node is None:
            node = self.root
        print(_prefix, "`- " if _last else "|- ", node.keys, sep="", file=file)
        _prefix += "   " if _last else "|  "

        if type(node) is Node:
            # Recursively print the key of child nodes (if these exist).
            for i, child in enumerate(node.values):
                _last = (i == len(node.values) - 1)
                self.show(child, file, _prefix, _last)

    def output(self):
        return splits, parent_splits, fusions, parent_fusions, self.depth

    def readfile(self, reader):
        i = 0
        for i, line in enumerate(reader):
            s = line.decode().split(maxsplit=1)
            self[s[0]] = s[1]
            if i % 1000 == 0:
                print('Insert ' + str(i) + 'items')
        return i + 1

    def leftmost_leaf(self) -> Leaf:
        node = self.root
        while type(node) is not Leaf:
            node = node.values[0]
        return node

    def inorder(self, node=None, L=[]):
        """Perform in-order traversal on the B+ Tree and print keys in order."""
        if node is None:
            node = self.root  # Start from the root if no node is provided
        if isinstance(node, Leaf):  # If it's a leaf node, print its keys
            for key in node.keys:
                L.append(key)
        else:
            # Traverse internal node by recursively traversing children
            for i in range(len(node.keys)):
                self.inorder(node.values[i],L)  # Visit the child
            self.inorder(node.values[-1],L)  # Traverse the last child
        return L
    
    def inorder_leaf(self):
        """Perform in-order traversal and return keys (room numbers) from the leaf nodes only."""
        leaf = bplustree.leftmost_leaf()  # Start from the leftmost leaf
        result = []
        
        while leaf is not None:
            result.extend(leaf.keys)  # Collect all keys in the current leaf
            leaf = leaf.next  # Move to the next leaf in the linked list
        return result

#---------------------------------------------------------------------------------------------------------------------------------------------------

def generate_room_number(num_walk_in = 1, num_bus = 1, num_ship = 1, num_fleet = 1): 
      room_number = []
      list_old_guest = bplustree.inorder()
      num_old_guest = len(list_old_guest)
      move_old_guest(list_old_guest)
      for o in range(num_old_guest) :
            room_num = pow(2,o)*pow(3,0)*pow(5,0)*pow(7,0)
            room_number.append((room_num,[0,0,0,o]))
      for i in range(1,num_fleet+1) :
            for j in range(1,num_ship+1) :
                  for k in range(1,num_bus+1) :
                        for l  in range(1,num_walk_in+1) :
                              room_num = pow(2,l)*pow(3,k)*pow(5,j)*pow(7,i)
                              room_number.append((room_num,[i,j,k,l]))
      sort_rooms(room_number,0,len(room_number)-1)
      return room_number

def receive_guests():
      receive_guests = [x for x in input("Route of guest arrival : ").split('/')]
      for i in range(len(receive_guests)) :
            route,amount = receive_guests[i].split(':')
            if route == 'walk_in' :
                  num_walk_in = amount[0]
                  list_room_number = generate_room_number(int(num_walk_in))
            elif route == 'bus' :
                  num_bus , num_walk_in = amount.split(',')
                  list_room_number = generate_room_number(int(num_walk_in),int(num_bus))
            elif route == 'ship' :
                  num_ship, num_bus , num_walk_in = amount.split(',')
                  list_room_number = generate_room_number(int(num_walk_in),int(num_bus),int(num_ship))
            elif route == 'fleet' :
                  num_fleet, num_ship, num_bus , num_walk_in = amount.split(',')
                  list_room_number = generate_room_number(int(num_walk_in),int(num_bus),int(num_ship),int(num_fleet))
            print(list_room_number)
      add_room(list_room_number)


def add_room(list_room_number):
    for room_number,route_data in list_room_number:
        bplustree[room_number] = route_data

def move_old_guest(list_old_guest):
    for guest in list_old_guest :
      bplustree.delete(guest)

def set_up_hotel():
    for i in range(5):
        bplustree[i] = [0,0,0,i]


# Function Group 3 - Room Operations and Display
def sort_rooms(room_number,low,high):
    if low < high:

        pi = partition(room_number, low, high)


        sort_rooms(room_number, low, pi - 1)
        sort_rooms(room_number, pi + 1, high)
    


def partition(arr, low, high):
  

    pivot = arr[high][0]
    
    i = low - 1
    for j in range(low, high):
        if arr[j][0] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1



def search_room(): #if you want to pass parameter delete below code and add to parameter instead อ่านอังกฤษเอานะ ขก เขียนไทย
    room_number = int(input("Seacrh Room Number: ")) # delete this if you dont want it
    
    leaf = bplustree.find(room_number) #Function that this Tree already give so use it why not only BigO (log N) :D
    if room_number in leaf.keys:
        print (f"Room {room_number} exists in the tree.")  #print for DEBUG you can delete if you want
        return True #Return if room already in tree
    else:
        print (f"Room {room_number} does not exist in the tree.") #for DEBUG you can delete
        return False #Return if room is not in tree

def show_available_rooms():
   
    room = bplustree.inorder_leaf() #list that contain number of Room from leaf inorder that only get leaf
    
    count = 0 #count availible room in tree
    if room[0] != 0: #I dont know that do we still have room number 0 or not if not delete this for me thank you
        count += 1
    
    for i in range (len(room)-1): #sadly it has to be BigO (N) D;
        if room[i+1] - room[i] > 1:
            count += room[i+1] - room[i]-1 
    
    return count
            

# Function Group 4: Performance Monitoring and Reporting
def display_memory_usage():
    pass

def write_to_file(filename="hotel_report.txt"):
    pass

def measure_time(func, *args):
    pass

def manage_command():
    command = input("Enter your command : ")
    if command == 'RG':
        receive_guests()
        return True
    elif command == 'C':
        return False
    elif command == "S":   # in tree or not in tree
        search_room()
        return True
    elif command == "A":
        print(show_available_rooms()) # integer <3
        return True

if __name__ == '__main__':
    bplustree = BPlusTree()
    set_up_hotel()
    recieve_command = True
    while recieve_command :
        recieve_command = manage_command()
    
    
