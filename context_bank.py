from random import randrange, shuffle

from sqlalchemy.orm import declarative_base
from sqlalchemy import func, Table, create_engine


class ContextBank:
    def __init__(self, db_config, db=None, db_fn=None, window_size: int = 11, hide_char: str = '#'):
        if db is None and db_fn is not None:
            db = create_engine(f'sqlite:///{db_fn}')
        elif db is None and db_fn is None and 'database_name' in db_config:
            db = create_engine(f'sqlite:///{db_config["database_name"]}')

        self._db = db
        self._table_obj = Table(db_config['table_name'], declarative_base().metadata, autoload_with=self._db.engine)
        col_objs = {col_obj.key: col_obj for col_obj in self._table_obj.c}
        self._id_obj = col_objs[db_config['id_name']]
        self._left_obj = col_objs[db_config['left_name']]
        self._word_obj = col_objs[db_config['word_name']]
        self._right_obj = col_objs[db_config['right_name']]
        self._freq = col_objs[db_config['freq']]

        self._window_size = window_size
        self._hide_char = hide_char

    # TODO sentence -> example !
    def read_all_examples_for_word(self, word: str = None, displayed_sents: list = (), hide_word=True):
        """Read all examples for the specific word and separate the ones which were already shown from the new ones"""

        if self._window_size >= 2:
            context_size = (self._window_size - 1) // 2
        else:
            context_size = 1_000_000  # Extremely big to include full sentence

        if hide_word:
            hide_fun = self._hide_word
        else:
            hide_fun = self._identity

        sents_to_display, new_sents = {}, []
        if word is None:
            if len(displayed_sents) > 0:
                word, _ = self.identify_word_from_id(displayed_sents[0])
            else:
                ValueError('At least one displayed example must present to look up the word'
                           ' if word is None in read_all_examples_for_word !')
        displayed_sents_set = set(displayed_sents)

        sents_for_word_query = self._db.session.query(self._table_obj). \
            with_entities(self._id_obj, self._left_obj, self._word_obj, self._right_obj). \
            filter(self._word_obj == word)
        for sent_id, left, word, right in sents_for_word_query.all():
            word = hide_fun(word, self._hide_char)
            # Truncate contexts if needed
            left_truncated = ' '.join(left.split(' ')[-min(context_size, len(left)):])
            right_truncated = ' '.join(right.split(' ')[:min(context_size, len(right))])

            if sent_id in displayed_sents_set:
                sents_to_display[sent_id] = [sent_id, left_truncated, word, right_truncated]
            else:
                new_sents.append([sent_id, left_truncated, word, right_truncated])

        sents_to_display = [sents_to_display[sent_id] for sent_id in displayed_sents]  # In the original order!
        shuffle(new_sents)

        return sents_to_display, new_sents

    def select_one_random_sentence(self):
        """Select one random sentence from all available sentences
            Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows
            Raises sqlalchemy.orm.exc.MultipleResultsFound if multiple rows are returned
        """

        random_sent_id = self._get_random_sent_id()

        # Retrieve data for that specific sentence
        entry_query = self._db.session.query(self._table_obj). \
            with_entities(self._id_obj, self._left_obj, self._word_obj, self._right_obj). \
            filter(self._id_obj == random_sent_id)
        sent_id, left, word, right = entry_query.one()

        return [[sent_id, left, self._hide_word(word), right]]

    def _get_random_sent_id(self):
        """Select a random id (sent_id) from the table"""
        row_count_query = self._db.session.query(func.count(self._id_obj))
        row_count = row_count_query.scalar()
        random_sent_id = randrange(row_count) + 1

        return random_sent_id

    def select_random_word(self):
        """Select one random word from all available sentences
            Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows
            Raises sqlalchemy.orm.exc.MultipleResultsFound if multiple rows are returned
        """

        random_sent_id = self._get_random_sent_id()

        return self.identify_word_from_id(random_sent_id)

    def identify_word_from_id(self, one_sent_id):
        """Identify word from (one of the) the already shown sentence ID
            Raises sqlalchemy.orm.exc.NoResultFound if the query selects no rows
            Raises sqlalchemy.orm.exc.MultipleResultsFound if multiple rows are returned
        """

        word_query = self._db.session.query(self._table_obj). \
            with_entities(self._word_obj, self._freq). \
            filter(self._id_obj == one_sent_id)
        word, freq = word_query.one()

        return word, freq

    @staticmethod
    def _identity(word, _):
        return word

    @staticmethod
    def _hide_word(word: str, hide_char: str = 'X'):
        """Hide word with same amount of hide_char characters to maintain the length"""
        return hide_char * len(word)
