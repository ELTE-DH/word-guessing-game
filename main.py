#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import os
import sys
from random import choice, randrange

from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy, declarative_base
from yamale import make_schema, make_data, validate, YamaleError
from flask import request, flash, Flask, render_template, current_app

db = SQLAlchemy()


def load_and_validate_config(config_filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                          'config.yaml'),
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

    # Setup Flask application
    flask_app = Flask('word-guessing-game')
    flask_app.config.from_mapping(APP_SETTINGS=config,
                                  SECRET_KEY='any random string',
                                  SQLALCHEMY_DATABASE_URI='sqlite:///{0}'.format(config['database_name']),
                                  SQLALCHEMY_TRACK_MODIFICATIONS=False,
                                  # JSONIFY_PRETTYPRINT_REGULAR=True,
                                  # JSON_AS_ASCII=False,
                                  )
    app_settings = flask_app.config['APP_SETTINGS']

    # Setup SQLAlchemy database for pythonic usage (column obj to name mapping)
    db.init_app(flask_app)
    with flask_app.app_context():
        base = declarative_base(bind=db.engine)
        app_settings['table_obj'] = db.Table(config['table_name'], base.metadata, autoload=True)
        col_objs = {col_obj.key: col_obj for col_obj in config['table_obj'].columns}
        app_settings['id_obj'] = col_objs[config['id_name']]
        app_settings['left_obj'] = col_objs[config['left_name']]
        app_settings['word_obj'] = col_objs[config['word_name']]
        app_settings['right_obj'] = col_objs[config['right_name']]

    @flask_app.route('/')  # So one can create permalink for states!
    # @auth.login_required
    def index():
        """Control the query in a stateless manner"""

        settings = current_app.config['APP_SETTINGS']
        # Parse parameters and put errors into messages if necessary
        messages, next_action, displayed_sent_ids, guessed_word, previous_guesses = parse_params(settings)

        # Execute one step in the game if there were no errors, else do nothing
        messages, displayed_sents, buttons_enabled = game_logic(messages, next_action, displayed_sent_ids, guessed_word,
                                                                previous_guesses, settings)

        # Display messages (errors and informational ones)
        for m in messages:
            flash(m)

        # Render output HTML
        out_content = render_template('layout.html', ui_strings=settings['ui-strings'], buttons_enabled=buttons_enabled,
                                      previous_guesses=previous_guesses, displayed_sents=displayed_sents)
        return out_content

    return flask_app


def parse_params(settings):
    """Parse input parameters (Flask-specific)"""
    messages = []

    previous_guesses = request.args.getlist('previous_guesses[]')

    guessed_word = request.args.get('guessed_word')
    if 'guess' in request.args and guessed_word is None:
        messages.append(settings['ui-strings']['no_guessed_word_specified'])

    displayed_sent_ids = request.args.getlist('displayed_sents[]', int)

    if len({'guess', 'give_up', 'next_sent'}.intersection(request.args.keys())) > 0 and len(displayed_sent_ids) == 0:
        messages.append(settings['ui-strings']['no_displayed_sentences_specified'])

    for action in ('guess', 'next_sent', 'give_up', 'new_game'):
        if action in request.args:
            next_action = action
            break
    else:
        next_action = None

    if len(request.args) > 0 and next_action is None:
        messages.append(settings['ui-strings']['no_action_specified'])

    return messages, next_action, displayed_sent_ids, guessed_word, previous_guesses


