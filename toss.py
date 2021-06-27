#!/usr/bin/python3

# ---------------------------------------------------------------------------- #
import sys
import os

# ---------------------------------------------------------------------------- #
def file2pdlist(filename):
    "convert pd file to list"
    try:
        fd = open(filename)
    except:
        print("error open %s" % (filename))
        exit()

    l = fd.readlines()
    res = []
    s = ''
    for i in l:
        i = i.strip()
        s = s + ' ' + i
        if i[-1] == ';':
            s = s.strip().split()
            res.append(s)
            s = ''
    fd.close()
    print("file %s to list : done." % (filename))
    return(res)


# ---------------------------------------------------------------------------- #
def pdlist2file(filename, l):
    "convert list to pd file"
    try:
        fd = open(filename, 'w')
    except:
        print("error open %s" % (filename))
        exit()

    for i in l:
        s = ''
        for j in i:
            s = s + ' ' + j
        s = s.strip()
        fd.write(s)
        fd.write('\n')
    fd.close()
    print("list to file %s : done." % (filename))

# ---------------------------------------------------------------------------- #
def print_list(l):
    "print list"
    s = ''
    for i in l:
        s = s + ' ' + i
        if len(s) > 80:
            s = s[:74]
            s = s + ' >'
            break
    return(s.strip())

# ---------------------------------------------------------------------------- #
def insert_string(s, l , pos):
    "insert string to list"
    l.insert(pos, s.split())


# ---------------------------------------------------------------------------- #
def create_ss(lpd, ins_name):
    "remove old ps ss, find ss objects and create new pd ss"
    res = []

    #####################################################################
    # find and remove ss
    num = 0
    find = 0
    st = -1
    for s in lpd:
        if find == 0 and s[0] == '#N' and s[1] == 'canvas' and s[6] == 'ss':
            find = 1
            st = num
        
        if find == 0:
            res.append(s)
            print("%-4d +" % (num), print_list(s))
        else:
            print("%-4d -" % (num), print_list(s))

        if find == 1 and s[0] == '#X' and s[1] == 'restore' and s[5] == 'ss;':
            find = 0

        num += 1

    if st == -1:
        st = num
        print('pd ss not found. st = ', st)
    else:
        print('pd ss found. st = ', st)


    #####################################################################
    # find ss objects
    obj = []
    obj_n = 0
    arr = []
    arr_n = 0
    for s in res:
        if s[0] == '#X' and s[1] == 'obj':

            if s[4] == 'tgl':
                s[7] = '\$0_s_%d' % (obj_n)
                s[8] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[9]))

            elif s[4] == 'hradio':
                s[9] = '\$0_s_%d' % (obj_n)
                s[10] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[11]))

            elif s[4] == 'vradio':
                s[9] = '\$0_s_%d' % (obj_n)
                s[10] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[11]))

            elif s[4] == 'nbx':
                s[11] = '\$0_s_%d' % (obj_n)
                s[12] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[13]))

            elif s[4] == 'hsl':
                s[11] = '\$0_s_%d' % (obj_n)
                s[12] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[13]))

            elif s[4] == 'vsl':
                s[11] = '\$0_s_%d' % (obj_n)
                s[12] = '\$0_r_%d' % (obj_n)
                obj_n += 1
                obj.append(s)
                print('find: %s %s' % (s[4], s[13]))

    # add array for par
    arr_for_par_s = '#X obj 10 114 table \$0_ss_a_0 %d;' % (ALL_SNAP * obj_n)
    arr_for_par = arr_for_par_s.split()
    obj.append(arr_for_par)
    print('add : table %s (par)' % (arr_for_par[5]))


    # find array objects
    for s in res:
        if s[0] == '#X' and s[1] == 'array':
            arr_name = s[2]
            if arr_name[-2] == 's' and arr_name[-1] == 's':
                obj.append(s)
                print('find: array %s' % (s[2]))



    #####################################################################
    # insert pd ss
    insert_string('#N canvas 20 20 900 500 ss 0;', res , st)
    st += 1; insert_string('#X text 10 10 automatic created by toss.py;', res, st)
    st += 1; insert_string('#X text 10 30 delete this canvas if you change structure path;', res, st)
    st += 1; insert_string('#X text 10 50 and run: toss.py <%s.pd> <%s.pd>;' % (ins_name,ins_name), res, st)
    st += 1; insert_string('#X obj 10 70 r \$0_ss_snap;', res, st)
    st += 1; insert_string('#X obj 10 92 n_ss_snap %s \$0 \$1 %d;' % (ins_name, obj_n), res, st)
    st += 1; insert_string(arr_for_par_s, res, st)

    # insert odj's and array's
    obj_ox = 10
    obj_oy = 140
    obj_ix = 300
    obj_iy = 28
    obj_r = 16
    obj_n = 0
    arr_n = 0
    for i in obj:

        x  = obj_n // obj_r
        y  = obj_n % obj_r
        ox = obj_ox + (obj_ix * x)
        oy = obj_oy + (obj_iy * y)

        # 1) ins name
        # 2) $0
        # 3) $1
        # 4) number
        # 5) type obj (tgl, hradio, vradio, nbx, vsl, hsl)
        # 6) name
        # 7) lower
        # 8) upper

        if i[4] == 'tgl':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d tgl %s 0 1;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[9])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             
        elif i[4] == 'hradio':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d hrd %s 0 %s;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[11],
                i[8])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             
        elif i[4] == 'vradio':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d vrd %s 0 %s;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[11],
                i[8])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             

        elif i[4] == 'nbx':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d nbx %s %s %s;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[13],
                i[7],
                i[8])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             
        elif i[4] == 'hsl':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d hsl %s %s %s;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[13],
                i[7],
                i[8])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             
        elif i[4] == 'vsl':
            s = '#X obj %d %d n_ss_par %s \$0 \$1 %d vsl %s %s %s;' % (
                ox, oy,
                ins_name,
                obj_n,
                i[13],
                i[7],
                i[8])
            st += 1; insert_string(s, res, st)
            obj_n += 1
             
        # 1) ins name
        # 2) $0
        # 3) $1
        # 4) number
        # 5) name

        elif i[4] == 'table':
            s = '#X obj %d %d n_ss_array %s \$0 \$1 %d %s;' % (
                ox, oy,
                ins_name,
                arr_n,
                i[5])
            st += 1; insert_string(s, res, st)
            obj_n += 1
            arr_n += 1
             
        elif i[1] == 'array':
            s = '#X obj %d %d n_ss_array %s \$0 \$1 %d %s;' % (
                ox, oy,
                ins_name,
                arr_n,
                i[2])
            st += 1; insert_string(s, res, st)
            obj_n += 1
            arr_n += 1
             
    # end canvas and connect
    st += 1; insert_string('#X connect 3 0 4 0;', res, st)
    st += 1; insert_string('#X restore 20 50 pd ss;', res, st)

    return(res)


