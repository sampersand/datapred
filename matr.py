from warnings import warn
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
            # if type(ret) == list: #Matr is a list...
            #     ret = Matr(data = ret)
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
        return col

    def __repr__(self):
        return "Matr(file={},data={})".format(repr(self.file), super().__repr__())

    def tostr(self):
        cp = +self
        ret = 'Matrix (file = \'{}\')%n'.format(cp.file)
        def getlen(e):
            ret = []
            for x in str(e).split('\n'):
                ret.append(len(x))
            return ret
        maxc = []
        maxr = []
        for linlen in [[getlen(e) for e in col] for col in cp.cols]:
            maxc.append(max(e for lin in linlen for e in lin))
        for linlen in [[getlen(e) for e in row] for row in cp.rows]:
            maxr.append(max(len(lin) for lin in linlen))
        retbnd = '' #the --+-- stuff
        rethdr = [[] for i in range(maxr[0])] #the header
        for hdrp in range(len(cp.headers)):
            spl = str(cp.cols[hdrp, 0]).split('\n')
            for rowp in range(maxr[0]):
                rethdr[rowp].append(rowp <= len(spl) - 1 and spl[rowp] or None)
            # rethdr  += ' | {:^{}}'.format(len(cp.cols[hdrp]), maxl[hdrp])
            # hdrs = str(cp.headers[hdrp]).split('\n')
            # reta.append(' | {:^{}}'.format(hdrs[linep], maxl[hdrp]))
            print(maxc[hdrp], max(len(e) for e in spl), spl)
            retbnd += '-+-{:->{}}'.format('', maxc[hdrp])
        ret += '\n ' + retbnd[1:] + '+\n'
        rethdr2 = ['' for i in range(len(rethdr))]
        for lin in range(len(rethdr)):
            for ele in range(len(rethdr[lin])):
                rethdr2[lin] += ' | {:^{}}'.format(rethdr[lin][ele] or '', maxc[ele])
        ret += '|\n'.join(rethdr2) + "|"
        ret += '\n ' + retbnd[1:] + '+\n'
        # maxl = [max([len(str(e)) for e in col]) for col in cp.cols]
        # retb = ''
        # for hdrp in range(len(cp.headers)): #should be
        #     ret  += ' | {:^{}}'.format(len(cp.cols[hdrp]), maxl[hdrp])
        #     hdrs = str(cp.headers[hdrp]).split('\n')
        #     reta.append(' | {:^{}}'.format(hdrs[linep], maxl[hdrp]))
        #     retb += '-+-' + '-' * (maxl[hdrp][0])
        # retb = '-----' + retb[1:] + '-+'
        # print(reta)
        # ret = ret + ' |%n' + retb + '%n {:^3} '.format(len(cp.headers)) + reta[1:] + ' |%n' + retb + '%n'
        # for row in cp[1:]:
        #     ret += ' {:^3} | '.format(len(row))
        #     for colp in range(len(row)):
        #         ret += '{:^{}} | '.format(str(row[colp]), maxl[colp][0])

        #     ret = ret + '%n'
        # return ret + retb
        return ret
    def __str__(self):
        return self.tostr().replace('%n','\n')


    def __pos__(self):
        import copy
        ret = copy.copy(self)
        for row in ret:
            if __debug__:
                assert len(row) <= len(ret.headers), 'header needs to be larger or equal to all! ({},{})'.\
                    format(row, ret.headers)
            for i in range(len(ret.headers) - len(row)):
                row.append(None)
        return ret

    def __contains__(self, val):
        return val in self.ids or super().__contains__(val)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if type != None:
            raise
        elif self.file != None:
            self >> self.file
        return True

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
    def fromfile(fin, dtype = None, skipchar = '#', splitchar = ','):
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
        for line in fin:
            if not isinstance(line, list):
                if __debug__:
                    assert isinstance(line, str)
                assert 0, repr(ret)#line = line.split(splitchar)
            if __debug__:
                if len(line[0]) == 0:
                    line[0] = 'None'
            if not line[0][0] == skipchar:
                data.append(Matr())
                for val in line:
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
            row = [repr(ele) for ele in row]
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
        return self[0]

    @property
    def ids(self):
        return [row[0] for row in self][1:]

class T:
    def __init__(self):
        pass
    def __str__(self):
        return '1ab\n2cd\nef23'
    def __repr__(self):
        return "T()"

def main():
    with Matr('testdata.txt') as m:
        # m['id3',-1] = Matr(data=[[1]])
        print(m)
    # m = 'testdata.txt' >> Matr()
    # print(repr(m))
    # m['id3', -1] = 99
    # m >> 'testdata.txt'
if __name__ == '__main__':
    main()







