#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from random import seed, sample


# Set random seed for reproducibility
seed(12345)


def select_elems(inp_fh, out_fh, no_of_elements=30):
    prev_word = None
    conc_list = []
    for line in inp_fh:
        line = line.rstrip()
        word, left, right = line.split('\t', maxsplit=2)
        if word == prev_word:
            conc_list.append(line)
        else:
            sample_elems(conc_list, no_of_elements, out_fh)
            prev_word = word
            conc_list.append(line)
    sample_elems(conc_list, no_of_elements, out_fh)


def sample_elems(conc_list, no_of_elements, out_fh):
    if len(conc_list) > no_of_elements:
        chosen_concs = sample(conc_list, no_of_elements)
    else:
        chosen_concs = conc_list
    for c in chosen_concs:
        print(c, file=out_fh)
    conc_list.clear()


if __name__ == '__main__':
    select_elems(sys.stdin, sys.stdout)
