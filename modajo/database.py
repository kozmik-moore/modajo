from os import PathLike
from os.path import abspath

from flask import current_app
from sqlalchemy import create_engine, or_

from modajo import db
from modajo.models import Journal


# def get_sqlite_engine(path: PathLike | str = 'journals.db'):
#     pathstring = 'sqlite://'
#     if path is not None:
#         pathstring = pathstring + '/' + str(abspath(path))
#     return create_engine(pathstring)

#  TODO add logging for all of these functions
def get_journal(handle: int | str):
    """
    Gets a journal from the database
    :param handle: the name or id of the journal
    :return: a Journal object
    """
    if type(handle) in [str, int]:
        stmt = db.select(Journal).where(or_(Journal.name == handle, Journal.id == handle))
        journal: Journal | None = db.session.scalar(stmt)
        if not journal:
            raise ValueError('No journal found for the given handle.')
        else:
            return journal
    else:
        raise TypeError(f'handle must be of type \'int\' or \'str\', not \'{type(handle)}\'')


def create_journal(name: str, enabled: bool = True, visible: bool = True):
    """
    Creates a journal with the given name, if it doesn't exist
    :param name: the name of the journal
    :param enabled: whether the journal is enabled for editing
    :param visible: whether the journal is visible in all interfaces
    :return: a Journal object
    """
    check = get_journal(name)
    if not check:
        journal = Journal()
        journal.name = name
        journal.enabled = enabled
        journal.visible = visible
        journal.trash = False
        db.session.add(journal)
        db.session.commit()
        return journal
    else:
        raise ValueError(f'A journal with the name \'{name}\' already exists.')


def update_journal(journal: int | str | Journal,
                   name: str = None,
                   enabled: bool = None,
                   visible: bool = None,
                   trash: bool = None):
    """
    Updates the attributes of the given journal
    :param journal: the name or id of the journal, or a Journal object of the journal
    :param name: the new name of the journal
    :param enabled: whether the journal is enabled for editing
    :param visible: whether the journal is visible in all interfaces
    :param trash: whether the journal is in the trash
    :return: a Journal object
    """
    if not isinstance(journal, Journal):
        journal = get_journal(journal)
    if name and not get_journal(name):
        journal.name = name
    elif name:
        raise ValueError(f'A journal with the name \'{name}\' already exists.')
    if enabled is not None:
        journal.enabled = enabled
    if visible is not None:
        journal.visible = visible
    if trash is not None:
        journal.trash = trash

    # TODO change "trash" status of all tags, fields and contents
    current_app.logger.info(f'Deleted the journal named \'{name}\'')


def delete_journal(journal: int | str | Journal):
    """
    Deletes a journal from the database.\n
    THIS IS IRREVERSIBLE.
    :param journal: the journal to be deleted
    """
    if not isinstance(journal, Journal):
        journal = get_journal(journal)
    name = journal.name
    db.session.delete(journal)
    db.session.commit()
    current_app.logger.info(f'Deleted the journal named \'{name}\'')


def edit_journal_settings(**kwargs):
    """"""
    if 'visible' in kwargs:
        pass
    if 'enabled' in kwargs:
        pass
