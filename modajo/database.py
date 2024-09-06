from flask import current_app
from sqlalchemy import or_, and_

from modajo import db
from modajo.models import Journal, Field

RESOLUTIONS = [
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'millisecond',
]

TIME_TYPES = [
    'timestamp',
    'duration'
]

STRING_TYPES = [
    'string',
    'text',
    'tag',
]

NUMBER_TYPES = [
    'integer',
    'float',
]

PRIMITIVE_TYPES = TIME_TYPES + STRING_TYPES + NUMBER_TYPES

COMPOUND_TYPES = [
    'group',
    'session',
    'attachment'
]


FIELDTYPES = PRIMITIVE_TYPES + COMPOUND_TYPES


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
    stmt = db.select(Field)
    if journal is None and isinstance(handle, int):
        stmt = stmt.where(Field.id == handle)
    elif journal is None:
        raise ValueError(f'Field is accessed either by id or a combination of name and journal')
    else:
        if not isinstance(journal, Journal):
            journal = get_journal(journal)
        stmt = stmt.where(and_(Field.fieldname == handle, Field.journal == journal))
    field: Field | None = db.session.scalar(stmt)
    if field:
        return field
    else:
        raise ValueError('No field found')


def search_fields(journal: str | int | Journal,
                  fieldname: str = None,
                  fieldtype: str = None,
                  group: str | int | Field = None,
                  displayname: str = None,
                  visible: bool = None,
                  multiple_allowed: bool = None,
                  trash: bool = None,
                  partial: bool = True):
    """
    Performs basic search for fields with given attribute
    :param journal: the journal to search through
    :param fieldname: the fieldname of the field. Can be a partial match
    :param fieldtype: the type of the field
    :param group: the group the field is part of.
    :param displayname: the displayname of the field. Can be a partial match
    :param visible: whether the field is visible in most interfaces
    :param multiple_allowed: whether the field allows multiple entries per record
    :param trash: whether the field is marked "trash"
    :param partial: whether partial matches are allowed for specific fields
    :return: a list of JournalField
    """
    if not isinstance(journal, Journal):
        journal = get_journal(journal)
    stmt = db.select(Field).where(Field.journal == journal)
    if fieldname is not None and isinstance(fieldname, str):
        if partial:
            stmt = stmt.where(Field.fieldname.ilike(fieldname))
        else:
            stmt = stmt.where(Field.fieldname == fieldname)
    elif fieldname is not None:
        raise ValueError('\'fieldname\' must be of type str')
    if fieldtype is not None and fieldtype in FIELDTYPES:
        stmt = stmt.where(Field.fieldtype.ilike(fieldtype))
    elif fieldtype is not None:
        raise TypeError(f'\'{fieldtype}\' is not an accepted field type')
    if group is not None:
        if not isinstance(group, Field):
            group = get_field(group, journal)
        stmt = stmt.where(Field.group == group)
    if displayname is not None and isinstance(displayname, str):
        if partial:
            stmt = stmt.where(Field.displayname.ilike(displayname))
        else:
            stmt = stmt.where(Field.displayname == displayname)
    elif displayname is not None:
        raise TypeError('\'displayname\' must be of type str')
    for a, v in ('visible', visible), ('multiple_allowed', multiple_allowed), ('trash', trash):
        if v is not None and isinstance(v, bool):
            stmt = stmt.where(getattr(Field, a) == v)
        elif v is not None:
            raise TypeError(f'\'{a}\' must be of type bool')
    return list(db.session.scalars(stmt))


def create_field(journal: str | int | Journal,
                 fieldname: str,
                 fieldtype: str,
                 displayname: str,
                 group: str | int | Field = None,
                 visible: bool = True,
                 multiple_allowed: bool = False,
                 **kwargs
                 ):
    """
    Creates a single field in a journal
    :param journal: the journal that the field is added to
    :param fieldname: the database name of the field
    :param fieldtype: the type of the field
    :param displayname: the interface name of the field
    :param group: if part of multi-field, like "attachment", the group the field belongs to
    :param visible: whether the field is visible in the interface
    :param multiple_allowed: whether this field supports multiple entries per record
    :return: a JournalField object
    """
    if not isinstance(journal, Journal):
        journal = get_journal(journal)
    if get_field(fieldname, journal):
        raise ValueError(f'Fieldname \'{fieldname}\' in journal \'{journal.name}\' already exists')
    stmt = db.select(Field).where(and_(Field.displayname == displayname, Field.journal == journal))
    if db.session.scalar(stmt):
        raise ValueError(f'Displayname \'{displayname}\' in journal \'{journal.name}\' already exists')
    if not isinstance(group, Field):
        group = get_field(group, journal)
    if fieldtype not in FIELDTYPES:
        raise ValueError(f'\'{fieldtype}\' is not an accepted field type')
    elif fieldtype == 'group':
        raise TypeError('Use \'create_group_field\' to create a new group (i.e. "compound") field')
    elif fieldtype == 'session':
        options = dict(journal=journal,
                       fieldname=fieldname,
                       displayname=displayname,
                       visible=visible,
                       multiple_allowed=multiple_allowed)
        if 'start' in kwargs:
            if isinstance(kwargs['start'], str):
                pass

        create_session_field(**options)


