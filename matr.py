from warnings import warn
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

class Matr(list):

    def __new__(self, file = None, data = [], dtype = float):
        return super().__new__(self, data)

    def __init__(self, file = None, data = [], dtype = float):
        super().__init__(Matr.fromfile(file, dtype = dtype) if file and not data else data)
        self.file = file
        self.dtype = dtype

    def __getitem__(self, val):
        row, col = isinstance(val, tuple) and val or (val, slice(None))
        row = self.indrow(row)
        col = self.indcol(col)
        return super().__getitem__(row).__getitem__(col)

    def indrow(self, row):
        if isinstance(row, slice):
            return slice(self.indrow(row.start), self.indrow(row.stop), self.indrow(row.step))
        if isinstance(row, int):
            return row
        for i in range(self.rows):
            if row == self[i,0]:
                return i
        return row
    def indcol(self, col):
        if isinstance(col, slice):
            return slice(self.indcol(col.start), self.indcol(col.stop), self.indcol(col.step))
        if isinstance(col, int):
            return col
        for i in range(self.cols):
            if col == self[0,i]:
                return i
        return col

    # def __getitem__(self, val, useindexing = None):
    #     if useindexing == None:
    #         useindexing = not hasattr(self.idtype, '__int__')
    #     if __debug__:
    #         assert not isinstance(val, tuple) or len(val) == 2, \
    #         'val needs to be (row, col) or just row\n' + str(val)
    #     print(row,col)
    #     print(self)
    #     for rowkey in self.data.keys():
    #         if self.idtype(row) == rowkey.id or useindexing and int(row) == rowkey.pos:
    #             return self.data[rowkey]
    #     return None



    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type != None:
            raise
        elif self.file != None:
            self >> self.file
        return True

    @property
    def rows(self):
        return len(self)

    @property
    def cols(self):
        return len(super().__getitem__(0))
    
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

    @staticmethod
    def fromfile(fin,
                 dtype = float,
                 hasheader = True,
                 hasIds = True,
                 skipchar = '#',
                 splitchar = ','):
        """ splitchar is only when no csv """
        import io
        if isinstance(fin, str):
            file = fin
            fin = csv.reader(open(fin, 'r'))
        elif isinstance(fin, io.IOBase):
            file = fin.name
            fin = csv.reader(fin)
        else:
            raise TypeError("No known way to read from file type '%s'." % type(fin))
        del io

        if __debug__:
            assert hasattr(fin, '__iter__'), 'cannot iterate over type \'{}\'!'.format(type(fin))

        data = []
        for line in fin:
            if not isinstance(line, list):
                if __debug__:
                    assert isinstance(line, str)
                line = line.split(splitchar)

            if not hasIds:
                line.insert(0, str(idn))

            if not line[0][0] == skipchar:
                data.append([])
                for val in line:
                    try:
                        data[-1].append(dtype(val))
                    except ValueError:
                        data[-1].append(str(val))
        return Matr(file = file, data = data)

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
    with Matr('testdata.txt') as m:
        print(m[1:])
    # sm.tofile()
if __name__ == '__main__':
    main()







