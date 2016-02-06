from numpy import matrix as npmatr
class matrfile:

    def __init__(self, datainp):
        self.data = matrfile.readdata(datainp)

    @staticmethod
    def readdata(datainp):
        data = npmatr([''])
        if __debug__:
            assert hasattr(datainp, "__next__")
            assert hasattr(datainp, "__iter__")
        print(datainp)


df = matrfile(open("testdata.txt", "r"))
        