def create_group_field(journal,
                       fieldname,
                       fieldtype,
                       displayname,
                       group,
                       visible,
                       multiple_allowed):
    """
    Creates a group (i.e. compound) field in a journal
    :return:
    """


def create_primitive_field(journal: str | int | Journal,
                           fieldname: str,
                           fieldtype: str,
                           displayname: str,
                           group: str | int | Field = None,
                           visible: bool = True,
                           multiple_allowed: bool = False,
                           length: int = None,
                           resolution: str = None):
    """
    Creates a journal field\n
    Fieldtype must be one of PRIMITIVE_TYPES
    :param journal: the journal to add the field to
    :param fieldname: the name of the field as it appears in the database
    :param fieldtype: the type of the field. Must be from PRIMITIVE_TYPES
    :param displayname: the name of the field as it appears in interfaces
    :param group: the group the field will belong to, if any
    :param visible: whether the field is visible in most interfaces
    :param multiple_allowed: whether the field can have multiple entries per record
    :param length: the maximum length of the field (only applies to STRING_TYPES). -1 indicates "unlimited"
    :param resolution: the smallest unit of time measured (only applies to TIME_TYPES)
    :return: a JournalField object
    """
    # Check existence, types and constraints
    if not isinstance(journal, Journal):  # Get  Journal object if not supplied
        journal = get_journal(journal)
    if get_field(fieldname, journal):  # Check if field name exists already
        raise ValueError(f'Fieldname \'{fieldname}\' in journal \'{journal.name}\' already exists')
    if search_fields(journal, displayname=displayname, partial=False):  # Check if displayname already exists
        raise ValueError(f'Displayname \'{displayname}\' in journal \'{journal.name}\' already exists')
    if fieldtype not in PRIMITIVE_TYPES:  # Check fieldtype of primitive kind
        raise ValueError(f'\'{fieldtype}\' is not of type {", ".join([f"\'{x}\'" for x in PRIMITIVE_TYPES])}')
    if group is not None and not isinstance(group, Field): # Get JournalField object, if needed
        group = get_field(group, journal)
    for n, a in dict(visible=visible, multiple_allowed=multiple_allowed).items(): # Check type
        if not isinstance(a, bool):
            raise TypeError(f'\'{n}\' must be of type bool')
    if length is not None:  # Check type and value
        if not isinstance(length, int):
            raise TypeError(f'\'length\' must be if type int')
        if not (length == -1 or length > 0):
            raise ValueError('\'length\' must be equal to -1 ("unlimited") or greater than 0')
    if resolution is not None:  # Check type and value
        if not isinstance(resolution, str):
            raise TypeError(f'\'resolution\' must be if type str')
        if resolution not in RESOLUTIONS:
            raise TypeError(f'\'{resolution}\' is not an accepted time unit resolution')

    # Create field, add to database and return
    field = Field()
    field.journal = journal
    field.fieldname = fieldname
    field.displayname = displayname
    field.fieldtype = fieldtype
    field.group = group
    field.visible = visible
    if fieldtype in TIME_TYPES and not resolution:
        resolution = 'second'
    field.resolution = resolution
    if field in STRING_TYPES and not length:
        length = -1
    field.length = length
    db.session.add(field)
    db.session.commit()
    return field


def create_session_field(journal: str | int | Journal,
                         fieldname: str,
                         displayname: str,
                         group: str | int | Field = None,
                         start: str | dict[str] = 'Start',
                         end: bool = True,
                         duration: bool = True,
                         resolution: str | list[str] | dict[str, str] = 'second',
                         visible: bool = True,
                         multiple_allowed: bool = False):
    """
    Creates a session group field with options. Assumes one session per record.
    :param fieldname:
    :param journal:
    :param displayname:
    :param group:
    :param start:
    :param end:
    :param duration:
    :param resolution:
    :param visible:
    :param multiple_allowed:
    :return: A JournalField object
    """
    if not isinstance(journal, Journal):
        journal = get_journal(journal)
    if get_field(fieldname, journal):
        raise ValueError(f'Fieldname \'{fieldname}\' in journal \'{journal.name}\' already exists')
    stmt = db.select(Field).where(and_(Field.displayname == displayname, Field.journal == journal))
    if db.session.scalar(stmt):
        raise ValueError(f'A field with the displayname {displayname} in journal {journal.name} already exists')
    if group:
        if not isinstance(group, Field):
            group = get_field(group, journal)
    if isinstance(resolution, str):
        if start is True:
            pass
    if end is True:
        pass
    if duration is True:
        pass


def create_attachment_field(fieldname,
                            displayname,
                            group=None,
                            visible=True,
                            multiple_allowed=True):
    """
    Creates an attachment group field. Assumes multiple attachments per record.
    :param fieldname:
    :param displayname:
    :param group:
    :param visible:
    :param multiple_allowed:
    :return:
    """
