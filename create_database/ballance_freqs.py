#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from random import seed, sample
from argparse import ArgumentParser, FileType


# Set random seed for reproducibility
seed(12345)


def select_elems(inp_fh, out_fh, no_of_elements=30):
    prev_word = None
    conc_list = []
    for line in inp_fh:
        line = line.rstrip()
        word, left, right, sent = line.split('\t', maxsplit=3)
        if word == prev_word:
            conc_list.append(line)
        else:
            sample_elems(conc_list, no_of_elements, out_fh)
            prev_word = word
            conc_list.append(line)
    sample_elems(conc_list, no_of_elements, out_fh)


def sample_elems(conc_list, no_of_elements, out_fh):
    freq = len(conc_list)
    if freq > no_of_elements:
        chosen_concs = sample(conc_list, no_of_elements)
    else:
        chosen_concs = conc_list
    for c in chosen_concs:
        print(c, freq, sep='\t', file=out_fh)
    conc_list.clear()


if __name__ == '__main__':
    parser = ArgumentParser(description='Select random contexts for each word to ballance frequent and rare words')
    parser.add_argument('-i', '--input', help='Input text file name (omit for STDIN)', required=False,
                        default=sys.stdin, type=FileType(encoding='UTF-8'))
    parser.add_argument('-o', '--output', help='Output text file name (omit for STDOUT)', required=False,
                        default=sys.stdout, type=FileType('w', encoding='UTF-8'))
    parser.add_argument('-n', '--no-of-conts', help='Number of context for each word to keep', required=True, type=int)
    args = parser.parse_args()
    select_elems(args.input, args.output, args.no_of_conts)
