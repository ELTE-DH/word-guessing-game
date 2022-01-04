#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from random import seed, sample
from argparse import ArgumentParser, FileType


# Set random seed for reproducibility
seed(12345)


def select_elems(inp_fh, out_fh, no_of_elements=30):
    conc_list = []
    lefts = set()
    rights = set()
    sents = set()
    words = set()
    left_size, right_size = 4, 4
    for line in inp_fh:
        line = line.rstrip()
        word, left, right, sent = line.split('\t', maxsplit=3)
        # TODO generalize this!
        left_truncated, right_truncated = turncate_context(left, right, left_size, right_size)
        # Checking the smallest context is enough!
        if word not in words and sent not in sents and left_truncated not in lefts and right_truncated not in rights:
            lefts.add(left_truncated)
            rights.add(right_truncated)
            sents.add(sent)
            words.add(word)
            conc_list.append((word, left, right, sent))

    chosen_concs = sample(conc_list, no_of_elements)
    for sent_id, (word, left, right, sent) in enumerate(chosen_concs, start=1):
        # TODO generalize this
        for left_size, right_size in ((4, 0), (0, 4), (4, 4), (8, 0), (0, 8), (8, 8)):
            left_truncated, right_truncated = turncate_context(left, right, left_size, right_size)
            print(word, left_truncated, right_truncated, sent, sent_id, sep='\t', file=out_fh)


def turncate_context(left, right, left_size, right_size):
    left_split = left.split(' ')
    right_split = right.split(' ')
    left_truncated = ' '.join(left_split[max(len(left_split) - left_size, 0):])
    right_truncated = ' '.join(right_split[:min(right_size, len(right_split))])
    return left_truncated, right_truncated


if __name__ == '__main__':
    parser = ArgumentParser(description='Select random contexts for each word to ballance frequent and rare words')
    parser.add_argument('-i', '--input', help='Input text file name (omit for STDIN)', required=False,
                        default=sys.stdin, type=FileType(encoding='UTF-8'))
    parser.add_argument('-o', '--output', help='Output text file name (omit for STDOUT)', required=False,
                        default=sys.stdout, type=FileType('w', encoding='UTF-8'))
    parser.add_argument('-n', '--no-of-conts', help='Number of context for each word to keep', required=True, type=int)
    args = parser.parse_args()
    select_elems(args.input, args.output, args.no_of_conts)
