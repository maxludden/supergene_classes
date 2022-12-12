# supergene_classes/chapter.py
## Imports
import os
import re
import sys
import types
import csv
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from loguru import logger as log
from maxcolor import gradient, gradient_panel
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from mongoengine import Document, connect
from mongoengine.fields import IntField, ListField, StringField, URLField
from mongoengine.queryset.queryset import QuerySet
from pymongo.errors import ConnectionFailure, ConnectionError
from rich.box import ROUNDED
from rich.panel import Panel
from rich.markdown import Markdown
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.traceback import install as install_rich_traceback
from sh import Command
from ujson import dump, dumps, load, loads

from log import log

# Monkey patch QuerySet to allow for type hinting
def no_op(self, x):
    return self


QuerySet.__class_getitem__ = types.MethodType(no_op, QuerySet)


## Load environmental variable from .env
load_dotenv()


# Register Connections
SUPERGENE_URI = os.environ.get("SUPERGENE")
LOCALDB_URI = os.environ.get("LOCALDB")
CWD = Path.cwd()


## setup rich console & progress
console = get_console(get_theme())
install_rich_traceback(console=console)
progress = get_progress(console)


# Helper function to connect to MongoDB
@log.catch
def sg(database: str = "SUPERGENE") -> None:
    """A helper function to connect to MongoDB.
    Args:
        database(`str`): Which MongoDB Database to connect to.
    """
    match database:
        case "SUPERGENE":
            URI = SUPERGENE_URI
        case "LOCALDB":
            URI = LOCALDB_URI
        case _:
            raise ValueError(f"Invalid database name: {database}")
    log.debug(f"Connecting to MongoDB", database=database)
    try:
        connect(URI)
    except ConnectionError as ce:
        log.error(
            f"Function `sg()` raised a Pymongo `Connection Error` when it attempted to connect to MongoDB: {database}"
        )
        raise ce(
            f"`Connection Error` occurred when attempting to connect to MongoDB: {database}"
        )
    except ConnectionFailure as cf:
        log.error(
            f"Function `sg()` raised a Pymongo `Connection Failure` when it attempted to connect to MongoDB: {database}"
        )
        raise ce(
            f"`Connection Failure` occurred when attempting to connect to MongoDB: {database}"
        )


"""
┌────────────────────────────────────────────────────────┐
│                        Chapter                         │
└────────────────────────────────────────────────────────┘
"""


class ChapterNotFound(Exception):
    """A custom exception to raise when the queried chapter does not exist."""

    pass


