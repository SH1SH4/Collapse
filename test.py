class Ochko:
    def __init__(self):
        self.y = 10

a = [Ochko() for _ in range(10)]
for i in range(len(a)):
    a[i].y -= i
for i in a:
    print(i.y)