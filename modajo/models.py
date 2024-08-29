from typing import List

from sqlalchemy import ForeignKey, JSON
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
    contents: Mapped[List['Content']] = relationship(back_populates='journal', cascade='all, delete')

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
    metadata: Mapped[JSON] = mapped_column(nullable=True)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='fields')
    # TODO address issue where groupfield of type 'meta' is deleted but sub-fields are not (is there an issue?)
    group: Mapped['Field'] = relationship()  # TODO check if this is the correct way to self-reference table
    contents: Mapped['Content'] = relationship(back_populates='field', cascade='all, delete')

    def __repr__(self):
        return f'Field(name={self.fieldname}, journal={self.journal.name}, type={self.fieldtype}'


# class IntegerField(db.Model):
#     __tablename__ = 'integer_fields'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
#     field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
#     minimum: Mapped[int] = mapped_column(nullable=True)
#     maximum: Mapped[int] = mapped_column(nullable=True)
#     trash: Mapped[bool] = mapped_column(nullable=False)
#
#     field: Mapped['Field'] = relationship(back_populates='integer_field')
#     journal: Mapped['Journal'] = relationship()
#
#     def __repr__(self):
#         return f'IntegerField(field={self.field.fieldname}, journal={self.journal.name})'
#
#
# class FloatField(db.Model):
#     __tablename__ = 'float_fields'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
#     field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
#     minimum: Mapped[float] = mapped_column(nullable=True)
#     maximum: Mapped[float] = mapped_column(nullable=True)
#     round: Mapped[int] = mapped_column(nullable=False, default=3)
#     trash: Mapped[bool] = mapped_column(nullable=False)
#
#     field: Mapped['Field'] = relationship(back_populates='float_field')
#     journal: Mapped['Journal'] = relationship()
#
#     def __repr__(self):
#         return f'FloatField(field={self.field.fieldname}, journal={self.journal.name})'
#
#
# class StringField(db.Model):
#     __tablename__ = 'string_fields'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
#     field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
#     length: Mapped[int] = mapped_column(nullable=True, default=-1)
#     trash: Mapped[bool] = mapped_column(nullable=False)
#
#     field: Mapped['Field'] = relationship(back_populates='string_field')
#     journal: Mapped['Journal'] = relationship()
#
#     def __repr__(self):
#         return f'StringField(field={self.field.fieldname}, journal={self.journal.name})'
#
#
# class TimeField(db.Model):
#     __tablename__ = 'time_fields'
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
#     field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
#     resolution: Mapped[str] = mapped_column(nullable=True, default='second')
#     format: Mapped[str] = mapped_column(nullable=True, default='%Y-%m-%dT%h:%m:%s')
#     displayformat: Mapped[str] = mapped_column(nullable=True, default='%Y-%m-%d %h:%m:%s')
#     trash: Mapped[bool] = mapped_column(nullable=False)
#
#     field: Mapped['Field'] = relationship(back_populates='time_field')
#     journal: Mapped['Journal'] = relationship()
#
#     def __repr__(self):
#         return f'TimeField(field={self.field.fieldname}, journal={self.journal.name})'


class Record(db.Model):
    __tablename__ = 'records'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='records')
    contents: Mapped[List['Content']] = relationship(back_populates='record')  # TODO add cascade

    def __repr__(self):
        return f'Record(id={self.id}, journal={self.journal.name})'


class Content(db.Model):
    __tablename__ = 'contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey('contents.id'), nullable=True)
    content: Mapped[str] = mapped_column(nullable=True)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='contents')
    parent: Mapped['Content'] = relationship(back_populates='children')
    children: Mapped['Content'] = relationship(back_populates='parent')
    field: Mapped['Field'] = relationship(back_populates='contents')
    record: Mapped['Record'] = relationship(back_populates='contents')

    def __repr__(self):
        return f'Contents(id={self.id}, journal={self.journal.name}'


