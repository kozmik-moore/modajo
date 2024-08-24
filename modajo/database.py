from flask import current_app
from sqlalchemy import or_, and_

from modajo import db
from modajo.models import Journal, JournalField


FIELDTYPES = {
    'integer': {},
    'float': {},
    'string': {'length': -1},
    'text': {'length': -1},  # Like 'string' but allows spaces
    'tag': {'length': -1, 'multiple_allowed': 'true'},  # Like 'string' but allows spaces
    'timestamp': {'resolution': 'second'},
    'duration': {'resolution': 'second'},
    'session': {
        'start': {'type': 'timestamp'},
        'end': {'type': 'timestamp'},
        'duration': {'type': 'duration'},
    },
    'attachment': {
        'filename': {'type': 'string', 'length': -1},
        'uuid': {'type': 'string', 'visible': 'false'}
    }
}


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


def search_journals(name: str = None,
                    enabled: bool = None,
                    visible: bool = None,
                    trash: bool = None):
    """
    Searches for journals with the given attributes. Supports partial matching
    :param name: the name of the journal (can be a partial match)
    :param enabled: whether the journal is enabled for editing
    :param visible: whether the journal is visible in all interfaces
    :param trash: whether the journal is in the trash
    :return: a list of Journal objects
    """
    stmt = db.select(Journal)
    if name is not None:
        stmt = stmt.where(Journal.name.ilike(f'%{name}%'))
    if enabled is not None:
        stmt = stmt.where(Journal.enabled == enabled)
    if visible is not None:
        stmt = stmt.where(Journal.visible == enabled)
    if trash is not None:
        stmt = stmt.where(Journal.trash == trash)
    results: list[Journal] = list(db.session.scalars(stmt))
    return results


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


def get_field(handle: str | int, journal: str | int | Journal = None):
    """
    Gets a field from a specific journal
    :param handle: the name or id of the field
    :param journal: the journal the field is part of (optional if field id is supplied)
    :return: a JournalField object
    """
    stmt = db.select(JournalField)
    if journal is None and isinstance(handle, int):
        stmt = stmt.where(JournalField.id == handle)
    elif journal is None:
        raise ValueError(f'Field is accessed either by id or a combination of name and journal')
    else:
        if not isinstance(journal, Journal):
            journal = get_journal(journal)
        stmt = stmt.where(and_(JournalField.name == handle, JournalField.journal == journal))
    field: JournalField | None = db.session.scalar(stmt)
    if field:
        return field
    else:
        raise ValueError('No field found')


def create_field(journal: str | int | Journal,
                 fieldname: str,
                 fieldtype: str,
                 displayname: str,
                 group: str | int | JournalField = None,
                 visible: bool = True,
                 multiple_allowed: bool = False,
                 ):
    """
    Creates a field in a journal
    :param journal: the journal that the field is added to
    :param fieldname: the database name of the field
    :param fieldtype: the type of the field
    :param displayname: the interface name of the field
    :param group: if part of multi-field, like "attachment", the group the field belongs to
    :param visible: whether the field is visible in the interface
    :param multiple_allowed: whether this field supports multiple entries per record
    :return: a JournalField object
    """


def create_session_field(fieldname,
                         displayname,
                         group = None,
                         start = True,
                         end = True,
                         duration = True,
                         visible = True,
                         multiple_allowed = False):
    """
    Creates a session group field with options. Assumes one session per record.
    :param fieldname:
    :param displayname:
    :param group:
    :param start:
    :param end:
    :param duration:
    :param visible:
    :param multiple_allowed:
    :return:
    """


def create_attachment_field(fieldname,
                            displayname,
                            group = None,
                            visible = True,
                            multiple_allowed = True):
    """
    Creates an attachment group field. Assumes multiple attachments per record.
    :param fieldname:
    :param displayname:
    :param group:
    :param visible:
    :param multiple_allowed:
    :return:
    """
