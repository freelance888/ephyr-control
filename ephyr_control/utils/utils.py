import string
import random

import yarl

__all__ = ('random_ascii_string', 'generate_random_key_of_length', 'build_rtmp_uri')


def random_ascii_string(length: int, uppercase: bool = True, lowercase: bool = True, digits: bool = True):
    pool = ''
    if uppercase:
        pool += string.ascii_uppercase
    if lowercase:
        pool += string.ascii_lowercase
    if digits:
        pool += string.digits
    return ''.join(random.choices(pool, k=length))


def generate_random_key_of_length(length: int) -> str:
    """ Accounts for Ephyr restrictions of symbols allowed in as "key" param. """
    return random_ascii_string(
        length=length,
        uppercase=False,
    )


def build_rtmp_uri(host: str, path: str, key: str) -> str:
    url_obj = yarl.URL.build(
        scheme='rtmp',
        host=host,
        path=f'/{path}/{key}',
    )
    return str(url_obj)
