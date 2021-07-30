#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from itertools import chain, islice

from sqlalchemy import Column, Integer, String, MetaData, Table, create_engine

out_db = 'webcorpus_conc.db'
engine = create_engine(f'sqlite:///{out_db}')
metadata = MetaData()

sqlite_table = Table('examples', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('left', String),
                     Column('word', String, index=True),
                     Column('right', String))
metadata.create_all(engine)


def chunked_iterator(iterable, chunksize):
    # Original source:
    # https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python/29524877#29524877
    it = iter(iterable)
    try:
        while True:
            yield chain((next(it),), islice(it, chunksize-1))
    except StopIteration:
        return


def do_insert(row_gen, chunksize=100000):
    with engine.connect() as conn:
        for i, batch in enumerate(chunked_iterator(row_gen, chunksize), start=1):
            with conn.begin():
                for table_vals in batch:
                    conn.execute(sqlite_table.insert(), table_vals)
            print(i * chunksize, flush=True)


def gen_rows(inp_fh=sys.stdin):
    for line in inp_fh:
        line = line.rstrip()
        word, left, right = line.split('\t', maxsplit=2)
        yield {'left': left, 'word': word, 'right': right}


if __name__ == '__main__':
    do_insert(gen_rows())
