#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from collections import Counter
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db = create_engine('sqlite:///PrevCons.sqlite3')
base = declarative_base(bind=db.engine)

table_objs = {table_name: Table(table_name, base.metadata, autoload=True) for table_name in db.engine.table_names()}
table_column_objs = {(table_name, col_obj.key): col_obj for table_name, table_obj in table_objs.items()
                     for col_obj in table_obj.columns}

with sessionmaker(db)() as session:
    query = session.query(table_objs['prevcons']).select_from(table_objs['prevcons']).\
        with_entities(table_column_objs[('prevcons', 'prev')], table_column_objs[('prevcons', 'actform')],
                      table_column_objs[('prevcons', 'clause')])
    for prev, actform, clause in query.all():
        if not actform.startswith(prev):
            print('ERROR: prev is not the prefix of act form', prev, actform, clause, sep='\t', file=sys.stderr)
        elif actform not in {e.lower() for e in clause.split(' ')}:  # Allow sentence starter tokens!
            print('ERROR: actform is not a token in clause', prev, actform, clause, sep='\t', file=sys.stderr)
        elif Counter(e.lower() for e in clause.split(' '))[actform] > 1:
            print('ERROR: actform has more occurences as token in clause', prev, actform, clause, sep='\t',
                  file=sys.stderr)
        else:
            tokens = clause.split(' ')
            left = []
            word = prev
            right = []
            for i, t in enumerate(tokens):
                if t.lower() == actform:
                    left = tokens[:i]
                    right = tokens[i+1:]
                    right.insert(0, t[len(prev):])
                    break
            print(word, ' '.join(left), ' '.join(right), sep='\t')

"""
./venv/bin/python3 filter_prevcons.py | sort --parallel=$(nproc) -T ~/tmp -S10% --compress-program=pigz | \
 ./create_database/uniq_2nd_field.sh | ./create_database/uniq_3rd_field.sh | ./venv/bin/python3 create_prevcons_db.py
"""