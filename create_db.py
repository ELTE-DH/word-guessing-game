#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import csv
from pathlib import Path

from sqlalchemy import create_engine, MetaData, Table, Column, String, insert, Index, Integer

"""Example for creating a database from a TSV file"""

# File and DB config
tsv_path = Path('examples.tsv')
sqlite_path = Path('database.db')

# Step 1: Read header and rows from TSV
with tsv_path.open(encoding='UTF-8') as f:
    reader = csv.DictReader(f, delimiter='\t', quotechar=None, quoting=csv.QUOTE_NONE)
    rows = list(reader)
    headers = list(reader.fieldnames)

# Step 2: Set column types
column_types = {}
for header in headers[1:]:
    column_types[header] = String

# Step 3: Create SQLAlchemy table
engine = create_engine(f'sqlite:///{sqlite_path}', future=True)
metadata = MetaData()

columns = [Column('id', Integer, primary_key=True, autoincrement=True)] + \
          [Column(col_name, String) for col_name in headers[1:]]

table = Table('lines', metadata, *columns)

# Add index on the last column
Index(f'ix_data_{headers[-1]}', table.c[headers[-1]])

# Step 4: Create the table in SQLite
metadata.create_all(engine)

# Step 5: Insert the data
with engine.connect() as conn:
    conn.execute(insert(table), rows)
    conn.commit()

print(f'Done. Imported {len(rows)} rows into {sqlite_path}')
