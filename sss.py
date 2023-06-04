#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.6'

import os
import argparse
import re

max_par = 128
max_ar = 32

# ============================================================================ #
def is_pd_file(file, is_help_file):
    name, ex = os.path.splitext(file)
    first = ''
    if ex != '.pd':
        return False
    if is_help_file == 0:
        if name.find('help') != -1:
            return False
    try:
        f = open(file, errors='ignore')
        first = f.readline()
        f.close()
    except:
        print('warning: is_pd_file: open: %s' % (file))
        return False
    first = first.split()
    if len(first) > 1 and first[0] == '#N':
        return True
    else:
        print('warning: is_pd_file: bad pd file: %s' % (file))
        return False

def find_pd_files(files, h):
    res = []
    for file in files:
        if is_pd_file(file, h):
            res.append(file)
    return res

def all_in_dir(path):
    d = []
    res = []
    try:
        d = os.listdir(path)
    except:
        print("warning: all_in_dir: read: %s" % (path))
        return res
    for i in d:
        res.append(path + '/' + i)
    return res

def all_in_dir_rec(path, res):
    d = []
    try:
        d = os.listdir(path)
    except:
        print("error: all_in_dir_rec: open %s" % (path))
        return
    for i in d:
        s = path + '/' + i
        if os.path.isdir(s):              # directory ?
            if not os.path.islink(s):     # link ?
                if os.access(s, os.R_OK): # read access ?
                    all_in_dir_rec(s, res)
        else:
            res.append(s)
    return

def path_norm(path):
    if path[-1] == '/':
        path = path[:-1]
    return path

def split():
    print('='*80)

# ============================================================================ #
def pdfile2pdlist(filename):
    f = None
    try:
        f = open(filename, errors='ignore')
    except:
        print("error: pdfile2pdlist: open: %s" % (filename))
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
    return res

def pdlist2pdfile(filename, l):
    f = None
    try:
        f = open(filename, 'w')
    except:
        print("error: pdlist2pdfile: open: %s" % (filename))
        exit()
    for i in l:
        s = ''
        for j in i:
            s = s + ' ' + j
        s = s.strip()
        s = s + ";\n" # add last ';'
        f.write(s)
    f.close()
    print("pdlist2pdfile: done.")

def find_all_object(lpd, obj):
    res = []
    for i in lpd:
        if len(i) >= 5:
            if i[0] == '#X' and i[1] == 'obj' and i[4] == obj:
                res.append(i)
    return res

def find_all_arrays(lpd):
    res = []
    for i in lpd:
        if len(i) >= 6:
            if i[0] == '#X' and i[1] == 'array' and i[2].find('sss') != -1:
                res.append(i)
    return res

def find_all_tables(lpd):
    res = []
    for i in lpd:
        if len(i) >= 6:
            if (i[0] == '#X'
                and i[1] == 'obj'
                and  i[4] == 'table'
                and i[5].find('sss') != -1):
                res.append(i)
    return res

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
    return (st, en)

def remove_canvas(lpd, st, en):
    res = []
    for i in range(len(lpd)):
        if i < st or i > en:
            res.append(lpd[i])
    return res

# ============================================================================ #
def calc_coords(coord, pos):
    x  = pos // coord['obj_r'] # position
    y  = pos %  coord['obj_r']
    ox = coord['obj_ox'] + (coord['obj_ix'] * x) # coords
    oy = coord['obj_oy'] + (coord['obj_iy'] * y)
    return(ox, oy)


