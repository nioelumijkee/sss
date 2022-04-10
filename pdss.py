#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.3'

# ---------------------------------------------------------------------------- #
import os
import argparse
import re

# ---------------------------------------------------------------------------- #
# vanila
# ---------------------------------------------------------------------------- #
pdvanila_general = [
    'bang', 'b',
    'float', 'f',
    'symbol', 
    'int', 'i',
    'send', 'receive', 's', 'r',
    'select', 'sel',
    'route',
    'pack', 'unpack', 
    'trigger', 't', 
    'spigot', 'moses', 'until', 'print', 'trace', 
    'makefilename', 'change', 'swap', 
    'value', 'v', 
    'list',
]

pdvanila_gui = [
    'bng', 'tgl', 'nbx', 'hsl', 'vsl', 'hradio', 'vradio', 'vu', 'cnv'
]

pdvanila_time = [
    'delay', 'del',
    'metro', 'line', 'timer', 'cputime', 'realtime', 'pipe', 
]

pdvanila_math = [
    'expr',
    '+', '-', '*', '/', 'pow', 
    '==', '!=', '>', '<', '>=', '<=', 
    '&', '&&', '|', '||', '%', '<<', '>>', 
    'mtof', 'ftom', 'powtodb', 'rmstodb', 'dbtopow', 'dbtorms',
    'mod', 'div',
    'sin', 'cos', 'tan', 
    'atan', 'atan2', 
    'sqrt', 'log', 'exp', 'abs',
    'random', 
    'max', 'min', 
    'clip',
    'wrap',
]

pdvanila_io = [
    'notein', 'ctlin', 'pgmin', 'bendin', 'touchin', 'polytouchin', 
    'midiin', 'sysexin', 'midirealtimein',
    'noteout', 'ctlout', 'pgmout', 'bendout', 'touchout', 
    'polytouchout', 'midiout', 
    'makenote', 'stripnote', 
    'poly',
    'oscparse', 'oscformat',
    'fudiparse', 'fudiformat',
]

pdvanila_array = [
    'tabread', 'tabread4',
    'tabwrite', 
    'soundfiler',
    'table',
    'array',
]

pdvanila_misc = [
    'loadbang',
    'declare',
    'savestate',
    'pdcontrol',
    'netsend', 'netreceive',
    'qlist', 
    'textfile',
    'text',
    'file',
    'openpanel', 'savepanel', 
    'bag',
    'key', 'keyup', 'keyname',
]

pdvanila_audiomath = [
    'expr~', 'fexpr~',
    '+~', '-~', '*~', '/~',
    'min~', 'max~', 
    'clip~', 
    'sqrt~', 'rsqrt~', 'q8_sqrt~', 'q8_rsqrt~', 
    'wrap~',
    'fft~', 'ifft~', 'rfft~', 'rifft~', 
    'pow~', 'log~', 'exp~', 'abs~', 
    'framp~', 
    'mtof~', 'ftom~', 'rmstodb~', 'dbtorms~', 
]

pdvanila_general_audio_tools = [
    'dac~', 'adc~', 
    'sig~', 
    'line~', 'vline~',
    'threshold~',
    'snapshot~', 'vsnapshot~', 
    'bang~', 
    'samplerate~',
    'send~', 'receive~', 's~', 'r~',
    'throw~', 'catch~',
    'block~', 
    'readsf~', 'writesf~', 
    'print~',
]

pdvanila_audio_gen_and_tables = [
    'noise',
    'phasor~', 
    'cos~', 
    'osc~', 
    'tabwrite~', 'tabplay~', 'tabread~', 'tabread4~', 
    'tabosc4~', 'tabsend~','tabreceive~',
]

pdvanila_audio_filters = [
    'vcf~', 
    'env~', 
    'hip~', 'lop~', 'slop~', 'bp~', 'biquad~', 
    'samphold~',
    'rpole~', 'rzero~', 'rzero_rev~', 
    'cpole~', 'czero~', 'czero_rev~',
]

