from os import PathLike
from os.path import abspath

from sqlalchemy import create_engine


def get_sqlite_engine(path: PathLike | str = 'journals.db'):
    pathstring = 'sqlite://'
    if path is not None:
        pathstring = pathstring + '/' + str(abspath(path))
    return create_engine(pathstring)


def add_journal():
    """"""


def remove_journal():
    """"""


def edit_journal_settings(**kwargs):
    """"""
    if 'visible' in kwargs:
        pass
    if 'enabled' in kwargs:
        pass
