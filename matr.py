from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

from numpy import matrix as npmatr
class matr(npmatr):

    defaultskipchar = '#'

    def __new__(self, file = None, data = [], skipchar = None):
        if file:
            ret = matr().__rrshift__(file)
        else:
            ret = super().__new__(self, data)    
        ret.file = file
        return ret

    def __str__(self):
        return 'file \'{}\':\n{}'.format(self.file, super().__str__())
    def __lshift__(self, inp):
        return self.__rrshift__(inp)

    def __rlshift__(self, outp):
        return self.__rshift__(outp)

    def __rrshift__(self, iterable, skipchar = None):
        """ inputfile >> self :: Sets self to the matrix read from the input file"""
        if isinstance(iterable, str):
            ret = self.__rrshift__(csv.reader(open(iterable)))
            ret.file = iterable #its a string
            return ret
        elif not hasattr(iterable, '__iter__') and not hasattr(iterable, '__next__'):
            return NotImplemented
        return matr(data = matr._npmatrfromfile(iterable, skipchar or matr.defaultskipchar))

    def __rshift__(self, outp):
        """ self >> outputfile :: writes self to outputfile, """
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

    def __getitem__(self, val):
        return super().__getitem__(self._transrowcol(*val if isinstance(val, tuple) else (val, slice(None))))

    def __setitem__(self, val, toset):
        return super().__setitem__(self._transrowcol(*val if isinstance(val, tuple) else (val, slice(None))), toset)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type is None and self.file != None:
            return self.__rshift__(self.file)
        return True

    def __invert__(self):
        pass

    def _npmatrfromfile(iterable, skipchar):
        mdata = []
        if __debug__:
            assert hasattr(iterable, '__iter__') or hasattr(iterable, '__next__')
        if hasattr(iterable, '__iter__'):
            for line in iterable:
                if not line[0][0] == skipchar:
                    mdata.append(line)
        elif hasattr(iterable, '__next__'):
            while iterable.hasnext():
                line = next(iterable)
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

def main():
    with matr('testdata.txt') as m:
        print(~m)
if __name__ == '__main__':
    main()







