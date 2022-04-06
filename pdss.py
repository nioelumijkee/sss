#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------- #
# import sys
import os
import argparse

# ---------------------------------------------------------------------------- #
verbose = 0
quitet = 0

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
    '+', '-', '*', '/', 'pow' 
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

pdvanila = [
    pdvanila_general,
    pdvanila_gui,
    pdvanila_time,
    pdvanila_math,
    pdvanila_io,
    pdvanila_array,
    pdvanila_misc,
    pdvanila_audiomath,
    pdvanila_general_audio_tools,
    pdvanila_audio_gen_and_tables,
    pdvanila_audio_filters,
    pdvanila_audio_delay,
    pdvanila_patch,
    pdvanila_data,
    pdvanila_acc_data,
    pdvanila_extra,
]


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
        f = open(file)
        first = f.readline()
        f.close()
    except:
        print('error: open file %s' % (file))
        return(False)
    first = first.split()
    if first[0] == '#N' and first[1] == 'canvas':
        return(True)
    else: 
        print('error: not pd file %s' % (file))
        return(False)


# ---------------------------------------------------------------------------- #
def find_pd_files(files, h):
    b = []
    for file in files:
        if this_pd_file(file, h):
            b.append(file)
    return(b)


# ---------------------------------------------------------------------------- #
def find_all_files_in_dir(dir):
    if dir[-1] == '/':
        dir = dir[:-1]
    a = os.listdir(dir)
    b = []
    for i in a:
        b.append(dir + '/' + i)
    return(b)


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
        f = open(filename)
    except:
        print("error: open file %s" % (filename))
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
    print("pdfile2pdlist: done.")
    return(res)


# ---------------------------------------------------------------------------- #
def pdlist2pdfile(filename, l):
    "convert list to pd file"
    f = None
    try:
        f = open(filename, 'w')
    except:
        print("error open %s" % (filename))
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
def pdss_calc_coords(pos):
    obj_ox = 20  # offset
    obj_oy = 20
    obj_ix = 300 # inc
    obj_iy = 28
    obj_r = 16 # row

    x  = pos // obj_r # position
    y  = pos % obj_r
    ox = obj_ox + (obj_ix * x) # coords
    oy = obj_oy + (obj_iy * y)
    return(ox, oy)


