#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = '0.4'

# ---------------------------------------------------------------------------- #
import os
import argparse
import re


# ---------------------------------------------------------------------------- #
# files
# ---------------------------------------------------------------------------- #
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

# ---------------------------------------------------------------------------- #
# print
# ---------------------------------------------------------------------------- #
def split():
    print('='*80)


# ---------------------------------------------------------------------------- #
# convert pd file
# ---------------------------------------------------------------------------- #
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
    return res

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
            l[13] = '\\\\\$0-pdss-s-%d' % (obj_n)   
            l[14] = '\\\\\$0-pdss-r-%d' % (obj_n)   
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
            all_in_dir_rec(path, files_in)
        else:
            files_in = all_in_dir(path)
        files_in = find_pd_files(files_in, args.H)
        files_out = files_in

    pdss_treat_files(files_in, files_out, args.q)


# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='pure data save state script. version = %s' % (__version__))

    parser.add_argument('-f', default='', help='input file')
    parser.add_argument('-o', default='', help='output file')
    parser.add_argument('-d', default='', help='directory')
    parser.add_argument('-r', action='store_true', help='recursive')
    parser.add_argument('-H', action='store_true', help='with *help* files')
    parser.add_argument('-q', action='store_true', help='quitet')
    parser.set_defaults(func=pdss_input)

    args = parser.parse_args()
    if not vars(args):
        parser.print_usage()
    else:
        args.func(args)