class Chapter(Document):
    """A MongoEngine Document class to work with the MongoDB collection `chapter`."""

    book = IntField(min_value=1, max_value=10, required=True)
    chapter = IntField(required=True, unique=True)
    csv_path = StringField()
    filename = StringField()
    html = StringField()
    html_path = StringField()
    json_path = StringField()
    md = StringField()
    md_path = StringField()
    section = IntField()
    tags = ListField(StringField(max_length=50))
    text = StringField()
    text_path = StringField()
    title = StringField(max_length=500, required=True)
    unparsed_text = StringField()
    url = URLField()

    def __rich_repr__(self) -> None:
        """A rich rendered representation of the Chapter."""
        table = Table(
            title=Text(f"Chapter {self.chapter}", style="bold cyan"),
            show_header=True,
            header_style="bold magenta",
            box=ROUNDED,
        )

        table.add_column("Key", style="dim", width=12)
        table.add_column("Value", style="bright")
        table.add_row("Chapter", f"{self.chapter}")
        table.add_row("Section", f"{self.section}")
        table.add_row("Book", f"{self.book}")
        table.add_row("Title", f"{self.title}")
        table.add_row("Filename", f"{self.filename}")
        table.add_row("Text Path", f"{self.text_path}")
        table.add_row("MD Path", f"{self.md_path}")
        table.add_row("HTML Path", f"{self.html_path}")
        repr_md = Markdown(str(self.md))
        console.print(table)
        console.print(repr_md)

    def __int__(self) -> int:
        """Retrieves the given chapter's chapter number.

        Returns:
            chapter (`chapter`): The chapter's number.
        """
        return self.chapter

    def __str__(self) -> str:
        """Returns the text of the given chapter.

        Returns:
            text (`str`): The given chapter's text.
        """
        return self.text

    def __json__(self) -> str:
        """Export the given chapter to a JavaScript Object Notation (`JSON`) string.

        Returns:
            json ('str'): The given chapter as a JSON formatted string.
        """
        return self.to_json()

    def __csv__(self) -> str:
        """Export the given chapter to a Comma Separated Values (`CSV`) file.

        Returns:
            csv (`str`): The given chapter as a CSV formatted string.
        """
        return self.to_csv

    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)

    def _get_path(self, path: str = "text", path_as_string: bool = True) -> str | Path:
        """Generate the filepaths to any of the formats of the chapter:

        - csv
        - html
        - json
        - md
        - text
       
        Args:
            path (`str`, `optional`): Which type of format to find the path of. Defaults to 'file'.
            path_as_string (bool, optional): Whether to return the path as pathlib `Path` or a `str`. Defaults to True, returns a string.

        Returns:
            path = (`str` | `Path`): The retrieve filepath.
        """
        filename = self.filename
        book = int(self.book)
        book_zfill = f"book{str(book).zfill(2)}"
        
        CWD = Path.cwd()
        BOOKS_DIR = CWD / 'books'
        if not BOOKS_DIR.exists():
            log.debug(f"The `books` directory does not exist. Creating `books` directory...")
            try:
                BOOKS_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)
                log.success(f"Created the `books` directory at filepath: {str(BOOKS_DIR)}")
            except:
                log.error(f"Unable to create the books directory.")

        
        BOOK_DIR = BOOKS_DIR / book_zfill
        if not BOOK_DIR.exists()
            BOOK_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)

def chapter_print(chapter: int, mode: str = ("md")) -> None:
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    if doc:
        log.debug(f"Found Chapter {chapter} in MongoDB")
        match mode:
            case "text":
                text = gradient(doc.text)
                console.print(
                    f"\n\n{doc.title}\n\n",
                    justify="center",
                    style=Style(
                        color="#ffffff", bgcolor="#000000", underline=True, bold=True
                    ),
                )
                console.print(
                    f"Chapter {chapter}",
                    justify="center",
                    style=Style(
                        color="#ffffff", bgcolor="#000000", bold=False, italic=True
                    ),
                )
                console.print(text, justify="left")
            case "md":
                chapter_markdown = Markdown(
                    doc.md,
                    justify="left",
                )
                console.print(
                    Panel(
                        renderable=chapter_markdown,
                        title=f"[bold bright_white]\n\n{doc.title}\n\n[/]",
                        title_align="center",
                        subtitle=f"[italic white]\n\nChapter {chapter}\n\n[/]",
                        subtitle_align="center",
                        style=Style(color="#00ff00", bgcolor="#212121", bold=False),
                        border_style="bold bright_white",
                    )
                )



class chapter_gen:
    """
    Generator for chapter numbers.
    """

    def __init__(self, start: int = 1, end: int = 3462):
        self.start = start
        self.end = end
        self.chapter_number = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.chapter_number >= 3462:
            raise StopIteration
        elif self.chapter_number == 3094:
            # Skipping chapter 3095
            # 3094 + 1 + 1 = 3096
            self.chapter_number += 2
            return self.chapter_number
        elif self.chapter_number == 3116:
            # Skipping chapter 3117
            # 3116 + 1 + 1 = 3118
            self.chapter_number += 2
            return self.chapter_number
        else:
            self.chapter_number += 1
            return self.chapter_number

    def __len__(self):
        return self.end - self.start + 1


