#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys
from uuid import uuid4
from logging.config import dictConfig

from yaml import load as yaml_load, SafeLoader
from flask_sqlalchemy import SQLAlchemy
from yamale import make_schema, make_data, validate, YamaleError
from flask import request, flash, session, Flask, render_template, current_app

from context_bank import ContextBank
from guesser_helper import word_similarity, dummy_similarity_fun, guess


def load_and_validate_config(config_filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml'),
                             config_schema_filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                 'config_schema.yaml')):
    """Load YAML config and validate it with the given schema"""

    # Load Schema
    with open(config_schema_filename, encoding='UTF-8') as fh:
        schemafile_content = fh.read()
    config_schema = make_schema(content=schemafile_content)

    # Load Data
    with open(config_filename, encoding='UTF-8') as data_fh:
        data_content = data_fh.read()
    data = make_data(content=data_content)

    # Validate
    try:
        validate(config_schema, data)
    except YamaleError as e:
        for result in e.results:
            print('Error validating data {0} with {1}:'.format(result.data, result.schema), file=sys.stderr)
            for error in result.errors:
                print('', error, sep='\t', file=sys.stderr)
        exit(1)

    return data[0][0]


def validate_config_special(config):
    config['ui_strings']['footer'] = config['ui_strings']['footer'].replace(r':\ ', ': ')
    if config['guesser_config']['baseurl'] is not None:
        config['guesser_config']['word_similarity_fun'] = word_similarity
    else:
        config['guesser_config']['word_similarity_fun'] = dummy_similarity_fun
    if (config['guesser_config']['baseurl'] is not None and
        config['guesser_config']['guesser'] is None) or \
            (config['guesser_config']['baseurl'] is None and
             config['guesser_config']['guesser'] is not None):
        raise ValueError('Both or none of gueser_config/guesser_baseurl and gueser_config/guesser_name must be null!')


def create_app(config_filename='config.yaml'):
    """Create and configure the app (and avoid globals as possible)"""

    # Read configuration
    config = load_and_validate_config(config_filename)
    validate_config_special(config)

    # Read logging configuration
    with open('logging.cfg') as fh:
        dictConfig(yaml_load(fh, SafeLoader))

    # Setup Flask application
    flask_app = Flask('word-guessing-game')
    flask_app.config.from_mapping(APP_SETTINGS=config,
                                  SECRET_KEY='any random string',
                                  SQLALCHEMY_DATABASE_URI=f'sqlite:///{config["db_config"]["database_name"]}',
                                  SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                  # JSONIFY_PRETTYPRINT_REGULAR=True,
                                  # JSON_AS_ASCII=False,
                                  )
    app_settings = flask_app.config['APP_SETTINGS']

    # Setup SQLAlchemy database for pythonic usage (column obj to name mapping)
    db = SQLAlchemy(flask_app)
    with flask_app.app_context():
        left_size = config['contextbank_config']['left_size']
        right_size = config['contextbank_config']['right_size']
        hide_char = config['contextbank_config']['hide_char']
        app_settings['context_bank'] = ContextBank(config['db_config'], db, left_size, right_size, hide_char)

    @flask_app.route('/')  # So one can create permalink for states!
    # @auth.login_required
    def index():
        """Control the query in a stateless manner"""

        settings = current_app.config['APP_SETTINGS']
        # Parse parameters and put errors into messages if necessary
        messages, next_action, displayed_line_ids, this_player, other_player = parse_params(settings['ui_strings'])

        # Create random session id to identify users
        if 'id' not in session:
            session['id'] = uuid4()
        # Log parameters and URL query string
        all_guesses = this_player[0][:]
        all_guesses.append(this_player[1])
        current_app.logger.info(
            '\t'.join(map(str, (session['id'], next_action, displayed_line_ids, all_guesses,
                                request.query_string.decode()))))

        # Execute one step in the game if there were no errors, else do nothing
        messages, displayed_lines, buttons_enabled, prev_guesses_this, prev_guesses_other, other_guess_state = \
            game_logic(messages, next_action, displayed_line_ids, this_player, other_player,
                       settings['guesser_config'], settings['ui_strings'], settings['context_bank'])

        # Display messages (errors and informational ones)
        for m in messages:
            flash(m)

        # Render output HTML
        out_content = render_template('layout.html', ui_strings=settings['ui_strings'], buttons_enabled=buttons_enabled,
                                      previous_guesses=prev_guesses_this, previous_guesses_other=prev_guesses_other,
                                      displayed_lines=displayed_lines, other_guess_state=other_guess_state)
        return out_content

    return flask_app


