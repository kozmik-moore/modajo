from datetime import datetime, timedelta
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modajo import db


class Journal(db.Model):
    __tablename__ = 'journals'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    enabled: Mapped[bool] = mapped_column(nullable=False)
    visible: Mapped[bool] = mapped_column(nullable=False)
    trash: Mapped[bool] = mapped_column(nullable=False)

    fields: Mapped[List['Field']] = relationship(back_populates='journal', cascade='all, delete')
    records: Mapped[List['Record']] = relationship(back_populates='journal', cascade='all, delete')
    integer_content: Mapped[List['IntegerContent']] = relationship(back_populates='journal')
    float_content: Mapped[List['FloatContent']] = relationship(back_populates='journal')
    string_content: Mapped[List['StringContent']] = relationship(back_populates='journal')
    timestamp_content: Mapped[List['TimestampContent']] = relationship(back_populates='journal')
    duration_content: Mapped[List['DurationContent']] = relationship(back_populates='journal')
    session_content: Mapped[List['SessionContent']] = relationship(back_populates='journal')
    attachment_content: Mapped[List['AttachmentContent']] = relationship(back_populates='journal')

    def __repr__(self):
        return f'Journal(name={self.name}, enabled={self.enabled}, visible={self.visible}'


class Field(db.Model):
    __tablename__ = 'fields'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    fieldname: Mapped[str] = mapped_column(nullable=False)
    fieldtype: Mapped[str] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=True)
    displayname: Mapped[str] = mapped_column(nullable=False)
    visible: Mapped[bool] = mapped_column(nullable=False, default=True)
    multiple_allowed: Mapped[bool] = mapped_column(nullable=False, default=False)  # whether multiple records allowed per journal entry
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='fields')
    # TODO address issue where groupfield of type 'meta' is deleted but sub-fields are not (is there an issue?)
    group: Mapped['Field'] = relationship()  # TODO check if this is the correct way to self-reference table
    integer_content: Mapped[List['IntegerContent']] = relationship(back_populates='field')
    float_content: Mapped[List['FloatContent']] = relationship(back_populates='field')
    string_content: Mapped[List['StringContent']] = relationship(back_populates='field')
    timestamp_content: Mapped[List['TimestampContent']] = relationship(back_populates='field')
    duration_content: Mapped[List['DurationContent']] = relationship(back_populates='field')
    session_content: Mapped[List['SessionContent']] = relationship(back_populates='field')
    attachment_content: Mapped[List['AttachmentContent']] = relationship(back_populates='field')

    def __repr__(self):
        return f'Field(name={self.fieldname}, journal={self.journal.name}, type={self.fieldtype}'


class Record(db.Model):
    __tablename__ = 'records'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=True)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='records')
    parent: Mapped['Record'] = relationship(back_populates='children')
    children: Mapped[List['Record']] = relationship(back_populates='parent')
    integer_content: Mapped[List['IntegerContent']] = relationship(back_populates='record')
    float_content: Mapped[List['FloatContent']] = relationship(back_populates='record')
    string_content: Mapped[List['StringContent']] = relationship(back_populates='record')
    timestamp_content: Mapped[List['TimestampContent']] = relationship(back_populates='record')
    duration_content: Mapped[List['DurationContent']] = relationship(back_populates='record')
    session_content: Mapped[List['SessionContent']] = relationship(back_populates='record')
    attachment_content: Mapped[List['AttachmentContent']] = relationship(back_populates='record')

    def __repr__(self):
        return f'Record(id={self.id}, journal={self.journal.name})'


class IntegerContent(db.Model):
    __tablename__ = 'integer_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    content: Mapped[int] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='integer_content')
    field: Mapped['Field'] = relationship(back_populates='integer_content')
    record: Mapped['Record'] = relationship(back_populates='integer_content')

    def __repr__(self):
        return f'IntegerContent(id={self.id}, journal={self.journal.name}, content={self.content})'


class FloatContent(db.Model):
    __tablename__ = 'float_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    content: Mapped[float] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='float_content')
    field: Mapped['Field'] = relationship(back_populates='float_content')
    record: Mapped['Record'] = relationship(back_populates='float_content')

    def __repr__(self):
        return f'FloatContent(id={self.id}, journal={self.journal.name}, content={self.content})'


class StringContent(db.Model):
    __tablename__ = 'string_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    content: Mapped[str] = mapped_column()

    journal: Mapped['Journal'] = relationship(back_populates='string_content')
    field: Mapped['Field'] = relationship(back_populates='string_content')
    record: Mapped['Record'] = relationship(back_populates='string_content')

    def __repr__(self):
        return f'StringContent(id={self.id}, journal={self.journal.name}, content={self.content})'


class TimestampContent(db.Model):
    __tablename__ = 'timestamp_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    content: Mapped[datetime] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='timestamp_content')
    field: Mapped['Field'] = relationship(back_populates='timestamp_content')
    record: Mapped['Record'] = relationship(back_populates='timestamp_content')

    def __repr__(self):
        return f'TimestampContent(id={self.id}, journal={self.journal.name}, content={self.content})'


class DurationContent(db.Model):
    __tablename__ = 'duration_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    content: Mapped[timedelta] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='duration_content')
    field: Mapped['Field'] = relationship(back_populates='duration_content')
    record: Mapped['Record'] = relationship(back_populates='duration_content')

    def __repr__(self):
        return f'DurationContent(id={self.id}, journal={self.journal.name}, content={self.content})'


class SessionContent(db.Model):
    __tablename__ = 'session_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    start: Mapped[datetime] = mapped_column(nullable=True)
    stop: Mapped[datetime] = mapped_column(nullable=True)
    duration: Mapped[timedelta] = mapped_column(nullable=True)

    journal: Mapped['Journal'] = relationship(back_populates='session_content')
    field: Mapped['Field'] = relationship(back_populates='session_content')
    record: Mapped['Record'] = relationship(back_populates='session_content')

    def __repr__(self):
        return f'SessionContent(id={self.id}, journal={self.journal.name})'


class AttachmentContent(db.Model):
    __tablename__ = 'attachment_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    filename: Mapped[int] = mapped_column(nullable=False)
    uuid: Mapped[int] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='attachment_content')
    field: Mapped['Field'] = relationship(back_populates='attachment_content')
    record: Mapped['Record'] = relationship(back_populates='attachment_content')

    def __repr__(self):
        return f'AttachmentContent(id={self.id}, journal={self.journal.name})'
