from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

from numpy import matrix as npmatr
class matr(npmatr):

    defaultskipchar = '#'

    def __new__(self, file = None, dtype = float, data = [], skipchar = None):
        if file:
            ret = matr().fromfile(file, dtype = dtype)
        else:
            ret = super().__new__(self, data)    
        ret.file = file
        return ret

    def __str__(self):
        return 'file \'{}\':\n{}'.format(self.file, super().__str__())

    def __lshift__(self, fout):
        return self.__rrshift__(fout)

    def __rlshift__(self, fout):
        return self.__rshift__(fout)

    def __rrshift__(self, fin):
        """ fin >> self :: Sets self to the matrix read from the input file"""
        return self.fromfile(fin)

    def __rshift__(self, fout):
        """ self >> fout :: writes self to fout, """
        return self.tofile(fout)

    def __getitem__(self, val):
        return super().__getitem__(self._transrowcol(*val if isinstance(val, tuple) else (val, slice(None))))

    def __setitem__(self, val, toset):
        return super().__setitem__(self._transrowcol(*val if isinstance(val, tuple) else (val, slice(None))), toset)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            if self.file != None:
                return self.__rshift__(self.file)
        else:
            raise type(value, traceback)
        return True

    def _npmatrfromfile(fin, skipchar, dtype):
        mdata = []
        if __debug__:
            assert hasattr(fin, '__iter__') or hasattr(fin, '__next__')
        if hasattr(fin, '__iter__'):
            for line in fin:
                if not line[0][0] == skipchar:
                    mdata.append([dtype(ele) for ele in line])
        elif hasattr(fin, '__next__'):
            while fin.hasnext():
                line = next(fin)
                if not line[0] == skipchar:
                    mdata.append(line)
        return mdata

    def _transrowcol(self, row, col=slice(None)):
        """ translates rows and columns into their respective strings..."""
        try:
            if isinstance(row, str):
                row = self[:,0].flatten().tolist()[0].index(row)
            if isinstance(col, str):
                col = self[0,].flatten().tolist()[0].index(col)
            return (row, col)
        except ValueError:
            raise

    def fromfile(self, fin, skipchar = None, dtype = None):
        if isinstance(fin, str):
            ret = self.fromfile(csv.reader(open(fin)))
            ret.file = fin #its a string
            return ret
        elif not hasattr(fin, '__iter__') and not hasattr(fin, '__next__'):
            return NotImplemented
        return matr(data = matr._npmatrfromfile(fin, skipchar or matr.defaultskipchar, dtype))

    def tofile(self, fout):
        if isinstance(fout, str):
            return self.tofile(csv.writer(open(fout, 'w')))
        if __debug__:
            assert hasattr(fout, "writerow") or hasattr(fout, "write") or hasattr(fout, "writeline")
        for row in self.tolist():
            if hasattr(fout, "writerow"): #AKA, if it's a csv writer.
                fout.writerow(row)
            elif hasattr(fout, "writeline"):
                fout.write(",".join(row))
            elif hasattr(fout, "write"):
                fout.write(",".join(row) + '\n')
            else:
                return NotImplemented
        return self


def main():
    with matr('testdata.txt') as m:
        # m2 = npmatr('1,2,3;4,5,6;7,8,9')
        print(m)
        # print(m+m2)
        # print(m2)
if __name__ == '__main__':
    main()