pdvanila_audio_delay = [
    'delwrite~', 'delread~',
    'delread4~', 'vd~', 
]
    
pdvanila_patch = [
    'clone',
#    'pd',
    'inlet', 'outlet', 'inlet~', 'outlet~',
    'namecanvas',
    'block~', 'switch~', # switch deprecated
]

pdvanila_data = [
    'struct', 
    'drawcurve', 'filledcurve',
    'drawpolygon', 'filledpolygon',
    'drawnumber', 'drawsymbol', 'drawtext',
    'plot',
]

pdvanila_acc_data = [
    'pointer', 
    'get', 'set', 
    'element', 
    'getsize', 'setsize', 
    'append', 'scalar',
]

pdvanila_extra = [
    'signund~',
    'bonk~',
    'choice',
    'hilbert~', 'complex-mod',
    'loop~',
    'lrshift~',
    'pd~',
    'stdout',
    'rev1~', 'rev2~', 'rev3~',
    'bob~',
    'output~'
]

pdvanila = (
    pdvanila_general +
    pdvanila_gui +
    pdvanila_time +
    pdvanila_math +
    pdvanila_io +
    pdvanila_array +
    pdvanila_misc +
    pdvanila_audiomath +
    pdvanila_general_audio_tools +
    pdvanila_audio_gen_and_tables +
    pdvanila_audio_filters +
    pdvanila_audio_delay +
    pdvanila_patch +
    pdvanila_data +
    pdvanila_acc_data +
    pdvanila_extra
)


# ---------------------------------------------------------------------------- #
# files
# ---------------------------------------------------------------------------- #
def this_pd_file(file, h):
    name, ex = os.path.splitext(file)
    first = ''

    # extension
    if ex != '.pd':
        return(False)

    # *help* files
    if h == 0:
        if name.find('help') != -1:
            return(False)

    # open and test first string
    try:
        f = open(file, errors='ignore')
        first = f.readline()
        f.close()
    except:
        print('error: this_pd_file: open %s' % (file))
        return(False)
    first = first.split()
    if len(first) > 1 and first[0] == '#N':
        return(True)
    else: 
        print('error: this_pd_file: not pd file %s' % (file))
        return(False)


# ---------------------------------------------------------------------------- #
def find_pd_files(files, h):
    b = []
    for file in files:
        if this_pd_file(file, h):
            b.append(file)
    return(b)


# ---------------------------------------------------------------------------- #
def find_all_files_in_dir(path):
    d = []
    b = []
    try:
        d = os.listdir(path)
    except:
        print("error: find_all_files_in_dir: open %s" % (path))
        return(b)
    for i in d:
        b.append(path + '/' + i)
    return(b)

# ---------------------------------------------------------------------------- #
def find_all_files_in_dir_rec(path, b):
    d = []
    try:
        d = os.listdir(path)
    except:
        print("error: find_all_files_in_dir_rec: open %s" % (path))
        return
    for i in d:
        s = path + '/' + i
        # directory ?
        if os.path.isdir(s):
            if not os.path.islink(s):
                if os.access(s, os.R_OK):
                    find_all_files_in_dir_rec(s, b)
        # file
        else:
            b.append(s)
    return

# ---------------------------------------------------------------------------- #
def path_norm(path):
    if path[-1] == '/':
        path = path[:-1]
    return(path)

# ---------------------------------------------------------------------------- #
# print
# ---------------------------------------------------------------------------- #
def split():
    print('-'*80)


# ---------------------------------------------------------------------------- #
# convert pdfile to pd list
# ---------------------------------------------------------------------------- #
def pdfile2pdlist(filename):
    "convert pd file to list"
    f = None
    try:
        f = open(filename, errors='ignore')
    except:
        print("error: pdfile2pdlist: open %s" % (filename))
        exit()

    l = f.readlines()
    res = []
    s = ''
    for i in l:
        i = i.strip()
        s = s + ' ' + i
        if s[-1] == ';':
            s = s[:-1] # remove last ';'
            s = s.strip().split()
            res.append(s)
            s = ''
    f.close()
    # print("pdfile2pdlist: done.")
    return(res)


