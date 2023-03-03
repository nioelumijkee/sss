import pd
import os

class SSSClass:
    def __init__( self, *creation ):
        self.Global_dollarzero = int(creation[0])
        self.Ins = {}
        self.Focus = -1
        self.Abs_name = ''
        self.Main_path = '.'
        self.Pro_path = '.'
        pd.post('global_dollarzero: %d' % (self.Global_dollarzero))
        return
    
    def load_data(self):
        pd.post('load data')
        #
        try:
            Main_path = os.environ['PD_SSS']
        except:
            pd.post('error: env PD_SSS not exist')
            Main_path = '.'
        # exist ?
        try:
            if (os.path.isdir(Main_path) and
                os.access(Main_path, os.R_OK) and
                os.access(Main_path, os.W_OK)):
                self.Main_path = Main_path
            else:
                os.mkdir(Main_path)
                pd.post('create Main_path: %s' % (Main_path))
                self.Main_path = Main_path
        except:
            pd.post('error: open Main_path')
        # load default
        Pro_path = self.Main_path + '/' + self.Abs_name


    def init(self):
        pd.post('init.')
        self.Ins = {} # clear older result !
        Res = []
        Res.append(['send', '%d-sss-get-info-par' % (self.Global_dollarzero)])
        Res.append(['msg', 'bang'])
        Res.append(['send', '%d-sss-get-info-array' % (self.Global_dollarzero)])
        Res.append(['msg', 'bang'])
        Res.append(['send', '%d-sss-loop' % (self.Global_dollarzero)])
        Res.append(['msg', 'list', 'after-get-info'])
        return (tuple(Res))

    def list(self, *args):
        Selector = args[0]
        if Selector == 'get-info-par-return':
            Ins_name          = str(args[1])
            Ins_dollarzero    = int(args[2]) # $0 local
            Global_dollarzero = int(args[3]) # $1 global
            Ins_num           = int(args[4]) # $2 number
            Par_num           = int(args[5])
            Par_type          = str(args[6])
            Par_label         = str(args[7])
            Par_min           = float(args[8])
            Par_max           = float(args[9])
            Par_step          = float(args[10])
            if Ins_num not in self.Ins:
                self.Ins[Ins_num] = {'Par':[], 'Ar':[]}
                self.Ins[Ins_num]['Ins_name'] = Ins_name
                self.Ins[Ins_num]['Ins_dollarzero'] = Ins_dollarzero
            if  self.Ins[Ins_num]['Ins_dollarzero'] != Ins_dollarzero:
                pd.post('error: not unique number ins ! Ins_name: %s Ins_num: %d' %
                        (Ins_name, Ins_num))
                return
            self.Ins[Ins_num]['Par'].append(
                {'Par_num'   : Par_num,
                 'Par_type'  : Par_type,
                 'Par_label' : Par_label,
                 'Par_min'   : Par_min,
                 'Par_max'   : Par_max,
                 'Par_step'  : Par_step,
                 'Par_value' : []
                 })
        elif Selector == 'get-info-array-return':
            Ins_name          = str(args[1])
            Ins_dollarzero    = int(args[2]) # $0 local
            Global_dollarzero = int(args[3]) # $1 global
            Ins_num           = int(args[4]) # $2 number
            Ar_num            = int(args[5])
            Ar_name           = str(args[6])
            if Ins_num not in self.Ins:
                self.Ins[Ins_num] = {'Par':[], 'Ar':[]}
                self.Ins[Ins_num]['Ins_name'] = Ins_name
                self.Ins[Ins_num]['Ins_dollarzero'] = Ins_dollarzero
            if  self.Ins[Ins_num]['Ins_dollarzero'] != Ins_dollarzero:
                pd.post('error: not unique number ins ! Ins_name: %s Ins_num: %d' %
                        (Ins_name, Ins_num))
            self.Ins[Ins_num]['Ar'].append(
                {'Ar_num'  : Ar_num, 
                 'Ar_name' : Ar_name,
                 })
        elif Selector == 'after-get-info':
            pd.post('done get info')
            # print
            for i in self.Ins:
                print('='*80)
                print('Ins_num:',i)
                print('Ins_name:', self.Ins[i]['Ins_name'])
                print('Ins_dollarzero:', self.Ins[i]['Ins_dollarzero'])
                self.Ins[i]['Par'].sort()
                self.Ins[i]['Ar'].sort()
                for j in self.Ins[i]['Par']:
                    print(j)
                for j in self.Ins[i]['Ar']:
                    print(j)
            # load data
            self.load_data()
        return

    def abs_name(self, s):
        s = str(s)
        i = s.find('.pd')
        if  i == -1:
            pd.post('error: bad abs name: %s' % (s))
        else:
            s = s[:i]
        self.Abs_name = s
        pd.post('abs name: %s' % (self.Abs_name))
        return

    def focus(self, n):
        self.Focus = int(n)
        pd.post('focus: %d' % (self.Focus))
        return

    def pro_save(self):
        pd.post('pro save')
        return

    def pro_save_as(self, filename):
        pd.post('pro save as: %s' % str(filename))
        return

    def pro_open(self, filename):
        pd.post('pro open: %s' % str(filename))
        return

    def snap_copy(self):
        pd.post('snap copy')
        return

    def bank(self, n):
        n = int(n)
        pd.post('bank: %d' % (n))
        return

    def snap(self, n):
        n = int(n)
        pd.post('snap: %d' % (n))
        return

    def snap_paste(self):
        pd.post('snap paste')
        return

    def snap_save(self, filename):
        pd.post('snap save: %s' % str(filename))
        return

    def snap_open(self, filename):
        pd.post('snap open: %s' % str(filename))
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
        pd.post('rnd: %s: %g: %d' % (Selector, Rng, I))
        return

