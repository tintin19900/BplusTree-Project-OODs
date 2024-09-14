import math

n = 106
mid = ((n + 1) // 2) - 1
half = int(math.ceil(n / 2)) - 1
print(f"Older value 1: {mid}")
print(f"Older value 2: {half}")

mid = ((n + 1) // 2) - 1
half = int(math.ceil(n / 2)) - 1
print(f"Parent value 1 : {mid}")
print(f"Parent value 2 : {half}")

a = 612544
mid = int(math.ceil(a / 2))
half = (a + 1) // 2
print(f"Er value 1 : {mid}")
print(f"Er value 2 : {half}")
mid = int(math.ceil((a - 1) / 2))
half = (a // 2)
print(f"Error value 1 : {mid}")
print(f"Error value 2 : {half}")