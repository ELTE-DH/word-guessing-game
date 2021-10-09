#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from random import seed, sample


# Set random seed for reproducibility
seed(12345)


def select_elems(inp_fh, out_fh, elems):
    prev_word = None
    conc_list = []
    no = -1
    for line in inp_fh:
        line = line.rstrip()
        word, left, right, freq = line.split('\t', maxsplit=3)
        if word == prev_word:
            conc_list.append(line)
        else:
            if no in elems:
                sample_elems(conc_list, out_fh)
            conc_list.clear()
            no += 1
            prev_word = word
            conc_list.append(line)

    if no in elems:
        sample_elems(conc_list, out_fh)


def sample_elems(conc_list, out_fh):
    for c in conc_list:
        print(c, file=out_fh)


if __name__ == '__main__':
    count_all = 653813
    sampled = set(sample(range(count_all), 8000))
    select_elems(sys.stdin, sys.stdout, sampled)