# ---------------------------------------------------------------------------- #
def pdlist2pdfile(filename, l):
    "convert list to pd file"
    f = None
    try:
        f = open(filename, 'w')
    except:
        print("error: pdlist2pdfile: open %s" % (filename))
        exit()

    for i in l:
        s = ''
        for j in i:
            s = s + ' ' + j
        s = s.strip()
        s = s + ";"
        f.write(s)
        f.write('\n')
    f.close()
    print("pdlist2pdfile: done.")


# ---------------------------------------------------------------------------- #
# operation with pdlist
# ---------------------------------------------------------------------------- #
def find_all_object(lpd, obj):
    res = []
    for i in range(len(lpd)):
        l = lpd[i]
        if len(l) >= 5:
            if l[0] == '#X' and l[1] == 'obj' and l[4] == obj:
                res.append(i)
    return(res)


# ---------------------------------------------------------------------------- #
def find_canvas(lpd, cnv):
    st = -1
    en = -1
    find = 0
    for i in range(len(lpd)):
        l = lpd[i]
        if len(l) >= 7:
            if find == 0 and l[0] == '#N' and l[1] == 'canvas' and l[6] == cnv:
                find = 1
                st = i
        
        if len(l) >= 6:
            if find == 1 and l[0] == '#X' and l[1] == 'restore' and l[5] == cnv:
                en = i
                break
    return(st, en)


# ---------------------------------------------------------------------------- #
def find_all_arrays(lpd):
    res = []
    ar = 0
    n = -1
    for i in range(len(lpd)):
        l = lpd[i]
        if ar == 0 and l[0] == '#X' and l[1] == 'array':
            if l[2].find('pdss') != -1:
                ar = 1
                n = i
        if ar == 1 and l[0] == '#A':
            n = -1
        if ar == 1 and l[0] == '#X' and l[1] == 'coords':
            ar = 0
            if n != -1:
                res.append(n)
    return(res)


# ---------------------------------------------------------------------------- #
# pdss
# ---------------------------------------------------------------------------- #
obj_ox = 20  # offset
obj_oy = 20
obj_ix = 350 # inc
obj_iy = 24
obj_r = 16 # row
cnv_w = obj_ox + (obj_ix * 3) 
cnv_h = obj_oy + (obj_iy * obj_r) + obj_oy

def pdss_calc_coords(pos):
    x  = pos // obj_r # position
    y  = pos % obj_r
    ox = obj_ox + (obj_ix * x) # coords
    oy = obj_oy + (obj_iy * y)
    return(ox, oy)


