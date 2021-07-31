#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from itertools import chain, islice
from argparse import ArgumentParser

from sqlalchemy import Column, Integer, String, MetaData, Table, create_engine


def create_db(db_fn):
    engine = create_engine(f'sqlite:///{db_fn}')
    metadata = MetaData()

    sqlite_table = Table('examples', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('left', String),
                         Column('word', String, index=True),
                         Column('right', String))
    metadata.create_all(engine)

    return engine, sqlite_table


def chunked_iterator(iterable, chunksize):
    # Original source:
    # https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python/29524877#29524877
    it = iter(iterable)
    try:
        while True:
            yield chain((next(it),), islice(it, chunksize-1))
    except StopIteration:
        return


def do_insert(row_gen, engine, sqlite_table, chunksize=100000):
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


def parse_args():
    parser = ArgumentParser(description='Create SQLite concordance database from TSV file (word, left, rigth)')
    parser.add_argument('-f', '--db-filename', dest='db_filename', required=True,
                        help='The filename of the SQLite database', metavar='DBNAME.db')
    options = vars(parser.parse_args())

    return options


def main():
    opts = parse_args()
    db_engine, table_name = create_db(opts['db_filename'])
    do_insert(gen_rows(), db_engine, table_name)


if __name__ == '__main__':
    main()
