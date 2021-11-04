from urllib.parse import urlencode
from json.decoder import JSONDecodeError

from requests import get as requests_get, post as requests_post
from requests.exceptions import ConnectionError


def word_similarity(guesser_settings, context_bank, displayed_lines, previous_guesses):
    new_previous_guesses = []
    if len(displayed_lines) > 0 and len(previous_guesses) > 0:
        word, _ = context_bank.identify_word_from_id(displayed_lines[0][0])
        for prev_guess in previous_guesses:
            params = {'word1': word, 'word2': prev_guess, 'guesser': guesser_settings['similarity']}
            word_sim, msg = request_helper(guesser_settings['baseurl'], 'word_similarity', params, 'word_similarity')
            if len(msg) > 0:
                return [], msg

            if word_sim != '-1.0':  # TODO omit or not omit similarity for unknown words?
                new_previous_guesses.append((prev_guess, word_sim))
            else:
                new_previous_guesses.append((prev_guess, ''))
    
    return new_previous_guesses, ''


def dummy_similarity_fun(_=None, __=None, ___=None, previous_guesses=()):
    return [(prev_guess, '') for prev_guess in previous_guesses], ''


def guess(guesser_settings, input_contexts, word, prev_guesses):
    # Get number of subwords for word
    params = {'guesser': guesser_settings['guesser'], 'word': word}
    no_of_subwords, msg = request_helper(guesser_settings['baseurl'], 'no_of_subwords', params, 'no_of_subwords')
    if len(msg) > 0:
        return [], msg

    contexts = []
    missing_token = ''
    for _, left, missing_token, right in input_contexts:
        contexts.append(f'{left} {missing_token} {right}')

    params = {'guesser': guesser_settings['guesser'],
              'missing_token': missing_token,
              'no_of_subwords': no_of_subwords,
              'contexts[]': contexts,
              'prev_guesses[]': prev_guesses,
              'retry_wrong': guesser_settings['retry_wrong'],
              'top_n': guesser_settings['top_n']
              }

    resp, msg = request_helper(guesser_settings['baseurl'], 'guess', params, 'guesses')
    if len(msg) > 0:
        return [], msg

    if not isinstance(resp, list) or len(resp) == 0:
        return [], 'ValueError: response is not a list or empty!'
    
    return resp, ''


def request_helper(base_url, query, params, out_key):
    # Use POST if query string is too long
    query_str = f'{base_url}/{query}?{urlencode(params, doseq=True)}'
    try:
        if len(query_str) < 2048:
            resp = requests_get(query_str)
        else:
            resp = requests_post(f'{base_url}/{query}', json=params)
    except ConnectionError as err:
        # Try to hide the word to be quessed
        err_str = str(err).split(':')
        err_str[2] = '('.join(err_str[2].split('(')[1:])
        err_str = ':'.join(err_str)
        return None, f'ConnectionError: {err_str}'

    # Handle errors... Raise exceptions...
    if resp.status_code > 200:
        return None, f'Status code: {resp.status_code}'

    try:
        resp_json = resp.json()
    except JSONDecodeError as err:
        return None, f'JSONDecodeError: {err}'

    ret_json = resp_json.get(out_key)
    if ret_json is None:
        return None, f'KeyError: {out_key} missing from JSON!'

    return ret_json, ''