# ---------------------------------------------------------------------------- #
def pdss(lpd, ins_name):
    obj_cnv    = '__pdss__'
    obj_driver = 'a_pdss_driver'
    obj_par    = 'a_pdss_par'
    obj_array  = 'a_pdss_array'


    # find ss canvas
    st, en = find_canvas(lpd, obj_cnv)
    if st != -1 and en != -1:
        print('pdss: find: old "%s" object' % (obj_cnv))
        b = []
        for i in range(len(lpd)):
            if i < st or i > en:
                b.append(lpd[i])
        lpd = b

    # find gui objects and arrays
    all_nbx     = find_all_object(lpd, 'nbx')
    all_hsl     = find_all_object(lpd, 'hsl')
    all_vsl     = find_all_object(lpd, 'vsl')
    all_tgl     = find_all_object(lpd, 'tgl')
    all_hradio  = find_all_object(lpd, 'hradio')
    all_vradio  = find_all_object(lpd, 'vradio')
    all_n_knob  = find_all_object(lpd, 'n_knob')
    all_obj = (
        all_nbx +
        all_hsl +
        all_vsl +
        all_tgl +
        all_hradio +
        all_vradio +
        all_n_knob
    )
    all_arrays  = find_all_arrays(lpd)

    obj = []

    # canvas
    s = '#N canvas 20 20 %d %d %s 0' % (cnv_w, cnv_h, obj_cnv)
    s = s.split()
    obj.append(s)

    pos = 0

    # comment
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X text %d %d [Created by pdss.py]' % (ox, oy)
    s = s.split()
    obj.append(s)

    # driver
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X obj %d %d %s %s \$0 \$1 %d \$2' % (
        ox, oy, obj_driver,ins_name, len(all_obj))
    s = s.split()
    obj.append(s)

    # array for par
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X obj %d %d table \$0-pdss-array-%d' % (ox, oy, 0)
    s = s.split()
    obj.append(s)
    
    pos = obj_r
    obj_n = 0
    for i in all_obj:
        l = lpd[i]
        ox, oy  = pdss_calc_coords(pos);   pos += 1
        s = ''
        
        # 1) ins name
        # 2) $0
        # 3) $1
        # 4) number
        # 5) type obj
        # 6) name
        # 7) lower
        # 8) upper

        if l[4] == 'nbx':
            l[10] = '0'                   
            l[11] = '\$0-pdss-s-%d' % (obj_n)  
            l[12] = '\$0-pdss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 %d nbx %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'hsl':
            l[10] = '0'                   
            l[11] = '\$0-pdss-s-%d' % (obj_n)  
            l[12] = '\$0-pdss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 %d hsl %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'vsl':
            l[10] = '0'                   
            l[11] = '\$0-pdss-s-%d' % (obj_n)  
            l[12] = '\$0-pdss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 %d vsl %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'tgl':
            l[6] = '0'                    
            l[7] = '\$0-pdss-s-%d' % (obj_n)   
            l[8] = '\$0-pdss-r-%d' % (obj_n)   
            s = '#X obj %d %d %s %s \$0 \$1 %d tgl %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[9], l[18])

        elif l[4] == 'hradio':
            l[7] = '0'                    
            l[9] = '\$0-pdss-s-%d' % (obj_n)   
            l[10] = '\$0-pdss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 %d hrd %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], l[8])

        elif l[4] == 'vradio':
            l[7] = '0'                    
            l[9] = '\$0-pdss-s-%d' % (obj_n)   
            l[10] = '\$0-pdss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 %d vrd %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], l[8])

        elif l[4] == 'n_knob':
            l[21] = '0'                        
            l[14] = '\\\\\$0-pdss-s-%d' % (obj_n)   
            l[13] = '\\\\\$0-pdss-r-%d' % (obj_n)   
            s = '#X obj %d %d %s %s \$0 \$1 %d n_knob %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[15], l[8], l[9])

        if s != '':
            s = s.split()
            print('pdss: add: %s %s %s %s %s' % (s[8], s[9], s[10], s[11], s[12]))
            obj.append(s)
            obj_n += 1
        else:
            print("error: pdss: ", l)
            exit()

    pos = pos // obj_r
    pos = (pos+1) * obj_r

    # array for par
    ox, oy  = pdss_calc_coords(pos);   pos += 1
    s = '#X obj %d %d %s %s \$0 \$1 %d \$0-pdss-array-%d' % (
        ox, oy, obj_array, ins_name, 0, 0)
    s = s.split()
    print('pdss: add: %s %s' % (s[8], s[9]))
    obj.append(s)

    arr_n = 1
    for i in all_arrays:
        l = lpd[i]
        ox, oy  = pdss_calc_coords(pos);   pos += 1
        s = ''

        # 1) ins name
        # 2) $0
        # 3) $1
        # 4) number
        # 5) name

        if l[1] == 'array':
            s = '#X obj %d %d %s %s \$0 \$1 %d %s' % (
                ox, oy, obj_array, ins_name, arr_n, l[2])
            s = s.split()
            print('pdss: add: %s %s' % (s[8], s[9]))
            obj.append(s)
            arr_n += 1
        else:
            print("error: pdss: ", l)
            exit()

    # canvas
    s = '#X restore 20 20 pd %s' % (obj_cnv)
    s = s.split()
    obj.append(s)

    # add to list if find
    if st != -1 and en != -1:
        j = st
        for i in obj:
            lpd.insert(j, i)
            j += 1
    else:
        for i in obj:
            lpd.append(i)


    print('pdss: done')
    return(lpd)


