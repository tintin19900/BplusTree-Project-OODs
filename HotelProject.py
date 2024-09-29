# B+ tee in python
import time

# Node creation
class Node:
    def __init__(self, order):
        self.order = order
        self.values = []
        self.keys = []
        self.nextKey = None
        self.parent = None
        self.check_leaf = False

    # Insert at the leaf
    def insert_at_leaf(self, leaf, value, key):
        if (self.values):
            temp1 = self.values
            for i in range(len(temp1)):
                if (value == temp1[i]):
                    self.keys[i].append(key)
                    break
                elif (value < temp1[i]):
                    self.values = self.values[:i] + [value] + self.values[i:]
                    self.keys = self.keys[:i] + [[key]] + self.keys[i:]
                    break
                elif (i + 1 == len(temp1)):
                    self.values.append(value)
                    self.keys.append([key])
                    break
        else:
            self.values = [value]
            self.keys = [[key]]


# B plus tree
class BplusTree:
    def __init__(self, order):
        self.root = Node(order)
        self.root.check_leaf = True

    # Insert operation
    def insert(self, value, key):
        value = str(value)
        old_node = self.search(value)
        old_node.insert_at_leaf(old_node, value, key)

        if (len(old_node.values) == old_node.order):
            node1 = Node(old_node.order)
            node1.check_leaf = True
            node1.parent = old_node.parent
            mid = ((old_node.order + 1) // 2) - 1
            node1.values = old_node.values[mid + 1:]
            node1.keys = old_node.keys[mid + 1:]
            node1.nextKey = old_node.nextKey
            old_node.values = old_node.values[:mid + 1]
            old_node.keys = old_node.keys[:mid + 1]
            old_node.nextKey = node1
            self.insert_in_parent(old_node, node1.values[0], node1)

    # Search operation for different operations
    def search(self, value):
        current_node = self.root
        while(current_node.check_leaf == False):
            temp2 = current_node.values
            for i in range(len(temp2)):
                if (value == temp2[i]):
                    current_node = current_node.keys[i + 1]
                    break
                elif (value < temp2[i]):
                    current_node = current_node.keys[i]
                    break
                elif (i + 1 == len(current_node.values)):
                    current_node = current_node.keys[i + 1]
                    break
        return current_node

    # Find the node
    def find(self, value, key):
        l = self.search(value)
        for i, item in enumerate(l.values):
            if item == value:
                if key in l.keys[i]:
                    return True
                else:
                    return False
        return False

    # Inserting at the parent
    def insert_in_parent(self, n, value, ndash):
        if (self.root == n):
            rootNode = Node(n.order)
            rootNode.values = [value]
            rootNode.keys = [n, ndash]
            self.root = rootNode
            n.parent = rootNode
            ndash.parent = rootNode
            return

        parentNode = n.parent
        temp3 = parentNode.keys
        for i in range(len(temp3)):
            if (temp3[i] == n):
                parentNode.values = parentNode.values[:i] + \
                    [value] + parentNode.values[i:]
                parentNode.keys = parentNode.keys[:i +
                                                  1] + [ndash] + parentNode.keys[i + 1:]
                if (len(parentNode.keys) > parentNode.order):
                    parentdash = Node(parentNode.order)
                    parentdash.parent = parentNode.parent
                    mid = ((parentNode.order + 1) // 2) - 1
                    parentdash.values = parentNode.values[mid + 1:]
                    parentdash.keys = parentNode.keys[mid + 1:]
                    value_ = parentNode.values[mid]
                    if (mid == 0):
                        parentNode.values = parentNode.values[:mid + 1]
                    else:
                        parentNode.values = parentNode.values[:mid]
                    parentNode.keys = parentNode.keys[:mid + 1]
                    for j in parentNode.keys:
                        j.parent = parentNode
                    for j in parentdash.keys:
                        j.parent = parentdash
                    self.insert_in_parent(parentNode, value_, parentdash)

    # Delete a node
    def delete(self, value, key):
        node_ = self.search(value)

        temp = 0
        for i, item in enumerate(node_.values):
            if item == value:
                temp = 1

                if key in node_.keys[i]:
                    if len(node_.keys[i]) > 1:
                        node_.keys[i].pop(node_.keys[i].index(key))
                    elif node_ == self.root:
                        node_.values.pop(i)
                        node_.keys.pop(i)
                    else:
                        node_.keys[i].pop(node_.keys[i].index(key))
                        del node_.keys[i]
                        node_.values.pop(node_.values.index(value))
                        self.deleteEntry(node_, value, key)
                else:
                    print("Value not in Key")
                    return
        if temp == 0:
            print("Value not in Tree")
            return

    # Delete an entry
    def deleteEntry(self, node_, value, key):

        if not node_.check_leaf:
            for i, item in enumerate(node_.keys):
                if item == key:
                    node_.keys.pop(i)
                    break
            for i, item in enumerate(node_.values):
                if item == value:
                    node_.values.pop(i)
                    break

        if self.root == node_ and len(node_.keys) == 1:
            self.root = node_.keys[0]
            node_.keys[0].parent = None
            del node_
            return
        elif (len(node_.keys) < int((node_.order + 1) // 2) and node_.check_leaf == False) or (len(node_.values) < int((node_.order // 2)) and node_.check_leaf == True):

            is_predecessor = 0
            parentNode = node_.parent
            PrevNode = -1
            NextNode = -1
            PrevK = -1
            PostK = -1
            for i, item in enumerate(parentNode.keys):

                if item == node_:
                    if i > 0:
                        PrevNode = parentNode.keys[i - 1]
                        PrevK = parentNode.values[i - 1]

                    if i < len(parentNode.keys) - 1:
                        NextNode = parentNode.keys[i + 1]
                        PostK = parentNode.values[i]

            if PrevNode == -1:
                ndash = NextNode
                value_ = PostK
            elif NextNode == -1:
                is_predecessor = 1
                ndash = PrevNode
                value_ = PrevK
            else:
                if len(node_.values) + len(NextNode.values) < node_.order:
                    ndash = NextNode
                    value_ = PostK
                else:
                    is_predecessor = 1
                    ndash = PrevNode
                    value_ = PrevK

            if len(node_.values) + len(ndash.values) < node_.order:
                if is_predecessor == 0:
                    node_, ndash = ndash, node_
                ndash.keys += node_.keys
                if not node_.check_leaf:
                    ndash.values.append(value_)
                else:
                    ndash.nextKey = node_.nextKey
                ndash.values += node_.values

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        j.parent = ndash

                self.deleteEntry(node_.parent, value_, node_)
                del node_
            else:
                if is_predecessor == 1:
                    if not node_.check_leaf:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm_1 = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [value_] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashkm_1
                                break
                    else:
                        ndashpm = ndash.keys.pop(-1)
                        ndashkm = ndash.values.pop(-1)
                        node_.keys = [ndashpm] + node_.keys
                        node_.values = [ndashkm] + node_.values
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashkm
                                break
                else:
                    if not node_.check_leaf:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [value_]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndashk0
                                break
                    else:
                        ndashp0 = ndash.keys.pop(0)
                        ndashk0 = ndash.values.pop(0)
                        node_.keys = node_.keys + [ndashp0]
                        node_.values = node_.values + [ndashk0]
                        parentNode = node_.parent
                        for i, item in enumerate(parentNode.values):
                            if item == value_:
                                parentNode.values[i] = ndash.values[0]
                                break

                if not ndash.check_leaf:
                    for j in ndash.keys:
                        j.parent = ndash
                if not node_.check_leaf:
                    for j in node_.keys:
                        j.parent = node_
                if not parentNode.check_leaf:
                    for j in parentNode.keys:
                        j.parent = parentNode


# Print the tree
def printTree(tree):
    lst = [tree.root]
    level = [0]
    leaf = None
    flag = 0
    lev_leaf = 0

    node1 = Node(str(level[0]) + str(tree.root.values))

    while (len(lst) != 0):
        x = lst.pop(0)
        lev = level.pop(0)
        if (x.check_leaf == False):
            for i, item in enumerate(x.keys):
                print(item.values)
        else:
            for i, item in enumerate(x.keys):
                print(item.values)
            if (flag == 0):
                lev_leaf = lev
                leaf = x
                flag = 1

guest_data = {
    "Hotel": [],
    "Bus": [],
    "Ship": [],
    "Fleet": []
}

# Function Group 1 - Guest Management
'''
receive_guests() เป็นฟังชันไว้จัดการ input
format input : เช่น fleet:5,4,7,10/bus:3,4
    - fleet:จำนวนกองเรือ,จำนวนเรือ,จำนวนรถบัส,จำนวนwalk-in
    - ship:จำนวนเรือ,จำนวนรถบัส,จำนวนwalk-in
    - bus:จำนวนรถบัส,จำนวนwalk-in
    - walk_in:จำนวนwalk-in

generate_room_number()
- รอฟังก์ชันนับห้อง ตอนนี้สมมุติจำนวนแขกเก่าทั้งหมด (พารามิเตอร์ old_guest )
- รอฟังก์ชัน sort เลขห้อง ตอนนี้ใช้ .sort() แทน
- return เป็น list ของ (เลขห้อง,[ช่องทางของแขก, , , ])


คิดว่า add_guest ไม่ต้องมีเพราะ 1 ห้อง มีได้ 1 คนอยู่แล้ว
เปลี่ยน add_guest เป็น add_room  (อัตโนมัติ) แทนได้เลย
เดี๋ยว Junior ทำเอง
'''
def generate_room_number(num_walk_in = 1, num_bus = 1, num_ship = 1, num_fleet = 1 , old_guest = 10): 
      room_number = []
      for o in range(old_guest) :
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
      return list_room_number

def add_room(list_room_number):
    pass
                              






# Function Group 2 - Manual Room Management
def add_room_manual(room_number, guest_info):
    pass

def remove_room_manual(room_number):
    pass

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



def search_room(room_number):
    pass

def show_available_rooms(max_room):
    pass

# Function Group 4: Performance Monitoring and Reporting
def display_memory_usage():
    pass

def write_to_file(filename="hotel_report.txt"):
    pass

def measure_time(func, *args):
    pass

def main():
    bplustree = BplusTree(3)  
    # measure_time(add_guests, "Hotel", 10)
    print(receive_guests())
    measure_time(add_room_manual, 101, "Special Guest")
    measure_time(remove_room_manual, 1)
    measure_time(sort_rooms)
    measure_time(search_room, 101)
    measure_time(show_available_rooms, 200)
    measure_time(write_to_file)
    measure_time(display_memory_usage)
    printTree(bplustree)

if __name__ == "__main__":
    main()
