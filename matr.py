from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

from numpy import matrix as npmatr
class matr(npmatr):

    def __new__(self, data = []):
        return super().__new__(self,data)

    def _frominp(inp):
        data = []
        if __debug__:
            assert hasattr(inp, '__iter__') or hasattr(inp, '__next__')
        if hasattr(inp, '__iter__'):
            for line in inp:
                data.append(line)
        elif hasattr(inp, '__next__'):
            while inp.hasnext():
                data.append(next(inp))
        return matr(data)

    def __lshift__(self, inp):
        return self.__rrshift__(inp)

    def __rlshift__(self, outp):
        return self.__rshift__(outp)

    def __rrshift__(self, inp):
        """ file >> self :: Sets self.data to the data read from inp."""
        if isinstance(inp, str):
            return csv.reader(open(inp)) >> self
        elif not hasattr(inp, '__iter__') and not hasattr(inp, '__next__'):
            return NotImplemented
        return matr._frominp(inp)

    def __rshift__(self, outp):
        if isinstance(outp, str):
            return self >> csv.writer(open(outp, 'w'))
        if __debug__:
            assert hasattr(outp, "writerow") or hasattr(outp, "write") or hasattr(outp, "writeline")
        for row in self.tolist():
            if hasattr(outp, "writerow"): #AKA, if it's a csv writer.
                outp.writerow(row)
            elif hasattr(outp, "writeline"):
                outp.write(",".join(row))
            elif hasattr(outp, "write"):
                outp.write(",".join(row) + '\n')
            else:
                return NotImplemented
        return self


def main():
    df = 'testdata.txt' >> matr()
    df >> 'testdata.txt'
if __name__ == '__main__':
    main()