# ---------------------------------------------------------------------------- #
def pdss_one_file(filename_in, filename_out):
    name = os.path.splitext(filename_in)[0].split('/')[-1]
    print('name: ', name)
    pdl = pdfile2pdlist(filename_in)
    pdl = pdss(pdl, name)
    pdlist2pdfile(filename_out, pdl)


# ---------------------------------------------------------------------------- #
def pdss_treat_files(files_in, files_out, quitet):
    split()
    print('all:')
    for i in range(len(files_in)):
        s = files_in[i] + '  ->  ' + files_out[i]
        print(s)
    for i in range(len(files_in)):
        split()
        if quitet == 0:
            s = files_in[i] + '  ->  ' + files_out[i]
            print(s)
            usin = 'Y'
            usin = input('Parse this file? (y-yes, q-quit, other skip): ')
            if usin == 'q':
                exit()
            if usin == 'y':
                pdss_one_file(files_in[i], files_out[i])
        else:
            pdss_one_file(files_in[i], files_out[i])


# ---------------------------------------------------------------------------- #
# stat
# ---------------------------------------------------------------------------- #
def stat_one_file(file_in, objs_vanila, objs_not_vanila):
    f = None
    try:
        f = open(file_in)
    except:
        print("error: stat_one_file: open %s" % (file_in))
        return

    pdl = pdfile2pdlist(file_in)
    for i in pdl:
        if len(i) >= 5:
            if i[0] == '#X' and i[1] == 'obj':
                n = i[4].replace(',','')
                if not n in pdvanila:
                    if not n in objs_not_vanila:
                        objs_not_vanila.append(n)
                else:
                    if not n in objs_vanila:
                        objs_vanila.append(n)


# ---------------------------------------------------------------------------- #
def stat_one_file_count(file_in, objs_vanila, objs_not_vanila):
    f = None
    try:
        f = open(file_in)
    except:
        print("error: stat_one_file: open %s" % (file_in))
        return

    pdl = pdfile2pdlist(file_in)
    for i in pdl:
        if len(i) >= 5:
            if i[0] == '#X' and i[1] == 'obj':
                n = i[4].replace(',','')
                if not n in pdvanila:
                    if not n in objs_not_vanila:
                        objs_not_vanila[n] = 1
                    else:
                        objs_not_vanila[n] += 1
                else:
                    if not n in objs_vanila:
                        objs_vanila[n] = 1
                    else:
                        objs_vanila[n] += 1


# ---------------------------------------------------------------------------- #
def stat_treat_files(files_in, c):
    split()
    print('all:')
    for i in files_in:
        print(i)
    if c:
        objs_vanila = {}
        objs_not_vanila = {}
        for i in files_in:
            stat_one_file_count(i, objs_vanila, objs_not_vanila)
        split()
        print("vanila objects:")
        for i in objs_vanila:
            print(i, ' : ', objs_vanila[i])
        split()
        print("not vanila objects:")
        for i in objs_not_vanila:
            print(i, ' : ', objs_not_vanila[i])

    else:
        objs_vanila = []
        objs_not_vanila = []
        for i in files_in:
            stat_one_file(i, objs_vanila, objs_not_vanila)
        split()
        print("vanila objects:")
        print(objs_vanila)
        split()
        print("not vanila objects:")
        print(objs_not_vanila)


