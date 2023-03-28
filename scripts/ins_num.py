#!/usr/bin/env python3

import sys
import os
import re
import shutil

def all_files_in_dir_recursive(dir, hiden, inv, regex):
    global files

    # norm path
    if dir[-1] != '/':
        dir = dir + '/'

    # listdir
    d = []
    try:
        d = os.listdir(dir)
    except:
        print("error: listdir:", dir)

    # find and path
    files_found = []
    for i in d:
        path = dir + i
        # directory ?
        if os.path.isdir(path):
            # is link ?
            if not os.path.islink(path):
                # read ?
                if os.access(path, os.R_OK):
                    # .hidden ?
                    if hiden:
                        if i[0] != '.':
                            all_files_in_dir_recursive(path, hiden, inv, regex)
                    else:
                        all_files_in_dir_recursive(path, hiden, inv, regex)
        # file
        else:
            if regex:
                r = regex.search(i)
                if inv:
                    if not r:
                        files_found.append(path)
                else:
                    if r:
                        files_found.append(path)
            else:
                files_found.append(path)

    # add to global
    files = files + files_found


def split_snap_name(name):
    n = name.split('.')
    abs_name = n[0]
    pro_name = n[1]
    snap = n[2]
    return (abs_name, pro_name, snap)


# arg
try:
    dir_sss = sys.argv[1]
    dir_sss_snap = dir_sss + 'snap/'
    dir_sss_pro = dir_sss + 'pro/'
    dir_sss_new = sys.argv[2]
    dir_my_pd = sys.argv[3]
    print(dir_sss_snap, dir_sss_pro, dir_my_pd)
except:
    print('usage: <dir_sss> <dir_sss_new> <dir_my_pd>')
    exit (0)


# ls sss snap
all_pro = os.listdir(dir_sss_pro)

files = []
regex = re.compile('.pd$')
all_files_in_dir_recursive(dir_my_pd, True, False, regex)


founded = []
for i in all_pro:
    found=False
    for j in files:
        if i in j:
            found=True
            print('-'*80)
            print(i, j)
            founded.append([i,j])
            fd = open(j)
            d = fd.readlines()
            for k in d:
                k = k.strip()
                k = k.split(' ')
                if len(k) >= 5:
                    if k[4].find('i_') == 0:
                        ins = k[4]
                        dollar = k[5]
                        num = k[6]
                        if num[-1] == ';':
                            num = num[:-1]
                        num = int(num)
                        p = dir_sss_snap + ins + '/.' + i + '.default.'
                        pr = dir_sss_new + ins + '/.' + i + '.default.' + str(num) + '.'
                        for l in range(0, 32):
                            filename     = dir_sss_snap + ins + '/.' + i + '.default.'                  + str(l)
                            filename_new = dir_sss_new  + ins + '/.' + i + '.default.' + str(num) + '.' + str(l)
                            if os.path.isfile(filename):
                                print(filename, '->', filename_new)
                                shutil.copyfile(filename, filename_new)
    if found==False:
        print('error find for:', i)

