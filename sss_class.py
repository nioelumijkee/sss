import pd

class SSSClass:
    def __init__( self, *creation ):
        self.global_dollarzero = int(creation[0])
        self.ins = {}
        pd.post('global_dollarzero: %d' % (self.global_dollarzero))
        return

    def init(self):
        pd.post('init.')
        self.ins = {} # clear older result !
        res = []
        res.append(['send', '%d-sss-get-info-par' % (self.global_dollarzero)])
        res.append(['msg', 'bang'])
        res.append(['send', '%d-sss-get-info-array' % (self.global_dollarzero)])
        res.append(['msg', 'bang'])
        res.append(['send', '%d-sss-loop' % (self.global_dollarzero)])
        res.append(['msg', 'list', 'after-get-info'])
        return (tuple(res))

    def list(self, *args):
        selector = args[0]
        if selector == 'get-info-par-return':
            ins_name          = str(args[1])
            ins_dollarzero    = int(args[2]) # $0 local
            global_dollarzero = int(args[3]) # $1 global
            ins_num           = int(args[4]) # $2 number
            par_num           = int(args[5])
            par_type          = str(args[6])
            par_label         = str(args[7])
            par_min           = float(args[8])
            par_max           = float(args[9])
            par_step          = float(args[10])
            if ins_num not in self.ins:
                self.ins[ins_num] = {'par':[], 'ar':[]}
                self.ins[ins_num]['ins_name'] = ins_name
                self.ins[ins_num]['ins_dollarzero'] = ins_dollarzero
            if  self.ins[ins_num]['ins_dollarzero'] != ins_dollarzero:
                pd.post('error: not unique number ins ! ins_name: %s ins_num: %d' %
                        (ins_name, ins_num))
                return
            self.ins[ins_num]['par'].append(
                [par_num, par_type, par_label, par_min, par_max, par_step])
        elif selector == 'get-info-array-return':
            ins_name          = str(args[1])
            ins_dollarzero    = int(args[2]) # $0 local
            global_dollarzero = int(args[3]) # $1 global
            ins_num           = int(args[4]) # $2 number
            ar_num            = int(args[5])
            ar_name           = str(args[6])
            if ins_num not in self.ins:
                self.ins[ins_num] = {'par':[], 'ar':[]}
                self.ins[ins_num]['ins_name'] = ins_name
                self.ins[ins_num]['ins_dollarzero'] = ins_dollarzero
            self.ins[ins_num]['ar'].append(
                [ar_num, ar_name])
        elif selector == 'after-get-info':
            pd.post('done get info')
            for i in self.ins:
                print('='*80)
                print('ins_num:',i)
                print('ins_name:', self.ins[i]['ins_name'])
                print('ins_dollarzero:', self.ins[i]['ins_dollarzero'])
                self.ins[i]['par'].sort()
                self.ins[i]['ar'].sort()
                for j in self.ins[i]['par']:
                    print('par:',j)
                for j in self.ins[i]['ar']:
                    print('ar:',j)
        elif selector == 'savestate':
            pd.post('savestate data')
        return

    def save(self):
        pd.post('save')
        return

    def save_as(self, filename):
        pd.post('save_as file: %s' % str(filename))
        return

    def open(self, filename):
        pd.post('open: %s' % str(filename))
        return

    def save_ins_as(self, filename, ins_num):
        pd.post('save_ins num: %d file: %s' % (int(ins_num), str(filename)))
        return

    def open_ins(self, filename, ins_num):
        pd.post('open_ins num: %d file: %s' % (int(ins_num), str(filename)))
        return