def sss(lpd, ins_name):
    obj_cnv    = '__sss__'
    obj_par    = 'sss_par'
    obj_ar    = 'sss_ar'
    coord = {'obj_ox' : 20,  # offset
             'obj_oy' : 20,
             'obj_ix' : 350, # inc
             'obj_iy' : 24,
             'obj_r'  : 16} # row
    cnv_w = coord['obj_ox'] + (coord['obj_ix'] * 3) 
    cnv_h = coord['obj_oy'] + (coord['obj_iy'] * coord['obj_r']) + coord['obj_oy']

    # find and remove old obj_cnv
    st, en = find_canvas(lpd, obj_cnv)
    if st != -1 and en != -1:
        print('find old "%s" object' % (obj_cnv))
        lpd = remove_canvas(lpd, st, en)

    # find gui objects and arrays
    all_nbx     = find_all_object(lpd, 'nbx')
    all_hsl     = find_all_object(lpd, 'hsl')
    all_vsl     = find_all_object(lpd, 'vsl')
    all_tgl     = find_all_object(lpd, 'tgl')
    all_hradio  = find_all_object(lpd, 'hradio')
    all_vradio  = find_all_object(lpd, 'vradio')
    all_n_knob  = find_all_object(lpd, 'n_knob')
    all_arr     = find_all_arrays(lpd)
    all_tab     = find_all_tables(lpd)
    all_obj = (
        all_nbx +
        all_hsl +
        all_vsl +
        all_tgl +
        all_hradio +
        all_vradio +
        all_n_knob +
        all_arr +
        all_tab
    )

    obj = []

    # canvas
    s = '#N canvas 20 20 %d %d %s 0' % (cnv_w, cnv_h, obj_cnv)
    obj.append(s.split())

    pos = 0
    obj_n = 0
    ar_n = 0
    for l in all_obj:
        ox, oy  = calc_coords(coord, pos)
        pos += 1
        s = ''
       
        # 1) ins name
        # 2) $0
        # 3) $1
        # 4) $2
        # 5) number par
        # 6) type par
        # 7) label par
        # 8) rng lower par
        # 9) rng upper par
        # 10) step par

        if obj_n >= max_par:
            print('error: max par = %d' % (max_par))
            exit()

        if ar_n >= max_ar:
            print('error: max ar = %d' % (max_ar))
            exit()

        if l[4] == 'nbx':
            l[10] = '0'                   
            l[11] = '\$0-sss-s-%d' % (obj_n)  
            l[12] = '\$0-sss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d nbx %s %s %s 1' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])
            obj_n += 1

        elif l[4] == 'hsl':
            l[10] = '0'                   
            l[11] = '\$0-sss-s-%d' % (obj_n)  
            l[12] = '\$0-sss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d hsl %s %s %s 0.01' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])
            obj_n += 1

        elif l[4] == 'vsl':
            l[10] = '0'                   
            l[11] = '\$0-sss-s-%d' % (obj_n)  
            l[12] = '\$0-sss-r-%d' % (obj_n)  
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d vsl %s %s %s 0.01' % (
                ox, oy, obj_par, ins_name, obj_n, l[13], l[7], l[8])
            obj_n += 1

        elif l[4] == 'tgl':
            l[6] = '0'                    
            l[7] = '\$0-sss-s-%d' % (obj_n)   
            l[8] = '\$0-sss-r-%d' % (obj_n)   
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d tgl %s 0 %s 1' % (
                ox, oy, obj_par, ins_name, obj_n, l[9], l[18])
            obj_n += 1

        elif l[4] == 'hradio':
            l[7] = '0'                    
            l[9] = '\$0-sss-s-%d' % (obj_n)   
            l[10] = '\$0-sss-r-%d' % (obj_n)  
            rng = int(l[8]) - 1
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d hrd %s 0 %d 1' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], rng)
            obj_n += 1

        elif l[4] == 'vradio':
            l[7] = '0'                    
            l[9] = '\$0-sss-s-%d' % (obj_n)   
            l[10] = '\$0-sss-r-%d' % (obj_n)  
            rng = int(l[8]) - 1
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d vrd %s 0 %d 1' % (
                ox, oy, obj_par, ins_name, obj_n, l[11], rng)
            obj_n += 1

        elif l[4] == 'n_knob':
            l[16] = '0'                        
            l[17] = '\\\\\$0-sss-s-%d' % (obj_n)
            l[18] = '\\\\\$0-sss-r-%d' % (obj_n)
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d n_knob %s %s %s %s' % (
                ox, oy, obj_par, ins_name, obj_n, l[19], l[11], l[12], l[13])
            obj_n += 1

        elif l[1] == 'array':
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d %s' % (
                ox, oy, obj_ar, ins_name, ar_n, l[2])
            ar_n += 1

        elif l[4] == 'table':
            s = '#X obj %d %d %s %s \$0 \$1 \$2 %d %s' % (
                ox, oy, obj_ar, ins_name, ar_n, l[5])
            ar_n += 1

        if s != '':
            s = s.split()
            print('add:', ' '.join(s[4:]))
            obj.append(s)
        else:
            print('error:', l)
            exit()

    # canvas
    s = '#X restore 20 20 pd %s' % (obj_cnv)
    obj.append(s.split())

    # add to pd list
    if st != -1 and en != -1:
        j = st
        for i in obj:
            lpd.insert(j, i)
            j += 1
    else:
        for i in obj:
            lpd.append(i)

    print('done')
    return lpd


def sss_one_file(filename_in, filename_out):
    name = os.path.splitext(filename_in)[0].split('/')[-1]
    print('name: ', name)
    pdl = pdfile2pdlist(filename_in)
    pdl = sss(pdl, name)
    pdlist2pdfile(filename_out, pdl)

def sss_treat_files(files_in, files_out, quitet):
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
                sss_one_file(files_in[i], files_out[i])
        else:
            sss_one_file(files_in[i], files_out[i])


# ============================================================================ #
def sss_input(args):
    msg_err = """usage: 
    -i input_file.pd -o output_file.pd
    or
    -d /path/to/dir/with/pd/files"""
    f = 1
    # -f -o
    if args.i != '':
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
        files_in = [args.i]
        files_out = [args.o]
        files_in = find_pd_files(files_in, args.H)
    # dir
    else:
        path = path_norm(args.d)
        files_in = []
        if args.r:
            all_in_dir_rec(path, files_in)
        else:
            files_in = all_in_dir(path)
        files_in = find_pd_files(files_in, args.H)
        files_out = files_in

    sss_treat_files(files_in, files_out, args.q)

# ============================================================================ #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='pure data save state system script. version = %s' %
        (__version__))
    parser.add_argument('-i', default='', help='input file')
    parser.add_argument('-o', default='', help='output file')
    parser.add_argument('-d', default='', help='directory')
    parser.add_argument('-r', action='store_true', help='recursive')
    parser.add_argument('-H', action='store_true', help='with *help* files')
    parser.add_argument('-q', action='store_true', help='quitet')
    parser.set_defaults(func=sss_input)
    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
