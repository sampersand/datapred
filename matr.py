from warnings import warn
import copy
try:
    import csv
except ImportError:
    warn('module \'csv\' could not be imported!')

class Matr(list):

    def __new__(self, file = None, data = []):
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
        for i in range(len(self.rows)):
            if row == self[i,0]:
                return i
        warn(str(row) + ' is not in the list of valid ids! ' + repr(self.ids))
        return row
    def indcol(self, col):
        if isinstance(col, slice):
            return slice(self.indcol(col.start),\
                         self.indcol(col.stop),\
                         self.indcol(col.step))
        if isinstance(col, int):
            return col
        for i in range(len(self.cols)):
            if col == self[0, i]:
                return i
        warn(str(col) + ' is not in the list of valid headers! ' + repr(self.headers))
        return col

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

        return ret + boldboundries

    def __pos__(self):
        ret = copy.deepcopy(self)
        for row in ret:
            if __debug__:
                assert hasattr(row, '__iter__'), repr(row) + " | " + repr(ret)
                assert len(row) <= len(ret.headers), 'header needs to be larger or equal to all! ({},{})'.\
                    format(row, ret.headers)
            for i in range(len(ret.headers) - len(row)):
                row.append(None)
        return ret

    def __contains__(self, val):
        """ checks if val is an id, or if super().__contains__(val) is true """
        return val in self.ids or super().__contains__(val)

    def __enter__(self):
        """ just returns self"""
        return self
    def __exit__(self, type, value, traceback):
        if type != None:
            raise
        elif self.file != None:
            self >> self.file
        return True


    def _dofunc(self, other, function):
        if not (hasattr(other, '__iter__') or hasattr(other, function)):
            return NotImplemented
        ret = copy.deepcopy(self)
        if hasattr(other, '__iter__'):
            pass
        else:
            for rowp in range(1,len(ret.rows)): #skip header
                for colp in range(1, len(ret[rowp])): #skip id
                    try:
                        attr = getattr(ret[rowp, colp],function)(other)
                        if attr == NotImplemented:
                            raise TypeError
                        ret[rowp, colp] = attr
                    except (TypeError, AttributeError):
                        warn("skipping element '{}' because there is no known way to apply '{}' on it and type '{}'".\
                             format(ret[rowp, colp], function, type(other)))
        return ret

    def __add__(self, other):  return self._dofunc(other, '__add__')
    def __radd__(self, other): return self._dofunc(other, '__radd__')
    def __iadd__(self, other): return self._dofunc(other, '__addi__')

    def __sub__(self, other):  return self._dofunc(other, '__sub__')
    def __rsub__(self, other): return self._dofunc(other, '__rsub__')
    def __isub__(self, other): return self._dofunc(other, '__subi__')

    def __div__(self, other):  return self._dofunc(other, '__div__')
    def __rdiv__(self, other): return self._dofunc(other, '__rdiv__')
    def __idiv__(self, other): return self._dofunc(other, '__divi__')

    def __mul__(self, other):  return self._dofunc(other, '__mul__')
    def __rmul__(self, other): return self._dofunc(other, '__rmul__')
    def __imul__(self, other): return self._dofunc(other, '__muli__')

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
        return [row[0] for row in self][1:] #0 is names

def main():
    m1 = 'testdata.txt' >> Matr()
    # m1['id2', 'h2']['1','h3'] = Matr(data=[[1,2]])
    m2 = 'testdata2.txt' >> Matr()
    # print(m1)
    # print(m2)
    m1 += 100
    m1 *= 1/100
    print(str(100 + m1))
if __name__ == '__main__':
    main()