def parse_params(ui_strings):
    """Parse input parameters (Flask-specific)"""
    messages = []

    prev_guesses = request.args.getlist('previous_guesses[]')
    prev_guesses_other = request.args.getlist('previous_guesses_other[]')
    other_guess_state = request.args.get('other_guess_state', '0')
    if other_guess_state not in {'0', '1', '2'}:
        messages.append(ui_strings['other_guess_state_invalid'])

    guessed_word = request.args.get('guessed_word')
    if 'guess' in request.args and guessed_word is None:
        messages.append(ui_strings['no_guessed_word_specified'])

    displayed_line_ids = request.args.getlist('displayed_lines[]', int)

    if len({'guess', 'give_up', 'next_line'}.intersection(request.args.keys())) > 0 and len(displayed_line_ids) == 0:
        messages.append(ui_strings['no_displayed_lines_specified'])

    for action in ('guess', 'next_line', 'give_up', 'new_game', 'new_game_vs_other'):
        if action in request.args:
            next_action = action
            break
    else:
        next_action = None

    if len(request.args) > 0 and next_action is None:
        messages.append(ui_strings['no_action_specified'])

    if next_action == 'new_game':
        other_guess_state = '2'  # Gave up if no other player is specified
    if next_action == 'new_game_vs_other':
        next_action = 'new_game'
        other_guess_state = '0'

    return messages, next_action, displayed_line_ids, (prev_guesses, guessed_word), \
        (prev_guesses_other, other_guess_state)


def game_logic(messages, action, displayed_lines, this_player, other_player, guesser_config, ui_strings, context_bank):
    """The main logic of the game"""
    previous_guesses, guessed_word = this_player
    previous_guesses_other, other_guess_state = other_player

    buttons_enabled = {'guess': True, 'next_line': True, 'give_up': True, 'new_game': True}

    if len(messages) > 0 or action is None:
        # There were errors
        lines_to_display = []
        buttons_enabled = {'guess': False, 'next_line': False, 'give_up': False, 'new_game': True}
    elif action == 'guess':
        # Get the word for ID and check it. If matches reveal word in displayed lines
        word, _ = context_bank.identify_word_from_id(displayed_lines[0])  # Empty list is handled in parse_params()
        if word == guessed_word:
            hide_word = False
            messages.append(ui_strings['win'])
            buttons_enabled = {'guess': False, 'next_line': False, 'give_up': False, 'new_game': True}
        else:
            hide_word = True
            messages.append(ui_strings['incorrect_guess'])
            previous_guesses.append(guessed_word)

        lines_to_display, _ = context_bank.read_all_lines_for_word(word, displayed_lines, hide_word=hide_word)

        if guesser_config.get('baseurl') is not None and other_guess_state == '0':
            other_guesses, msg = guess(guesser_config, lines_to_display, word, previous_guesses_other)
            other_guess = other_guesses[0]  # Always padded to top_n with '_' characters
            if len(msg) == 0:
                if word == other_guess:
                    messages.append(ui_strings['other_win'])
                    other_guess_state = '1'
                elif other_guess == '_':
                    other_guess_state = '2'
                    messages.append(ui_strings['other_gave_up'])
                else:
                    previous_guesses_other.append(other_guess)
            else:
                messages.append(f'{ui_strings["error"]}: {msg}')

    elif action == 'next_line':
        # Read lines for the word, display already shown and select a new one
        lines_to_display, new_lines = context_bank.read_all_lines_for_word(None, displayed_lines, hide_word=True)

        # Select a new line to display and insert it to the top
        if len(new_lines) > 0:
            lines_to_display.insert(0, new_lines[0])
        else:
            buttons_enabled['next_line'] = False
            messages.append(ui_strings['no_more_line_for_word'])
    elif action == 'give_up':
        # Reveal word in already displayed lines
        buttons_enabled = {'guess': False, 'next_line': False, 'give_up': False, 'new_game': True}
        lines_to_display, _ = context_bank.read_all_lines_for_word(None, displayed_lines, hide_word=False)
    elif action == 'new_game' or action == 'new_game_vs_bert':
        # Select a random line
        previous_guesses.clear()
        previous_guesses_other.clear()
        lines_to_display = context_bank.select_one_random_line()
    else:
        raise NotImplementedError('Nonsense state!')

    # Similarity helper
    if guesser_config.get('baseurl') is not None:
        for pg in (previous_guesses, previous_guesses_other):
            new_pg, msg = guesser_config['word_similarity_fun'](guesser_config, context_bank, lines_to_display, pg)
            if len(msg) > 0:
                new_pg, _ = dummy_similarity_fun(previous_guesses=pg)  # Use dummy similarity instead
                messages.append(f'{ui_strings["error"]}: {msg}')
            pg[:] = new_pg  # Overwrite list!
        buttons_enabled['new_game_vs_other'] = True
    else:
        new_pg, _ = dummy_similarity_fun(previous_guesses=previous_guesses)  # Use dummy similarity instead
        previous_guesses = new_pg
        buttons_enabled['new_game_vs_other'] = False

    return messages, lines_to_display, buttons_enabled, previous_guesses, previous_guesses_other, other_guess_state


# Create an app instance for later usage
app = create_app()

if __name__ == '__main__':
    app.run()
