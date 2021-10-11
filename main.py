#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys


from flask_sqlalchemy import SQLAlchemy
from yamale import make_schema, make_data, validate, YamaleError
from flask import request, flash, Flask, render_template, current_app

from context_bank import ContextBank


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


def create_app(config_filename='config.yaml'):
    """Create and configure the app (and avoid globals as possible)"""

    # Read configuration
    config = load_and_validate_config(config_filename)
    config['ui-strings']['footer'] = config['ui-strings']['footer'].replace(r':\ ', ': ')

    # Setup Flask application
    flask_app = Flask('word-guessing-game')
    flask_app.config.from_mapping(APP_SETTINGS=config,
                                  SECRET_KEY='any random string',
                                  SQLALCHEMY_DATABASE_URI='sqlite:///{0}'.format(config['db-config']['database_name']),
                                  SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                  # JSONIFY_PRETTYPRINT_REGULAR=True,
                                  # JSON_AS_ASCII=False,
                                  )
    app_settings = flask_app.config['APP_SETTINGS']

    # Setup SQLAlchemy database for pythonic usage (column obj to name mapping)
    db = SQLAlchemy()
    db.init_app(flask_app)
    with flask_app.app_context():
        app_settings['context_bank'] = ContextBank(config['db-config'], db)

    @flask_app.route('/')  # So one can create permalink for states!
    # @auth.login_required
    def index():
        """Control the query in a stateless manner"""

        settings = current_app.config['APP_SETTINGS']
        # Parse parameters and put errors into messages if necessary
        messages, next_action, displayed_sent_ids, guessed_word, previous_guesses = parse_params(settings['ui-strings'])

        # Execute one step in the game if there were no errors, else do nothing
        messages, displayed_sents, buttons_enabled = \
            game_logic(messages, next_action, displayed_sent_ids, guessed_word, previous_guesses,
                       settings['ui-strings'], settings['context_bank'])

        # Display messages (errors and informational ones)
        for m in messages:
            flash(m)

        # Render output HTML
        out_content = render_template('layout.html', ui_strings=settings['ui-strings'], buttons_enabled=buttons_enabled,
                                      previous_guesses=previous_guesses, displayed_sents=displayed_sents)
        return out_content

    return flask_app


def parse_params(ui_strings):
    """Parse input parameters (Flask-specific)"""
    messages = []

    previous_guesses = request.args.getlist('previous_guesses[]')

    guessed_word = request.args.get('guessed_word')
    if 'guess' in request.args and guessed_word is None:
        messages.append(ui_strings['no_guessed_word_specified'])

    displayed_sent_ids = request.args.getlist('displayed_sents[]', int)

    if len({'guess', 'give_up', 'next_sent'}.intersection(request.args.keys())) > 0 and len(displayed_sent_ids) == 0:
        messages.append(ui_strings['no_displayed_sentences_specified'])

    for action in ('guess', 'next_sent', 'give_up', 'new_game'):
        if action in request.args:
            next_action = action
            break
    else:
        next_action = None

    if len(request.args) > 0 and next_action is None:
        messages.append(ui_strings['no_action_specified'])

    return messages, next_action, displayed_sent_ids, guessed_word, previous_guesses


def game_logic(messages, action, displayed_sents, guessed_word, previous_guesses, ui_strings, context_bank):
    """The main logic of the game"""

    buttons_enabled = {'guess': True, 'next_sent': True, 'give_up': True, 'new_game': True}

    if len(messages) > 0 or action is None:
        # There were errors
        sents_to_display = []
        buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
    elif action == 'guess':
        # Get the word for ID and check it. If matches reveal word in displayed sentences
        word, _ = context_bank.identify_word_from_id(displayed_sents[0])  # Empty list is handled in parse_params()
        if word == guessed_word:
            hide_word = False
            messages.append(ui_strings['win'])
            buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
        else:
            hide_word = True
            messages.append(ui_strings['incorrect_guess'])
            previous_guesses.append(guessed_word)

        sents_to_display, _ = context_bank.read_all_examples_for_word(word, displayed_sents, hide_word=hide_word)
    elif action == 'next_sent':
        # Read sentences for the word, display already shown and select a new one
        sents_to_display, new_sents = context_bank.read_all_examples_for_word(None, displayed_sents, hide_word=True)

        # Select a new sentence to display and insert it to the top
        if len(new_sents) > 0:
            sents_to_display.insert(0, new_sents[0])
        else:
            buttons_enabled['next_sent'] = False
            messages.append(ui_strings['no_more_sent_for_word'])
    elif action == 'give_up':
        # Reveal word in already displayed sentences
        buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
        sents_to_display, _ = context_bank.read_all_examples_for_word(None, displayed_sents, hide_word=False)
    elif action == 'new_game':
        # Select a random sentence
        previous_guesses.clear()
        sents_to_display = context_bank.select_one_random_sentence()
    else:
        raise NotImplementedError('Nonsense state!')

    return messages, sents_to_display, buttons_enabled


# Create an app instance for later usage
app = create_app()

if __name__ == '__main__':
    app.run()
