#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import json
import pickle
from datetime import datetime
from collections import defaultdict

from context_bank import ContextBank
from main import load_and_validate_config

# Parameters
CONFIG_FILENAME = 'config.yaml'
LOG_FILENAME = 'results.log'
PICKLE_FILENAME = 'guess_data.pickle'


def read_and_format_log_data(log_filename, config):
    cb = ContextBank(config['db_config'],
                     config['contextbank_config']['left_size'],
                     config['contextbank_config']['right_size'],
                     config['contextbank_config']['hide_char'])

    by_uuid = defaultdict(list)
    with (open(log_filename, encoding='UTF-8') as fh):
        for line in fh:
            if '\t' not in line or ' werkzeug ' in line:
                continue  # Omit startup sequence and werkzeug logs
            first_part, command, contexts, guesses, *url_path_part = line.rstrip().split('\t', maxsplit=4)
            if command in {'None', 'new_game', 'next_line', 'give_up'}:
                continue  # Drop lines where no new guesses including the first page of a visitor (None)
            timestamp_str, logger_name, level, uuid = first_part.split(' - ')
            timestamp = datetime.fromisoformat(timestamp_str)
            contexts = json.loads(contexts)
            guesses = json.loads(guesses.replace("'", '"'))
            resolved_contexts = [tuple(cb.select_one_random_line(line_id=c, hide_word=False)[0]) for c in contexts]
            if len(resolved_contexts) != len(contexts):
                raise ValueError(f'Some contexts could not be found ({contexts} vs. {resolved_contexts}) !')
            # Format and store the output (there could be parallel UUIDs/players, store them separately)
            by_uuid[uuid].append((timestamp, resolved_contexts, guesses))
    return by_uuid


def filter_guess_entries(by_uuid):
    guess_data = []
    for uuid, records in by_uuid.items():
        # Keep the last guess of a round (which includes all previous guesses).
        # The guesses of each rounds should be continuous.
        sorted_records = sorted(records)
        record_iter = iter(sorted_records)
        previous = next(record_iter, None)
        if previous is None:
            raise NotImplementedError('Nonsense state, there should be at least one element!')
        for current in record_iter:
            prev_timestamp, prev_contexts, prev_guesses = previous
            curr_timestamp, curr_contexts, curr_guesses = current
            # Warning: Asking for new contexts does not have separate entries
            # Here for a specific set of contexts, the final set of guesses are filtered,
            # subset relation for contexts may present for the same guesses
            if prev_contexts != curr_contexts or prev_guesses != curr_guesses[:-1]:
                guess_data.append((uuid, prev_timestamp, prev_contexts, prev_guesses))
            previous = current
        # Store the final one if exists
        if len(records) > 1:
            timestamp, contexts, guesses = previous
            guess_data.append((uuid, timestamp, contexts, guesses))

    return guess_data


def main(config_filename, log_filename, pickle_filename):

    config = load_and_validate_config(config_filename)

    by_uuid = read_and_format_log_data(log_filename, config)

    # Keep entries which include all previous guesses for the same set of contexts
    guess_data = filter_guess_entries(by_uuid)

    # Store for further processing
    with open(pickle_filename, 'wb') as fh:
        pickle.dump(guess_data, fh)


if __name__ == '__main__':
    main(CONFIG_FILENAME, LOG_FILENAME, PICKLE_FILENAME)