# ---------------------------------------------------------------------------- #
def pdss(lpd, ins_name):
    obj_cnv    = '__pdss__'
    obj_driver = 'a_pdss_snap'
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
    a_nbx     = find_all_object(lpd, 'nbx')
    a_hsl     = find_all_object(lpd, 'hsl')
    a_vsl     = find_all_object(lpd, 'vsl')
    a_tgl     = find_all_object(lpd, 'tgl')
    a_hradio  = find_all_object(lpd, 'hradio')
    a_vradio  = find_all_object(lpd, 'vradio')
    a_n_knob  = find_all_object(lpd, 'n_knob')
    a_arrays  = find_all_arrays(lpd)

    a = (
        a_nbx +
        a_hsl +
        a_vsl +
        a_tgl +
        a_hradio +
        a_vradio +
        a_n_knob
    )
    allobj = len(a)
    allarr = len(a_arrays)
    a += a_arrays
    obj = []
    obj_n = 0
    arr_n = 0
    pos = 0

    # canvas
    s = '#N canvas 20 20 600 500 %s 0' % (obj_cnv)
    s = s.split()
    obj.append(s)

    # comment
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X text %d %d [Created by pdss.py]' % (ox, oy)
    s = s.split()
    obj.append(s)

    # a_snap
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X obj %d %d %s %s \$0 \$1 %d \$2' % (ox, oy, obj_driver,ins_name, allobj)
    s = s.split()
    obj.append(s)
    arr_n += 1

    # add array for par
    ox, oy  = pdss_calc_coords(pos);    pos += 1
    s = '#X obj %d %d table \$0_ss_a_%d;' % (ox, oy, arr_n)
    s = s.split()
    obj.append(s)
    
    for i in a:

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
            l[10] = '0'                   # init
            l[11] = '\$0_s_%d' % (obj_n)  # send
            l[12] = '\$0_r_%d' % (obj_n)  # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d nbx %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'hsl':
            l[10] = '0'                   # init
            l[11] = '\$0_s_%d' % (obj_n)  # send
            l[12] = '\$0_r_%d' % (obj_n)  # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d hsl %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'vsl':
            l[10] = '0'                   # init
            l[11] = '\$0_s_%d' % (obj_n)  # send
            l[12] = '\$0_r_%d' % (obj_n)  # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d vsl %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])

        elif l[4] == 'tgl':
            l[6] = '0'                    # init
            l[7] = '\$0_s_%d' % (obj_n)   # send
            l[8] = '\$0_r_%d' % (obj_n)   # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d tgl %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[9], l[18])

        elif l[4] == 'hradio':
            l[7] = '0'                    # init
            l[9] = '\$0_s_%d' % (obj_n)   # send
            l[10] = '\$0_r_%d' % (obj_n)  # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d hrd %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], l[8])

        elif l[4] == 'vradio':
            l[7] = '0'                    # init
            l[9] = '\$0_s_%d' % (obj_n)   # send
            l[10] = '\$0_r_%d' % (obj_n)  # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d vrd %s 0 %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], l[8])

        elif l[4] == 'n_knob':
            l[21] = '0'                        # init
            l[14] = '\\\\\$0_s_%d' % (obj_n)   # send
            l[13] = '\\\\\$0_r_%d' % (obj_n)   # receive
            s = '#X obj %d %d %s %s \$0 \$1 %d n_knob %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[15], l[8], l[9])

        if s != '':
            s = s.split()
            print('pdss: add: %s %s %s %s %s' % (s[8], s[9], s[10], s[11], s[12]))
            obj.append(s)
            obj_n += 1

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
def pdss_treat_files(files_in, files_out):
    if verbose:
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
# input function
# ---------------------------------------------------------------------------- #
def pdss_file(args):
    global verbose
    global quitet

    if args.v:
        verbose = 1

    if args.q:
        quitet = 1

    if args.i == '' or args.o == '':
        print('usage: -i input_file.pd -o output_file.pd')
        exit()

    files_in = [args.i]
    files_out = [args.o]
    files_in = find_pd_files(files_in, args.H)

    pdss_treat_files(files_in, files_out)


# ---------------------------------------------------------------------------- #
def pdss_dir(args):
    global verbose
    global quitet

    if args.v:
        verbose = 1

    if args.q:
        quitet = 1

    if args.d == '':
        print('usage: -d /path/to/dir/with/pd/files')
        exit()

    files_in = find_all_files_in_dir(args.d)
    files_in = find_pd_files(files_in, args.H)
    files_out = files_in

    pdss_treat_files(files_in, files_out)


# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='save state parser.')
    subparsers = parser.add_subparsers(title='subcommands')

    parser_pdss_file = subparsers.add_parser('file', help='parse one file')
    parser_pdss_file.add_argument('-i', default='', help='input file')
    parser_pdss_file.add_argument('-o', default='', help='output file')
    parser_pdss_file.add_argument('-v', action='store_true', help='verbose')
    parser_pdss_file.add_argument('-H', action='store_true', help='with *help* files')
    parser_pdss_file.add_argument('-q', action='store_true', help='quitet')
    parser_pdss_file.set_defaults(func=pdss_file)

    parser_pdss_dir = subparsers.add_parser('dir', help='parse directory')
    parser_pdss_dir.add_argument('-d', default='', help='input directory')
    parser_pdss_dir.add_argument('-v', action='store_true', help='verbose')
    parser_pdss_dir.add_argument('-H', action='store_true', help='with *help* files')
    parser_pdss_dir.add_argument('-q', action='store_true', help='quitet')
    parser_pdss_dir.set_defaults(func=pdss_dir)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
