def pr(l):
    return '\n'.join((', '.join('{:2}'.format(e) for e in r) for r in l))
def c(lis):
    ret = []
    for col in range(len(lis[0])):
        ret.append([])
        for row in range(len(lis)):
            ret[col].append(lis[row][col])
    return ret
l = [[0x1,0x2,0x3,0x4],\
     [0x0,-0x6,-0x7,0x8],\
     [0x9,0x10,0xA,0xB]]
# l = [[0x1,0x2,0x3,0x4],\
#      [0x5,0x6,0x7,0x8],\
#      [0x9,0x10,0xA,0xB]]
# l1 = []
l1 = c(l)
print(pr(l),pr(l1), sep='\n\n')
# class C:
#     def __init__(self, v):
#         print('__init__<', v, '>')
#         self.v = v
#
#     def __str__(self):
#         return 'C.v = ' + str(self.v)
#
#     def __sub__(self, b):
#         print('__sub__[', b, ']')
#         return C(self.v - b.v)
#
#     def __getattr__(self, attr):
#         print('__getattr__{', attr, '}')
#         return super().__getattr__(attr)
#
#     def __getattribute__(self, attribute):
#         print('__getattribute__(', attribute, ')')
#         return super().__getattribute__(attribute)
#
# c1 = C(9)
# c2 = C(4)
#
# c3 = c1.__sub__(c2) # this calls '__getattribute__'
#
# c4 = c1 - c2 # this calls neither '__getattr__' nor '__getattribute__', but succeeds because '__sub__' is defined.
#              # Why doesn't it call either?
#
# c5 = c1 + c2 # this calls neither '__getattr__' nor '__getattribute__', but fails because '__add__' isn't defined.
#              # Why doesn't it call either?
# c1.a # this calls '__getattribute__', and then goes to '__getattr__'