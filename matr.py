from warnings import warn
import copy
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

class Matr(list):

    def __new__(self, file = None, data = []):
        """ because if extending list, it needs __new__"""
        return super().__new__(self, data)
    def __init__(self, file = None, data = []):
        if file and not data:
            super().__init__(Matr.fromfile(file))
        else:
            super().__init__(data)
        self.file = file

    def __getitem__(self, pos):
        if not isinstance(pos, tuple):
            ret = super().__getitem__(self.indrow(pos))
        else:
            if __debug__:
                assert len(pos) == 2, 'cant have a getitem of length more than 2! ' + str(pos)
            ret = super().__getitem__(self.indrow(pos[0])).__getitem__(self.indcol(pos[1]))
        return ret      
    def __delitem__(self, pos):
        if not isinstance(pos, tuple):
            ret = super().__delitem__(self.indrow(pos))
        else:
            if __debug__:
                assert len(pos) == 2, 'cant have a getitem of length more than 2! ' + str(pos)
            ret = super().__getitem__(self.indrow(pos[0])).__delitem__(self.indcol(pos[1]))
        return ret
    def __setitem__(self, pos, val):
        if not isinstance(pos, tuple):
            super().__setitem__(self.indrow(pos), val)
        else:
            if __debug__:
                assert len(pos) == 2, 'cant have a getitem of length more than 2! ' + str(pos)
            super().__getitem__(self.indrow(pos[0])).__setitem__(self.indcol(pos[1]), val)

    def indrow(self, row):
        if isinstance(row, slice):
            return slice(self.indrow(row.start),\
                         self.indrow(row.stop),\
                         self.indrow(row.step))
        if isinstance(row, int):
            return row
        if row in self.ids:
            return self.ids.index(row)
        if row == None:
            return row
        raise IndexError(str(row) + ' is not in the list of valid ids! ' + repr(self.ids))
    def indcol(self, col):
        if isinstance(col, slice):
            return slice(self.indcol(col.start),\
                         self.indcol(col.stop),\
                         self.indcol(col.step))
        if isinstance(col, int):
            return col
        if col in self.headers:
            return self.headers.index(col)
        if col == None:
            return col
        raise IndexError(str(col) + ' is not in the list of valid headers! ' + repr(self.headers))

    def __repr__(self):
        """ """
        return "Matr(file={},data={})".format(repr(self.file), super().__repr__())
    def __str__(self):
        cp = +self
        ret = 'Matrix (file = \'{}\')'.format(cp.file)
        def getlen(e):
            ret = []
            for x in str(e).split('\n'):
                ret.append(len(x))
            return ret
        if len(cp) == 0:
            return ret

        maxc = []
        maxr = []

        for linlen in [[getlen(e) for e in col] for col in cp.cols]:
            maxc.append(max(e for lin in linlen for e in lin))
        for linlen in [[getlen(e) for e in row] for row in cp.rows]:
            maxr.append(max(len(lin) for lin in linlen))

        boundries = '' #the --+-- stuff

        #header
        rethdr = [[] for i in range(maxr[0])] #the header

        for hdrp in range(len(cp.headers)):
            spl = str(cp.cols[hdrp, 0]).split('\n')
            for rowp in range(maxr[0]):
                rethdr[rowp].append(spl[rowp] if rowp < len(spl) else None)
            boundries += '-+-{:->{}}'.format('', maxc[hdrp])

        boundries = '\n ' + boundries[1:] + '-+\n'
        boldboundries = boundries.replace('-','=').replace('+','*')

        rethdr2 = ['' for i in range(len(rethdr))]

        for lin in range(len(rethdr)):
            for ele in range(len(rethdr[lin])):
                rethdr2[lin] += ' | {:^{}}'.format(rethdr[lin][ele] if rethdr[lin][ele] != None else '', maxc[ele])
        ret += boldboundries + ' |\n'.join(rethdr2) + ' |' + boldboundries

        #data
        retdata = [[[] for i in range(maxr[rowp + 1])] for rowp in range(len(maxr[1:]))] #the data. maxr[0] is header
        for rowp in range(1, len(cp)): #row position
            for colp in range(len(cp[rowp])): #col position
                spl = str(cp[rowp, colp]).split('\n')
                for colp2 in range(maxr[rowp]):
                    retdata[rowp - 1][colp2].append((spl[colp2] if spl[colp2] != str(None) else None)\
                        if colp2 < len(spl) else None)

        retdata2 = [['' for i in range(len(row))] for row in retdata] 

        for rowp in range(len(retdata)):
            for colp in range(len(retdata[rowp])):
                ele = retdata[rowp][colp]
                for rowp2 in range(len(ele)):
                    retdata2[rowp][colp] += ' | {:^{}}'.format(ele[rowp2] if ele[rowp2] != None else '', maxc[rowp2])
        ret += ' |{}'.format(boundries).join([' |\n'.join(row) for row in retdata2]) + ' |'

        return ret + boldboundries[:-1]

    def __pos__(self):
        """ fill empty slots with None """
        ret = copy.deepcopy(self)
        for row in ret:
            if __debug__:
                assert hasattr(row, '__iter__'), repr(row) + " | " + repr(ret)
                assert len(row) <= len(ret.headers), 'header needs to be larger or equal to all! ({},{})'.\
                    format(row, ret.headers)
            for i in range(len(ret.headers) - len(row)):
                row.append(None)
        return ret
    def __neg__(self):
        """ strips rows with None values in them """
        return self.strip()
    def __invert__(self):
        """ strips cols with None values in them """
        return self.strip(axis = 1)

    def strip(self, axis = 0, docopy = True):
        self = +self
        if docopy:
            self = copy.deepcopy(self)
        if axis:
            colp = 0
            while colp < len(self.cols):
                if [1 for row in self if row[colp] == None]:
                    for row in self: del row[colp]
                    colp -= 1
                colp += 1
        else:
            rowp = 0
            while rowp < len(self.rows):
                if [1 for col in self[rowp] if col == None]:
                    del self[rowp]
                    rowp -= 1
                rowp += 1
        return self

    def __contains__(self, val):
        """ checks if val is an id, or if super().__contains__(val) is true """
        return val in self.ids or super().__contains__(val)

    def __reversed__(self):
        """ [ n , h1, h2, h3   --> [h3, h2, h1, n
              i1,  a,  b,  c ]       c,  b,  a, i1 ] """
        return Matr(file = self.file, data = [[e for e in reversed(r)] for r in self])

    def __enter__(self):
        """ just returns self"""
        return self
    def __exit__(self, type, value, traceback):
        if type != None:
            raise
        elif self.file != None:
            self >> self.file
        return True

    def applyFunc(self, other, function, docopy = True, recursive = True):
        if not (hasattr(other, '__iter__') or hasattr(other, function)):
            return NotImplemented
        if docopy:
            self = copy.deepcopy(self)
        if hasattr(other, '__iter__'):
            if __debug__:
                assert isinstance(other, Matr), "currently, type {} isn't supported for function '{}'".\
                    format(type(other), function)
            for header in other.headers:
                if header not in self.headers:
                    self.headers.append(header)
            for orow in other.rows[1:]:
                if orow[0] in self:
                    for colp in range(1, len(orow)):
                        try:
                            socol = self.indcol(other.headers[colp]) #self other col
                            self[orow[0]] = [self[orow[0], i] if i < len(self[orow[0]]) else None for i in range(len(self.headers))]
                            sele = self[orow[0], other.headers[colp]]
                            oele = orow[colp]
                            if sele == None or oele == None:
                                if sele == None:
                                    self[orow[0], other.headers[colp]] = oele
                                continue
                            if isinstance(ele, Matr) and recursive:
                                typ = Matr
                            else:
                                typ = type(ele + other) #coersion                            # typ = type(sele + oele) #coersion
                            if isinstance(typ, str) and not isinstance(sele, str):
                                raise TypeError
                            attr = getattr(typ(sele),function)(typ(oele))
                            if attr == NotImplemented:
                                raise TypeError
                            self[orow[0], other.headers[colp]] = attr
                        except (TypeError, AttributeError):
                            warn("skipping element '{}' because there is no known way to apply '{}' on it and type '{}'".\
                                 format(self[orow[0], other.headers[colp]], function, type(other)))

                else:
                    self.append(orow)
        else:
            for rowp in range(1,len(self.rows)): #skip header
                for colp in range(1, len(self[rowp])): #skip id
                    try:
                        ele = self[rowp, colp]
                        if isinstance(ele, Matr) and recursive:
                            typ = Matr
                        else:
                            typ = type(ele + other) #coersion
                        if isinstance(typ, str) and not isinstance(ele, str):
                            raise TypeError
                        attr = getattr(typ(ele),function)(typ(other))
                        if attr == NotImplemented:
                            raise TypeError
                        self[rowp, colp] = attr
                    except (TypeError, AttributeError):
                        warn("skipping element '{}' because there is no known way to apply '{}' on it and type '{}'".\
                             format(self[rowp, colp], function, type(other)))
        return self

    def __add__(self, other):       return self.applyFunc(other, '__add__')
    def __iadd__(self, other):      return self.applyFunc(other, '__add__', False)

    def __sub__(self, other):       return self.applyFunc(other, '__sub__')
    def __isub__(self, other):      return self.applyFunc(other, '__sub__', False)

    def __div__(self, other):       return self.applyFunc(other, '__div__')
    def __idiv__(self, other):      return self.applyFunc(other, '__div__', False)

    def __mul__(self, other):       return self.applyFunc(other, '__mul__')
    def __imul__(self, other):      return self.applyFunc(other, '__mul__', False)

    def __floordiv__(self, other):  return self.applyFunc(other, '__floordiv__')
    def __ifloordiv__(self, other): return self.applyFunc(other, '__floordiv__', False)

    def __pow__(self, other):       return self.applyFunc(other, '__pow__')
    def __ipow__(self, other):      return self.applyFunc(other, '__pow__', False)

    def __or__(self, other):        return self.applyFunc(other, '__or__')
    def __ior__(self, other):       return self.applyFunc(other, '__or__', False)

    def __and__(self, other):       return self.applyFunc(other, '__and__')
    def __iand__(self, other):      return self.applyFunc(other, '__and__', False)

    def __xor__(self, other):       return self.applyFunc(other, '__xor__')
    def __ixor__(self, other):      return self.applyFunc(other, '__xor__', False)

    def __lshift__(self, fout):
        """ self << fin :: Sets self to the Matrix read from the input file"""
        return self.__rrshift__(fout)
    def __rlshift__(self, fout):
        """ fout >> self :: writes self to fout, """
        return self.__rshift__(fout)
    def __rrshift__(self, fin):
        """ fin >> self :: Sets self to the Matrix read from the input file"""
        return self.fromfile(fin)
    def __rshift__(self, fout):
        """ self >> fout :: writes self to fout, """
        return self.tofile(fout)

    @staticmethod
    def fromfile(fin, dtype = None, hasIds = True, skipchar = '#', splitchar = ','):
        """ splitchar is only when no csv """
        import io
        if isinstance(fin, str):
            file = fin
            fin = csv.reader(open(fin, 'r'))
        elif isinstance(fin, io.IOBase):
            file = fin.name
            fin = csv.reader(fin)
        else:
            raise TypeError('No known way to read from file type \'%s\'.' % type(fin))
        del io

        if __debug__:
            assert hasattr(fin, '__iter__'), 'Cannot iterate over type \'{}\'!'.format(type(fin))

        data = []
        dtypes = dtype if hasattr(dtype, '__getitem__') else [dtype] if dtype else [int, float, complex, str]
        if not hasIds:
            idpos = 0
        for line in fin:
            if len(line) == 0:
                data.append([])
                continue
            if __debug__:
                if len(line[0]) == 0:
                    line[0] = 'None'
            if not line[0][0] == skipchar:
                data.append([]) #could be Matr(), but i thought bad idea
                if not hasIds:
                    data[-1].append('id' + str(idpos))
                    idpos+=1
                for val in line:
                    val = val.strip()
                    for datatype in dtypes:
                        try:
                            data[-1].append(None if val == '' else eval(val)) #eval isn't the best idea, lol
                            break
                        except NameError:
                            try:
                                data[-1].append(datatype(val))
                                break
                            except ValueError:
                                if dtypes[-1] == datatype:
                                    warn('No known way to coerce \'{}\' into {}!'.format(val, dtypes))
                                    data[-1].append(val)
        return Matr(file = file, data = data)
    def tofile(self, fout = None):
        if fout == None:
            fout = self.file
        if isinstance(fout, str):
            fout = csv.writer(open(fout, 'w'))
        if __debug__:
            assert hasattr(fout, 'writerow') or hasattr(fout, 'write') or hasattr(fout, 'writeline')
        for row in self:
            row = [repr(ele if ele != None else '') for ele in row]
            if hasattr(fout, 'writerow'): #AKA, if it's a csv writer.
                fout.writerow(row)
            elif hasattr(fout, 'writeline'):
                fout.write(','.join(row))
            elif hasattr(fout, 'write'):
                fout.write(','.join(row) + '\n')
            else:
                return NotImplemented
        return self

    @property
    def rows(self):
        """ is just self"""
        return self
    @property
    def cols(self):
        self = +self
        ret = Matr()
        for col in range(len(self.headers)):
            ret.append(Matr())
            for row in range(len(self.rows)):
                ret[col].append(self[row,col])
        return ret

    @property
    def headers(self):
        """ headers of the columns"""
        return self[0]
    @property
    def ids(self):
        """ identifiers of rows"""
        return [row[0] for row in self]
    
    @property
    def Tx(self):
        """ Transpose of X axis """
        return reversed(self)
    @property
    def Ty(self):
        """ Transpose of Y axis """
        return Matr(file = self.file, data = super().__reversed__())
    @property
    def Txy(self):
        """ Transpose of Y axis """
        return self.Tx.Ty

def main():
    m1 = Matr.fromfile(open('testdata.txt'))
    # m1 = 'testdata.txt' >> Matr()
    m2 = 'testdata2.txt' >> Matr()
    print(m2.Tx,sep='\n\n')
    # m3 = m1 + m2
    # print(m1 + 100)
    # print(m3, -m3, +m3, m3.strip(1), reversed(m3), sep='\n\n')

if __name__ == '__main__':
    main()