# ---------------------------------------------------------------------------- #
def parse_pd(filename_in, filename_out):
    "main parse function"

    # name
    ins_name = os.path.splitext(filename_in)[0]

    # file to list
    pd = []
    pd = file2pdlist(filename_in)

    # ss
    pd = create_ss(pd, ins_name)

    # write
    pdlist2file(filename_out, pd)


# ---------------------------------------------------------------------------- #
# constant
global ALL_SNAP
ALL_SNAP = 256

# ---------------------------------------------------------------------------- #
filename_in  = None
filename_out = None
try:
    filename_in  = sys.argv[1]
    filename_out = sys.argv[2]
except:
    print('usage: <file_in.pd> <file_out.pd>')
    exit()

parse_pd(filename_in, filename_out)

# ---------------------------------------------------------------------------- #
# pd lines

#N canvas ox oy w h name|(subpath) view;
#X restore r_ox r_oy pd name|(subpath);
#X coords 0 -1 1 1 350 60 1 100 150;

#X obj ox oy obj_name [...];

#X obj ox oy nbx W H lower upper ? ? snd rcv lab ldx ldy fn fs bc fc lc ? logW;
#X obj ox oy vsl W H lower upper ? ? snd rcv lab ldx ldy fn fs bc fc lc ? ?;
#X obj ox oy hsl W H lower upper ? ? snd rcv lab ldx ldy fn fs bc fc lc ? ?;
#X obj ox oy tgl size ? snd rcv lab ldx ldy fn fs bc fc lc ? ?;
#X obj ox oy hradio size ? ? nc snd rcv lab ldx ldy fn fs bc fc lc ?;
#X obj ox oy vradio size ? ? nc snd rcv lab ldx ldy fn fs bc fc lc ?;

#X text ox oy text text text, f w;
#X msg ox oy text;
#X floatatom ox oy w lower upper side snd rcv lab;
#X symbolatom ox oy w lower upper side snd rcv lab;

#N canvas ox oy w h (subpath) view;
#X array name size float f;
#A [...];
#X coords f f f f f f f f;
#X restore r_ox r_oy graph;

#X connect obj_out out obj_in in;
