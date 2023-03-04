import pd
import os

# ============================================================================ #
class SSSClass:
    def __init__(self, *creation):
        print('__init__')
        self.Globalzero = int(creation[0])
        self.Focus = -1
        self.Abs_name = ''
        self.Path = ''
        self.Path_allpro = ''
        self.Path_allsnap = ''
        self.Path_pro = ''
        self.Pro_name = 'default'
        self.Ins = {}
        # send names
        return
    
    # create and check path's
    def get_path(self):
        print('get_path')
        try:
            p = os.environ['PD_SSS']
        except:
            print('error: env PD_SSS not set')
            return
        if not open_or_create(p):
            return
        else:
            self.Path = p

        p = self.Path + '/pro'
        if not open_or_create(p):
            return
        else:
            self.Path_allpro = p

        p = self.Path + '/snap'
        if not open_or_create(p):
            return
        else:
            self.Path_allsnap = p

        p = self.Path + '/pro/' + self.Abs_name
        if not open_or_create(p):
            return
        else:
            self.Path_pro = p

        for i in self.Ins:
            p = self.Path_allsnap + '/' + self.Ins[i].Name
            if not open_or_create(p):
                return
            else:
                self.Ins[i].Path_snap = p

    def load_pro(self):
        print('load_pro')
        

    def print_info(self):
        print('='*80)
        print('print_info')
        print('Globalzero: %s' % (self.Globalzero))
        print('Abs_name: %s' % (self.Abs_name))
        print('Path: %s' % (self.Path))
        print('Path_allpro: %s' % (self.Path_allpro))
        print('Path_allsnap: %s' % (self.Path_allsnap))
        print('Path_pro: %s' % (self.Path_pro))
        print('Focus: %s' % (self.Focus))
        for i in self.Ins:
            print('-'*80)
            print('Ins num: %d' % (i))
            print('Ins name: %s' % (self.Ins[i].Name))
            print('Ins dollarzero: %d' % (self.Ins[i].Dollarzero))
            print('Ins globalzero: %d' % (self.Ins[i].Globalzero))
            print('Ins path snap: %s' % (self.Ins[i].Path_snap))
            for j in self.Ins[i].Par:
                print('Par: %d %s %s %g %g %g' % (j.Num,
                                                  j.Type,
                                                  j.Label,
                                                  j.Min,
                                                  j.Max,
                                                  j.Step))
            for j in self.Ins[i].Ar:
                print('Ar: %d %s' % (j.Num, j.Name))

    def init(self):
        print('init')
        self.Ins = {} # clear older result !
        Res = []
        Res.append(['send', '%d-sss-get-info-par' % (self.Globalzero)])
        Res.append(['msg', 'bang'])
        Res.append(['send', '%d-sss-get-info-array' % (self.Globalzero)])
        Res.append(['msg', 'bang'])
        Res.append(['send', '%d-sss-loop' % (self.Globalzero)])
        Res.append(['msg', 'list', 'after-get-info'])
        return (tuple(Res))

    def list(self, *args):
        Selector = args[0]
        if Selector == 'get-info-par-return':
            Name              = str(args[1])
            Dollarzero        = int(args[2]) # $0 local
            Globalzero        = int(args[3]) # $1 global
            Num               = int(args[4]) # $2 number
            Par_num           = int(args[5])
            Par_type          = str(args[6])
            Par_label         = str(args[7])
            Par_min           = float(args[8])
            Par_max           = float(args[9])
            Par_step          = float(args[10])
            if Num not in self.Ins:
                self.Ins[Num] = SSSIns()
                self.Ins[Num].Name = Name
                self.Ins[Num].Dollarzero = Dollarzero
                self.Ins[Num].Globalzero = Globalzero
            if  self.Ins[Num].Dollarzero != Dollarzero:
                print('error: not unique number ins! Name: %s Num: %d' %
                        (Name, Num))
                return
            self.Ins[Num].Par.append(SSSPar())
            self.Ins[Num].Par[-1].Num    = Par_num
            self.Ins[Num].Par[-1].Type   = Par_type
            self.Ins[Num].Par[-1].Label  = Par_label
            self.Ins[Num].Par[-1].Min    = Par_min
            self.Ins[Num].Par[-1].Max    = Par_max
            self.Ins[Num].Par[-1].Step   = Par_step
            print('Name = %s = %s' % (Par_num, self.Ins[Num].Par[-1].Num))
        elif Selector == 'get-info-array-return':
            Name              = str(args[1])
            Dollarzero        = int(args[2]) # $0 local
            Globalzero        = int(args[3]) # $1 global
            Num               = int(args[4]) # $2 number
            Ar_num            = int(args[5])
            Ar_name           = str(args[6])
            if Num not in self.Ins:
                self.Ins[Num] = SSSIns()
                self.Ins[Num].Name = Name
                self.Ins[Num].Dollarzero = Dollarzero
                self.Ins[Num].Globalzero = Globalzero
            if  self.Ins[Num].Dollarzero != Dollarzero:
                print('error: not unique number ins! Name: %s Num: %d' %
                        (Name, Num))
                return
            self.Ins[Num].Ar.append(SSSAr())
            self.Ins[Num].Ar[-1].Num   = Ar_num
            self.Ins[Num].Ar[-1].Name  = Ar_name
        elif Selector == 'after-get-info':
            for i in self.Ins:
                  self.Ins[i].Par.sort()
                  self.Ins[i].Ar.sort()
            self.get_path()
            self.load_pro()
            self.print_info()
        return

    def abs_name(self, s):
        s = str(s)
        i = s.find('.pd')
        if  i == -1:
            print('error: bad abs name: %s' % (s))
        else:
            s = s[:i]
        self.Abs_name = s
        print('abs_name: %s' % (self.Abs_name))
        return

    def focus(self, n):
        self.Focus = int(n)
        print('focus: %d' % (self.Focus))
        return

    def pro_save(self):
        print('pro_save')
        return

    def pro_save_as(self, filename):
        print('pro_save as: %s' % str(filename))
        return

    def pro_open(self, filename):
        print('pro_open: %s' % str(filename))
        return

    def snap_copy(self):
        print('snap_copy')
        return

    def bank(self, n):
        n = int(n)
        print('bank: %d' % (n))
        return

    def snap(self, n):
        n = int(n)
        print('snap: %d' % (n))
        return

    def snap_paste(self):
        print('snap_paste')
        return

    def snap_save(self, filename):
        print('snap_save: %s' % str(filename))
        return

    def snap_open(self, filename):
        print('snap_open: %s' % str(filename))
        return

    def rnd(self, *args):
        Selector = args[0]
        if Selector == 'nbx':
            Rng = float(args[1])
            I = int(args[2])
        elif Selector == 'slider':
            Rng = float(args[1])
            I = int(args[2])
        elif Selector == 'radio':
            Rng = float(args[1])
            I = 1
        elif Selector == 'tgl':
            Rng = float(args[1])
            I = 1
        elif Selector == 'knob':
            Rng = float(args[1])
            I = int(args[2])
        print('rnd: %s: %g: %d' % (Selector, Rng, I))
        return

def open_or_create(p):
    try:
        if (os.path.isdir(p) and
            os.access(p, os.R_OK) and
            os.access(p, os.W_OK)):
            return True
        else:
            os.mkdir(p)
            print('create: %s' % (p))
            return True
    except:
        print('error: open: %s' %  (p))
        return False


# ============================================================================ #
class SSSIns:
    def __init__(self, *creation):
        self.Name = ''
        self.Num = 0
        self.Dollarzero = 0
        self.Globalzero = 0
        self.Path_snap = ''
        self.Par = []
        self.Ar = []
        return

class SSSPar:
    def __init__(self, *creation):
        self.Num = -1
        self.Type = 'tgl'
        self.Label = 'empty'
        self.Min = 0.0
        self.Max = 1.0
        self.Step = 0.01
        self.Value = []
        return

class SSSAr:
    def __init__(self, *creation):
        self.Num = -1
        self.Name = ''
        return
