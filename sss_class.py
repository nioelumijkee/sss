import pd
import os

__version__ = '0.1'

pro_ext = 'pro'
snap_ext = 'snap'
max_bank = 8
max_snap = 8
all_snap = 64

# ============================================================================ #
class SSSClass:
    def __init__(self, *creation):
        print_split0()
        print('__init__')
        # var
        self.Localzero = int(creation[0])
        self.Globalzero = int(creation[1])
        self.Focus = -1
        self.Abs_name = ''
        self.Path_SSS = ''
        self.Path_allpro = ''
        self.Path_allsnap = ''
        self.Path_pro = ''
        self.Pro_name = 'default'
        self.Ins = {}
        # send names global
        self.s_sss_get_info = '%d-sss-get-info' % (self.Globalzero)
        self.s_sss_loop = '%d-sss-loop' % (self.Globalzero)
        self.s_sss_focus = '%d-sss-focus' % (self.Globalzero)
        # send names local
        self.s_sss_pro_path = '%d-sss-pro-path' % (self.Localzero)
        self.s_sss_snap_path = '%d-sss-snap-path' % (self.Localzero)
        self.s_sss_cnv_abs_name = '%d-sss-cnv-abs-name' % (self.Localzero)
        self.s_sss_cnv_pro_name = '%d-sss-cnv-pro-name' % (self.Localzero)
        self.s_sss_cnv_ins_name = '%d-sss-cnv-ins-name' % (self.Localzero)
        self.s_sss_sel_bank = '%d-sss-sel-bank' % (self.Localzero)
        self.s_sss_bank_have_data = '%d-sss-bank-have-data' % (self.Localzero)
        self.s_sss_sel_snap = '%d-sss-sel-snap' % (self.Localzero)
        self.s_sss_snap_have_data = '%d-sss-snap-have-data' % (self.Localzero)
        return
    
    def init(self):
        print_split0()
        print('init')
        self.Ins = {} # clear older result !

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

    # create and check path's
    def get_path(self):
        print('get_path')
        try:
            p = os.environ['PD_SSS']
        except:
            print('error: env PD_SSS not set')
            return
        if not open_or_create(p): return
        else: self.Path_SSS = p

        p = self.Path_SSS + '/pro'
        if not open_or_create(p): return
        else: self.Path_allpro = p

        p = self.Path_SSS + '/snap'
        if not open_or_create(p): return
        else: self.Path_allsnap = p

        p = self.Path_SSS + '/pro/' + self.Abs_name
        if not open_or_create(p): return
        else: self.Path_pro = p

        for i in self.Ins:
            p = self.Path_allsnap + '/' + self.Ins[i].Name
            if not open_or_create(p): return
            else: self.Ins[i].Path_snap = p

    def print_info(self):
        print_split0()
        print('print_info')
        print('localzero: %s' % (self.Localzero))
        print('globalzero: %s' % (self.Globalzero))
        print('abs_name: %s' % (self.Abs_name))
        print('path sss: %s' % (self.Path_SSS))
        print('path allpro: %s' % (self.Path_allpro))
        print('path allsnap: %s' % (self.Path_allsnap))
        print('path pro: %s' % (self.Path_pro))
        print('focus: %s' % (self.Focus))
        kl = len(self.Ins.keys())
        k = list(self.Ins.keys())
        c = 0
        while c < kl:
            i = k[c]
            print_split1()
            print('ins num: %d' % (i))
            print('ins name: %s' % (self.Ins[i].Name))
            print('ins dollarzero: %d' % (self.Ins[i].Localzero))
            print('ins globalzero: %d' % (self.Ins[i].Globalzero))
            print('ins path snap: %s' % (self.Ins[i].Path_snap))
            kp = len(self.Ins[i].Par)
            kc = 0
            while kc < kp:
                j = self.Ins[i].Par[kc]
                print('par: %d %s %s %g %g %g' % (j.Num,
                                                  j.Type,
                                                  j.Label,
                                                  j.Min,
                                                  j.Max,
                                                  j.Step))
                kc += 1
            kp = len(self.Ins[i].Ar)
            kc = 0
            while kc < kp:
                j = self.Ins[i].Ar[kc]
                print('ar: %d %s' % (j.Num, j.Name))
                kc += 1
            c += 1
        print_split0()

    def get_info_par_return(self, *args):
        Name              = str(args[0])
        Localzero         = int(args[1]) # $0 local
        Globalzero        = int(args[2]) # $1 global
        Num               = int(args[3]) # $2 number
        Par_num           = int(args[4])
        Par_type          = str(args[5])
        Par_label         = str(args[6])
        Par_min           = float(args[7])
        Par_max           = float(args[8])
        Par_step          = float(args[9])
        if Num not in self.Ins:
            self.Ins[Num] = SSSIns()
            self.Ins[Num].Name = Name
            self.Ins[Num].Localzero = Localzero
            self.Ins[Num].Globalzero = Globalzero
        if  self.Ins[Num].Localzero != Localzero:
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
        return

    def get_info_ar_return(self, *args):
        Name              = str(args[0])
        Localzero         = int(args[1]) # $0 local
        Globalzero        = int(args[2]) # $1 global
        Num               = int(args[3]) # $2 number
        Ar_num            = int(args[4])
        Ar_name           = str(args[5])
        if Num not in self.Ins:
            self.Ins[Num] = SSSIns()
            self.Ins[Num].Name = Name
            self.Ins[Num].Localzero = Localzero
            self.Ins[Num].Globalzero = Globalzero
        if  self.Ins[Num].Localzero != Localzero:
            print('error: not unique number ins! Name: %s Num: %d' %
                  (Name, Num))
            return
        self.Ins[Num].Ar.append(SSSAr())
        self.Ins[Num].Ar[-1].Num   = Ar_num
        self.Ins[Num].Ar[-1].Name  = Ar_name
        return

    def load_pro(self):
        print('load_pro')

    def ins_sort(self):
        for i in self.Ins:
            self.Ins[i].sort()

    def set_abs_name(self):
        pd.pd_send_list(self.s_sss_cnv_abs_name, ['label', self.Abs_name])

    def set_pro_name(self):
        pd.pd_send_list(self.s_sss_cnv_pro_name, ['label', self.Pro_name])

    def set_ins_name(self):
        if self.Focus != -1:
            pd.pd_send_list(self.s_sss_cnv_ins_name, [
                'label',
                '%s[%d]' % (self.Ins[self.Focus].Name, self.Focus)])
        else:
            pd.pd_send_list(self.s_sss_cnv_ins_name, [
                'label',
                '-----'])

    def set_pro_path(self):
        pd.pd_send_list(self.s_sss_pro_path, [self.Path_pro])

    def set_snap_path(self):
        pd.pd_send_list(self.s_sss_snap_path, [self.Path_snap])

    def set_focus(self):
        pd.pd_send_list(self.s_sss_focus, [self.Focus])

    def set_sel_bank(self):
        pd.pd_send_list(self.s_sss_sel_bank, [self.Ins[self.Focus].Sel_bank])

    def set_sel_snap(self):
        bank = self.Ins[self.Focus].Sel_snap / max_snap
        snap = self.Ins[self.Focus].Sel_snap % max_snap
        if bank == self.Ins[self.Focus].Sel_bank:
            pd.pd_send_list(self.s_sss_sel_snap, [snap])
        else:
            pd.pd_send_list(self.s_sss_sel_snap, [-1])

    def set_bank_have_data(self):
        pd.pd_send_list(self.s_sss_bank_have_data, self.Ins[self.Focus].Bank_have_data)

    def set_snap_have_data(self):
        pd.pd_send_list(self.s_sss_snap_have_data, self.Ins[self.Focus].Snap_have_data)

    def focus(self, n):
        self.Focus = int(n)
        # find if neg
        if self.Focus == -1:
            if len(self.Ins) > 0:
                # find first ins
                min = 9999999
                for i in self.Ins:
                    if i < min:
                        min = i
                self.Focus = min
        # set bank
        self.Ins[self.Focus].Sel_bank = self.Ins[self.Focus].Sel_snap / max_snap
        print('focus: %d' % (self.Focus))
        return

    def pro_save(self):
        print('pro_save')
        return

    def pro_save_as(self, p):
        _, filename, _ = split_path(p)
        self.Pro_name = filename
        print('pro_save as: %s/%s.%s' % (self.Path_pro, self.Pro_name, pro_ext))
        return

    def pro_open(self, filename):
        print('pro_open: %s' % str(filename))
        return

    def snap_save(self):
        print('snap_save')
        return

    def snap_save_as(self, p):
        _, filename, _ = split_path(p)
        p = '%s/%s.%s' % (self.Ins[self.Focus].Path_snap, filename, snap_ext)
        print('snap_save as: %s/%s.%s' % (p))
        return

    def snap_open(self, filename):
        print('snap_open: %s' % str(filename))
        return

    def snap_copy(self):
        print('snap_copy')
        return

    def snap_paste(self):
        print('snap_paste')
        return

    def sel_bank(self, n):
        n = int(n)
        if n<0: n=0
        if n>7: n=7
        self.Ins[self.Focus].Sel_bank = n
        return

    def sel_snap(self, n):
        n = int(n)
        if n<0: n=0
        if n>7: n=7
        self.Ins[self.Focus].Sel_snap = n + (self.Ins[self.Focus].Sel_bank * max_snap)
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



# ============================================================================ #
def print_split0():
    print('='*80)

def print_split1():
    print('-'*80)

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

def split_path(p):
    p = str(p)
    path, filename = os.path.split(p)
    filename, ext = os.path.splitext(filename)
    return (path, filename, ext)

# ============================================================================ #
class SSSIns:
    def __init__(self, *creation):
        self.Name = ''
        self.Localzero = 0
        self.Globalzero = 0
        self.Path_snap = ''
        self.Par = []
        self.Ar = []
        #
        self.Sel_bank = 0
        self.Sel_snap = 0
        self.Bank_have_data = [0, 0, 0, 0, 0, 0, 0, 0]
        self.Snap_have_data = [0, 0, 0, 0, 0, 0, 0, 0]
    def sort(self):
        self.Par.sort()
        self.Ar.sort()

class SSSPar:
    def __init__(self, *creation):
        self.Num = -1
        self.Type = 'tgl'
        self.Label = 'empty'
        self.Min = 0.0
        self.Max = 1.0
        self.Step = 0.01
        self.Value = []

class SSSAr:
    def __init__(self, *creation):
        self.Num = -1
        self.Name = ''
        self.Value = []

class SSSSnap:
    def __init__(self, *creation):
        self.Par = []
        self.Ar = []