def game_logic(messages, action, displayed_sents, guessed_word, previous_guesses, settings):
    """The main logic of the game"""

    hide_word = True
    buttons_enabled = {'guess': True, 'next_sent': True, 'give_up': True, 'new_game': True}

    if len(messages) > 0 or action is None:
        # There were errors
        hide_word = False
        sents_to_display = []
        buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
    elif action == 'guess':
        # Get the word for ID and check it. If matches reveal word in displayed sentences
        word = identify_word_from_id(displayed_sents, settings)
        if word == guessed_word:
            hide_word = False
            messages.append(settings['ui-strings']['win'])
            buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
        else:
            messages.append(settings['ui-strings']['incorrect_guess'])
            previous_guesses.append(guessed_word)

        sents_to_display, _ = read_all_sentences_for_word(displayed_sents, settings)
    elif action == 'next_sent':
        # Read sentences for the word, display already shown and select a new one
        sents_to_display, new_sents = read_all_sentences_for_word(displayed_sents, settings)

        # Select a new sentence to display and insert it to the top
        possible_new_sentids = list(new_sents.keys())
        if len(possible_new_sentids) > 0:
            next_sent = new_sents[choice(list(new_sents.keys()))]
            sents_to_display.insert(0, next_sent)
        else:
            buttons_enabled['next_sent'] = False
            messages.append(settings['ui-strings']['no_more_sent_for_word'])
    elif action == 'give_up':
        # Reveal word in already displayed sentences
        buttons_enabled = {'guess': False, 'next_sent': False, 'give_up': False, 'new_game': True}
        hide_word = False
        sents_to_display, _ = read_all_sentences_for_word(displayed_sents, settings)
    elif action == 'new_game':
        # Select a random sentence
        previous_guesses.clear()
        sents_to_display = select_one_random_sentence(settings)
    else:
        raise NotImplementedError('Nonsense state!')

    # Hide if neccesarry
    if hide_word:
        hide(sents_to_display)

    return messages, sents_to_display, buttons_enabled


def select_one_random_sentence(settings):
    """Select one random sentence from all available sentences
        Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows
        Raises sqlalchemy.orm.exc.MultipleResultsFound if multiple rows are returned
    """

    row_count_query = db.session.query(func.count(settings['id_obj']))
    row_count = row_count_query.scalar()

    random_sent_id = randrange(row_count) + 1

    entry_query = db.session.query(settings['table_obj']). \
        with_entities(settings['id_obj'], settings['left_obj'], settings['word_obj'], settings['right_obj']). \
        filter(settings['id_obj'] == random_sent_id)
    sent_id, left, word, right = entry_query.one()

    return [[sent_id, left, word, right]]


def read_all_sentences_for_word(displayed_sents, settings):
    """Read all sentences for the specific word and separate the ones which were already shown from the new ones"""

    sents_to_display, new_sents = {}, {}
    word = identify_word_from_id(displayed_sents, settings)
    displayed_sents_set = set(displayed_sents)

    sents_for_word_query = db.session.query(settings['table_obj']). \
        with_entities(settings['id_obj'], settings['left_obj'], settings['word_obj'], settings['right_obj']). \
        filter(settings['word_obj'] == word)
    for sent_id, left, word, right in sents_for_word_query.all():
        if sent_id in displayed_sents_set:
            sents_to_display[sent_id] = [sent_id, left, word, right]
        else:
            new_sents[sent_id] = [sent_id, left, word, right]

    sents_to_display = [sents_to_display[sent_id] for sent_id in displayed_sents]  # In the original order!

    return sents_to_display, new_sents


def identify_word_from_id(displayed_sents, settings):
    """Identify word from (one of the) the already shown sentence ID
        Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows
        Raises sqlalchemy.orm.exc.MultipleResultsFound if multiple rows are returned
    """

    one_sent_id = displayed_sents[0]
    word_query = db.session.query(settings['table_obj']). \
        with_entities(settings['word_obj']). \
        filter(settings['id_obj'] == one_sent_id)
    word = word_query.scalar()

    return word


def hide(sents_to_display):
    """Hide word with same amount of X characters to maintain the length"""
    word = sents_to_display[0][2]
    hidden = 'X' * len(word)
    for i, _ in enumerate(sents_to_display):
        sents_to_display[i][2] = hidden


# Create an app instance for later usage
app = create_app()

if __name__ == '__main__':
    app.run()
