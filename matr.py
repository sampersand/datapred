from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

class Matr:

    class _RowClass(list):
        def __new__(self, matr, iterable):
            return super().__new__(self, iterable)

        def __init__(self, matr, iterable):
            super().__init__(iterable)
            self.matr = matr

        def __getitem__(self, val):
            if isinstance(val, slice):
                assert 0
            return super().__getitem__(\
        self.matr.header.index(val) if isinstance(val, str) else val)

    def __init__(self,
                 file = None,
                 header = None,
                 data = None,
                 valtype = float,
                 hdrtype = str,
                 idtype = str):

        """ if you pass a file to it, it will only read it if there is no header or data"""

        self.file = file
        if self.file and not (header or data):
            matr = Matr.fromfile(file)
            self.header = matr.header
            self.data = matr.data
        else:
            self.header = header
            self.data = data
        self.valtype = valtype
        self.hdrtype = hdrtype
        self.idtype = idtype

    @staticmethod
    def fromfile(fin,
                 valtype = float,
                 hdrtype = str,
                 idtype = str,
                 hasheader = True,
                 hasIds = True,
                 skipchar = '#',
                 splitchar = ','):
        """ splitchar is only when no csv """
        file = None
        import io
        if isinstance(fin, str):
            file = fin
            fin = csv.reader(open(fin, 'r'))
        elif isinstance(fin, io.IOBase):
            file = fin.name
            fin = csv.reader(fin)
        del io
        if __debug__:
            assert hasattr(fin, '__iter__'), 'cannot iterate over type \'{}\'!'.format(type(fin))
        idn = 0

        if hasheader:
            header = [hdrtype(colname) for colname in next(fin)][hasIds:]
        data = {}

        retmatr = Matr(valtype = valtype, hdrtype = hdrtype, idtype = idtype)
        retmatr.file = file
        for line in fin:
            if not isinstance(line, list):
                if __debug__:
                    assert isinstance(line, str)
                line = line.split(splitchar)

            if not hasIds:
                line.insert(0, str(idn))
            if not line[0][0] == skipchar:
                data[(idtype(line[0]), idn)] = Matr._RowClass(retmatr, [valtype(val) for val in line[1:]])
            idn += 1

        if not hasheader:
            header = [hdrtype(pos) for pos in range(len(tuple(data.values())[0]))]

        retmatr.header = header
        retmatr.data = data
        return retmatr


    # def __iter__(self, axis=0):
    #     for a in range():
    def __repr__(self):
        return 'Matr(file={}, header={}, data={})'.format(repr(self.file), repr(self.header), repr(self.data))

    def __str__(self):
        ret = 'Matrix for file \'{}\''.format(self.file)
        maxls = (max() for col in self.cols)
        print(maxls)
        return ret

    def __lshift__(self, fout):
        return self.__rrshift__(fout)

    def __rlshift__(self, fout):
        return self.__rshift__(fout)

    def __rrshift__(self, fin):
        """ fin >> self :: Sets self to the Matrix read from the input file"""
        return self.fromfile(fin)

    def __rshift__(self, fout):
        """ self >> fout :: writes self to fout, """
        return self.tofile(fout)

    def __getitem__(self, val, useindexing = None):
        if useindexing == None:
            useindexing = not hasattr(self.idtype, '__int__')
        if __debug__:
            assert not isinstance(val, tuple) or len(val) == 2, \
            'val needs to be (row, col) or just row\n' + str(val)
        row, col = isinstance(val, tuple) and val or (val, slice(None))

        for rowkey in self.data.keys():
            if self.idtype(row) == rowkey[0] or useindexing and int(row) == rowkey[1]:
                return self.data[rowkey]
        return None

    # def __setitem__(self, val, toset):
    #     return super().__setitem__(self._transrowcol(*val if isinstance(val, tuple) else (val, slice(None))), toset)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print('todo: __exit__')
        if type is None:
            pass
            # if self.file != None:
                # return self.tofile()
        else:
            raise #type(value, traceback)
        return True

    def _transrowcol(self, row, col = slice(None)):
        """ translates rows and columns into their respective strings..."""
        try:
            if isinstance(row, str):
                row = self[:, 0].flatten().tolist()[0].index(row)
            if isinstance(col, str):
                col = self[0, ].flatten().tolist()[0].index(col)
            return (row, col)
        except ValueError:
            raise

    def tofile(self, fout = None):
        if fout == None:
            fout = self.file
        if isinstance(fout, str):
            return self.tofile(csv.writer(open(fout, 'w')))
        if __debug__:
            assert hasattr(fout, "writerow") or hasattr(fout, "write") or hasattr(fout, "writeline")
        for row in self:
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
    # with Matr('testdata.txt') as m:
        # print(m[0])
    m = 'testdata.txt' >> Matr()
    # m.tofile()
    print(m[0,:])
if __name__ == '__main__':
    main()







