from typing import List, Any

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

    fields: Mapped[List['JournalField']] = relationship(back_populates='journal', cascade='all, delete')
    records: Mapped[List['Record']] = relationship(back_populates='journal', cascade='all, delete')
    tags: Mapped[List['Tag']] = relationship(back_populates='journal', cascade='all, delete')
    contents: Mapped[List['FieldContent']] = relationship(back_populates='journal', cascade='all, delete')

    def __repr__(self):
        return f'Journal(name={self.name}, enabled={self.enabled}, visible={self.visible}'


class JournalField(db.Model):
    __tablename__ = 'journal_fields'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    fieldname: Mapped[str] = mapped_column(nullable=False)
    fieldtype: Mapped[str] = mapped_column(nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey('journal_fields.id'), nullable=True)
    displayname: Mapped[str] = mapped_column(nullable=False)
    visible: Mapped[bool] = mapped_column(nullable=False)
    unique: Mapped[bool] = mapped_column(nullable=False)  # whether multiple records allowed per journal entry
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='fields')
    # TODO address issue where groupfield of type 'meta' is deleted but sub-fields are not (is there an issue?)
    group: Mapped['JournalField'] = relationship()
    contents: Mapped['FieldContent'] = relationship(back_populates='field', cascade='all, delete')

    def __repr__(self):
        return f'Journal(name={self.fieldname}, enabled={self.enabled}, visible={self.visible}'


class Record(db.Model):
    __tablename__ = 'records'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='records')
    contents: Mapped[List['FieldContent']] = relationship(back_populates='record')
    # TODO add relationship to association table for 'tags'


class Tag(db.Model):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='tags')
    # TODO add relationship to association table for 'records'

    def __repr__(self):
        return f'Tag(name={self.name}, journal={self.journal.name}'


class FieldContent(db.Model):
    __tablename__ = 'field_contents'

    id: Mapped[int] = mapped_column(primary_key=True)
    journal_id: Mapped[int] = mapped_column(ForeignKey('journals.id'), nullable=False)
    field_id: Mapped[int] = mapped_column(ForeignKey('journal_fields.id'), nullable=False)
    record_id: Mapped[int] = mapped_column(ForeignKey('records.id'), nullable=False)
    parent_id: Mapped[int] = mapped_column(ForeignKey('field_contents.id'), nullable=True)
    contents: Mapped[Any] = mapped_column(nullable=True)
    trash: Mapped[bool] = mapped_column(nullable=False)

    journal: Mapped['Journal'] = relationship(back_populates='contents')
    parent: Mapped['FieldContent'] = relationship(back_populates='children')
    children: Mapped['FieldContent'] = relationship(back_populates='parent')
    field: Mapped['JournalField'] = relationship(back_populates='contents')
    record: Mapped['Record'] = relationship(back_populates='contents')

    def __repr__(self):
        return f'FieldData(id={self.id}, journal={self.journal.name}'
