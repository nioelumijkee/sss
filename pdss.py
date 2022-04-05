#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------- #
import sys
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
def split():
    print('-'*80)


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
        if find == 0 and l[0] == '#N' and l[1] == 'canvas' and l[6] == cnv:
            find = 1
            st = i
        
        if find == 1 and l[0] == '#X' and l[1] == 'restore' and l[5] == cnv:
            en = i
            break
    return(st, en)

# # ---------------------------------------------------------------------------- #
# def insert_string(s, l , pos):
#     "insert string to list"
#     l.insert(pos, s.split())

# ---------------------------------------------------------------------------- #
def doitss(lpd, ins_name):
    "remove old ps ss, find ss objects and create new pd ss"
    res = []

    # find ss canvas and remove
    st, en = find_canvas(lpd, '__ss__')
    print(st, en)
    if st != -1 and en != -1:
        print('doitss: find old "__ss__" object')
        b = []
        for i in range(len(lpd)):
            if i < st or i > en:
                b.append(lpd[i])
        lpd = b

    # find ss objects
    ss_nbx     = find_all_object(lpd, 'nbx')
    ss_hsl     = find_all_object(lpd, 'hsl')
    ss_vsl     = find_all_object(lpd, 'vsl')
    ss_tgl     = find_all_object(lpd, 'tgl')
    ss_hradio  = find_all_object(lpd, 'hradio')
    ss_vradio  = find_all_object(lpd, 'vradio')
    ss_n_knob  = find_all_object(lpd, 'n_knob')


    # print(ss_tgl)
    # print(ss_hradio)
    # print(ss_vradio)
    # print(ss_hsl)
    # print(ss_vsl)
    # print(ss_nbx)
    # print(ss_n_knob)


    print("doitss: done")
    return(lpd)


    # #####################################################################
    # # find ss objects
    # obj = []
    # obj_n = 0
    # arr = []
    # arr_n = 0
    # for s in res:
    #     if s[0] == '#X' and s[1] == 'obj':

    #         if s[4] == 'tgl':
    #             s[7] = '\$0_s_%d' % (obj_n)
    #             s[8] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[9]))

    #         elif s[4] == 'hradio':
    #             s[9] = '\$0_s_%d' % (obj_n)
    #             s[10] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[11]))

    #         elif s[4] == 'vradio':
    #             s[9] = '\$0_s_%d' % (obj_n)
    #             s[10] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[11]))

    #         elif s[4] == 'nbx':
    #             s[11] = '\$0_s_%d' % (obj_n)
    #             s[12] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[13]))

    #         elif s[4] == 'hsl':
    #             s[11] = '\$0_s_%d' % (obj_n)
    #             s[12] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[13]))

    #         elif s[4] == 'vsl':
    #             s[11] = '\$0_s_%d' % (obj_n)
    #             s[12] = '\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[13]))

    #         elif s[4] == 'n_knob':
    #             s[13] = '\\\\\$0_s_%d' % (obj_n)
    #             s[14] = '\\\\\$0_r_%d' % (obj_n)
    #             obj_n += 1
    #             obj.append(s)
    #             print('find: %s %s' % (s[4], s[15]))

    # # add array for par
    # arr_for_par_s = '#X obj 10 114 table \$0_ss_a_0;'
    # arr_for_par = arr_for_par_s.split()
    # obj.append(arr_for_par)
    # print('add : table %s (par)' % (arr_for_par[5]))


    # # find array objects
    # for s in res:
    #     if s[0] == '#X' and s[1] == 'array':
    #         arr_name = s[2]
    #         if arr_name[-2] == 's' and arr_name[-1] == 's':
    #             obj.append(s)
    #             print('find: array %s' % (s[2]))


    # #####################################################################
    # # insert pd ss
    # insert_string('#N canvas 20 20 900 500 ss 0', res , st)
    # st += 1; insert_string('#X text 10 50 this canvas automatic created by ss.py', res, st)
    # st += 1; insert_string('#X obj 10 92 n_ss_snap %s \$0 \$1 %d \$2' % (ins_name, obj_n), res, st)
    # st += 1; insert_string(arr_for_par_s, res, st)

    # # insert odj's and array's
    # obj_ox = 10
    # obj_oy = 140
    # obj_ix = 300
    # obj_iy = 28
    # obj_r = 16
    # obj_n = 0
    # arr_n = 0
    # for i in obj:

    #     x  = obj_n // obj_r
    #     y  = obj_n % obj_r
    #     ox = obj_ox + (obj_ix * x)
    #     oy = obj_oy + (obj_iy * y)

    #     # 1) ins name
    #     # 2) $0
    #     # 3) $1
    #     # 4) number
    #     # 5) type obj (tgl, hradio, vradio, nbx, vsl, hsl, n_knob)
    #     # 6) name
    #     # 7) lower
    #     # 8) upper

    #     if i[4] == 'tgl':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d tgl %s 0 1' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[9])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     elif i[4] == 'hradio':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d hrd %s 0 %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[11],
    #             i[8])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     elif i[4] == 'vradio':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d vrd %s 0 %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[11],
    #             i[8])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             

    #     elif i[4] == 'nbx':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d nbx %s %s %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[13],
    #             i[7],
    #             i[8])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     elif i[4] == 'hsl':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d hsl %s %s %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[13],
    #             i[7],
    #             i[8])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     elif i[4] == 'vsl':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d vsl %s %s %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[13],
    #             i[7],
    #             i[8])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     elif i[4] == 'n_knob':
    #         s = '#X obj %d %d n_ss_par %s \$0 \$1 %d n_knob %s %s %s' % (
    #             ox, oy,
    #             ins_name,
    #             obj_n,
    #             i[15],
    #             i[8],
    #             i[9])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
             
    #     # 1) ins name
    #     # 2) $0
    #     # 3) $1
    #     # 4) number
    #     # 5) name

    #     elif i[4] == 'table':
    #         s = '#X obj %d %d n_ss_array %s \$0 \$1 %d %s' % (
    #             ox, oy,
    #             ins_name,
    #             arr_n,
    #             i[5])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
    #         arr_n += 1
             
    #     elif i[1] == 'array':
    #         s = '#X obj %d %d n_ss_array %s \$0 \$1 %d %s' % (
    #             ox, oy,
    #             ins_name,
    #             arr_n,
    #             i[2])
    #         st += 1; insert_string(s, res, st)
    #         obj_n += 1
    #         arr_n += 1
             
    # # end canvas and connect
    # st += 1; insert_string('#X connect 1 0 2 0', res, st)
    # st += 1; insert_string('#X restore 20 50 pd ss', res, st)

    # return(res)


