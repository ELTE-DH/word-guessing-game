#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from itertools import islice, tee
from string import ascii_lowercase
from argparse import ArgumentParser, FileType


LOWERCASE_LETTERS_HUN = set(ascii_lowercase+'áéíóöőúüű')
NON_WORDS = set()
with open('non_words.txt', encoding='UTF-8') as fh:
    for elem in fh:
        elem = elem.rstrip()
        NON_WORDS.add(elem)


def n_gram_iter(input_iterator, n):
    return zip(*(islice(it, i, None) for i, it in enumerate(tee(iter(input_iterator), n))))


def create_context_main(inp_fh=sys.stdin, out_fh=sys.stdout,
                        word_min_len=4, word_max_len=15,
                        left_cont_len=5, right_cont_len=5):
    ngram_len = left_cont_len + 1 + right_cont_len
    right_cont_index = left_cont_len + 1
    for line in inp_fh:
        line = line.rstrip().split(' ')
        for entry in n_gram_iter(line, ngram_len):
            pre = entry[:left_cont_len]
            word = entry[left_cont_len]
            post = entry[right_cont_index:]
            if word_min_len <= len(word) <= word_max_len and LOWERCASE_LETTERS_HUN.issuperset(word) and \
                    word not in NON_WORDS:
                print(word, ' '.join(pre), ' '.join(post), sep='\t', file=out_fh)


if __name__ == '__main__':
    parser = ArgumentParser(description='Create word context for sentence per line (SPL) formatted sentences')
    parser.add_argument('-i', '--input', help='Input text file name (omit for STDIN)', required=False,
                        default=sys.stdin, type=FileType(encoding='UTF-8'))
    parser.add_argument('-o', '--output', help='Output text file name (omit for STDOUT)', required=False,
                        default=sys.stdout, type=FileType('w', encoding='UTF-8'))
    parser.add_argument('-s', '--word-min-len', help='Minimum (inclusive) word length in characters', required=True,
                        type=int)
    parser.add_argument('-m', '--word-max-len', help='Maximum (inclusive) word length in characters', required=True,
                        type=int)
    parser.add_argument('-l', '--left-cont-len', help='Length of left context in words', required=True, type=int)
    parser.add_argument('-r', '--right-cont-len', help='Length of right context in words', required=True, type=int)
    args = parser.parse_args()
    create_context_main(args.input, args.output, args.word_min_len, args.word_max_len, args.left_cont_len,
                        args.right_cont_len)