# ---------------------------------------------------------------------------- #
# objs
# ---------------------------------------------------------------------------- #
def objs_treat_files(path):
    split()

    all = {}
    dirs = os.listdir(path)

    regex_pd = re.compile(".pd$")
    regex_help_start = re.compile("^help-")
    regex_help_end = re.compile("-help.pd$")

    for d in dirs:
        all[d] = []

        buf = os.listdir("%s/%s" % (path,d))
        for f in buf:
            if os.path.isfile("%s/%s/%s" % (path,d,f)):
                r = regex_pd.search(f)
                if r:
                    r = regex_help_start.search(f)
                    if r:
                        str = f[5:-3]
                        all[d].append(str)

                    r = regex_help_end.search(f)
                    if r:
                        str = f[:-8]
                        all[d].append(str)

    # print
    ks = list(all.keys())
    ks.sort()

    print(path)
    for key in ks:
        split()
        print(path + '/' + key)
        print(all[key])


# ---------------------------------------------------------------------------- #
# input function
# ---------------------------------------------------------------------------- #
def pdss_input(args):
    msg_err = """usage: 
    -f input_file.pd -o output_file.pd
    or
    -d /path/to/dir/with/pd/files"""
    f = 1
    # -f -o
    if args.f != '':
        if args.o == '':
            print(msg_err)
            exit()
        else:
            f = 1
    elif args.o != '':
        print(msg_err)
        exit()
    elif args.d == '':
        print(msg_err)
        exit()
    else:
        f = 0

    # one file
    if f:
        files_in = [args.f]
        files_out = [args.o]
        files_in = find_pd_files(files_in, args.H)
    # dir
    else:
        path = path_norm(args.d)
        files_in = []
        if args.r:
            find_all_files_in_dir_rec(path, files_in)
        else:
            files_in = find_all_files_in_dir(path)
        files_in = find_pd_files(files_in, args.H)
        files_out = files_in

    pdss_treat_files(files_in, files_out, args.q)


# ---------------------------------------------------------------------------- #
def stat(args):
    msg_err = """usage: 
    -f input_file.pd
    or
    -d /path/to/dir/with/pd/files"""
    f = 1
    # -f
    if args.f != '':
        if args.d != '':
            print(msg_err)
            exit()
        else:
            f = 1
    elif args.d == '':
        print(msg_err)
        exit()
    else:
        f = 0

    # one file
    if f:
        files_in = [args.f]
        files_in = find_pd_files(files_in, args.H)
    # dir
    else:
        path = path_norm(args.d)
        files_in = []
        if args.r:
            find_all_files_in_dir_rec(path, files_in)
        else:
            files_in = find_all_files_in_dir(path)
        files_in = find_pd_files(files_in, args.H)

    stat_treat_files(files_in, args.c)


# ---------------------------------------------------------------------------- #
def objs(args):
    msg_err = """usage: 
    -d /path/to/dir/with/pd/libs"""
    if args.d == '':
        print(msg_err)
        exit()

    path = path_norm(args.d)
    objs_treat_files(path)


# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='pure data save state script. version = %s' % (__version__))
    subparsers = parser.add_subparsers(title='subcommands')

    parser_pdss = subparsers.add_parser('file', help='pdss one file')
    parser_pdss.add_argument('-f', default='', help='input file')
    parser_pdss.add_argument('-o', default='', help='output file')
    parser_pdss.add_argument('-d', default='', help='directory')
    parser_pdss.add_argument('-r', action='store_true', help='recursive')
    parser_pdss.add_argument('-H', action='store_true', help='with *help* files')
    parser_pdss.add_argument('-q', action='store_true', help='quitet')
    parser_pdss.set_defaults(func=pdss_input)

    parser_stat = subparsers.add_parser('stat', help='statistics')
    parser_stat.add_argument('-f', default='', help='file')
    parser_stat.add_argument('-d', default='', help='directory')
    parser_stat.add_argument('-r', action='store_true', help='recursive')
    parser_stat.add_argument('-H', action='store_true', help='with *help* files')
    parser_stat.add_argument('-c', action='store_true', help='count objects')
    parser_stat.set_defaults(func=stat)

    parser_objs = subparsers.add_parser('objs', help='find all objs')
    parser_objs.add_argument('-d', default='', help='directory')
    parser_objs.set_defaults(func=objs)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