# ---------------------------------------------------------------------------- #
def ss_pdfile(filename_in, filename_out):
    # name
    name = os.path.splitext(filename_in)[0].split('/')[-1]
    print("name: ", name)

    # file to list
    pdl = pdfile2pdlist(filename_in)

    # ss
    pdl = doitss(pdl, name)

    # list to file 
    pdlist2pdfile(filename_out, pdl)


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
def parse_files(files_in, files_out):
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
                ss_pdfile(files_in[i], files_out[i])
        else:
            ss_pdfile(files_in[i], files_out[i])


# ---------------------------------------------------------------------------- #
def ss(args):
    global verbose
    global quitet

    if args.v:
        verbose = 1

    if args.q:
        quitet = 1

    if args.i == '' or args.o == '':
        print("usage: -i input_file.pd -o output_file.pd")
        exit()

    files_in = [args.i]
    files_out = [args.o]
    files_in = find_pd_files(files_in, args.H)

    parse_files(files_in, files_out)


# ---------------------------------------------------------------------------- #
def ssdir(args):
    global verbose
    global quitet

    if args.v:
        verbose = 1

    if args.q:
        quitet = 1

    if args.d == '':
        print("usage: -d /path/to/dir/with/pd/files")
        exit()

    files_in = find_all_files_in_dir(args.d)
    files_in = find_pd_files(files_in, args.H)
    files_out = files_in

    parse_files(files_in, files_out)


# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="save state parser.")
    subparsers = parser.add_subparsers(title='subcommands')

    parser_ss = subparsers.add_parser('ss', help='parse one file')
    parser_ss.add_argument('-i', default='', help='input file')
    parser_ss.add_argument('-o', default='', help='output file')
    parser_ss.add_argument('-v', action='store_true', help='verbose')
    parser_ss.add_argument('-H', action='store_true', help='with *help* files')
    parser_ss.add_argument('-q', action='store_true', help='quitet')
    parser_ss.set_defaults(func=ss)

    parser_ssdir = subparsers.add_parser('ssdir', help='parse directory')
    parser_ssdir.add_argument('-d', default='', help='input directory')
    parser_ssdir.add_argument('-v', action='store_true', help='verbose')
    parser_ssdir.add_argument('-H', action='store_true', help='with *help* files')
    parser_ssdir.add_argument('-q', action='store_true', help='quitet')
    parser_ssdir.set_defaults(func=ssdir)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
