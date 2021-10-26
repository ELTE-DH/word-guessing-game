#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from random import seed, sample
from argparse import ArgumentParser, FileType


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
                for c in conc_list:
                    print(c, file=out_fh)
            conc_list.clear()
            no += 1
            prev_word = word
            conc_list.append(line)

    if no in elems:
        for c1 in conc_list:
            print(c1, file=out_fh)


if __name__ == '__main__':
    parser = ArgumentParser(description='Use random sampling to limit the number of words to be guessed')
    parser.add_argument('-i', '--input', help='Input text file name (omit for STDIN)', required=False,
                        default=sys.stdin, type=FileType(encoding='UTF-8'))
    parser.add_argument('-o', '--output', help='Output text file name (omit for STDOUT)', required=False,
                        default=sys.stdout, type=FileType('w', encoding='UTF-8'))
    parser.add_argument('-c', '--count', help='Count of words in the list to sample', required=True, type=int)
    parser.add_argument('-k', '--keep', help='Count of words to keep after sampling', required=True, type=int)
    args = parser.parse_args()
    sampled = set(sample(range(args.count), args.keep))
    select_elems(args.input, args.output, sampled)
