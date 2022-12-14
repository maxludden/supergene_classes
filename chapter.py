# ============================================================================ #
# supergene_classes/chapter.py
# ============================================================================ #


# ============================================================================ #
#   | Imports
# ============================================================================ #
import os
import re
import sys
import types
import csv
from io import StringIO
from pathlib import Path
from typing import Any, Self

from dotenv import load_dotenv
from loguru import logger as log
from maxcolor import gradient, gradient_panel
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from mongoengine import Document, connect
from mongoengine.fields import IntField, ListField, StringField, URLField
from mongoengine.queryset.queryset import QuerySet
from pymongo.errors import ConnectionFailure
from rich.box import ROUNDED
from rich.panel import Panel
from rich.markdown import Markdown
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.pretty import Pretty
from rich.traceback import install as install_rich_traceback
from sh import Command
from ujson import dump, dumps, load, loads

# ============================================================================ #
# Retrieve Loguru Logger

from log import log


# ============================================================================ #
# Monkey patch QuerySet
def no_op(self, x):
    """Monkey patch QuerySet to allow for type hinting"""
    return self
QuerySet.__class_getitem__ = types.MethodType(no_op, QuerySet)
# End of QuerySet Monkey patch


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
??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
???                        Chapter                         ???
??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
"""
class ChapterNotFound(Exception):
    """A custom exception to raise when the queried chapter does not exist."""
    pass

@log.catch
def _create_subdir(
    parent: Path | str = CWD/'books', 
    subdir: str = 'text', 
    mode: int = 0o755, 
    parents: bool = True, 
    exist_ok: bool = True) -> bool:
    """Helper function to generate sub-directories for different file formats. Valid formats are:
    - csv
    - html
    - json
    - md
    - text


    Args:
        parent (`Path`, `optional`): The parent directory. Defaults to `CWD/'books'`.
        subdir (`str`, `optional`): The name of the sub-directory. Defaults to 'text'.
        mode (`int`, `optional`): The permissions granted to the new directory. Defaults to `0o755`.
        parents (`bool`, `optional`): Generate the sub-directories parent directories if they do not exist. Defaults to True.
        exist_ok (`bool`, `optional`): Whether to ignore a sub-directory when it already exists or throw an error. Defaults to True (ignore existing directory).

    Raises:
        FileNotFoundError: Parent directory not found.
        OSError: Unable to create sub-directory.
    """
    log.debug(f"Sub-directory does not exist: {str(subdir)}")

    # Ensure that parent directory is pathlib `Path`
    if not isinstance(parent, Path):
        parent = Path(parent)

    # Validate parent directory exists
    if not parent.exists():
        error_msg = f"Error creating sub-directory: {str(subdir)}"
        error_cause = f"Error: Parent directory does not exist: {str(parent)}"
        log.error(f"{error_msg}\n\n{error_msg}")
        raise FileNotFoundError(f"{error_msg}\n\n{error_msg}")
    
    # Validate sub-directory
    SUB_DIR = parent / subdir

    # Attempt to create the missing sub-directory
    if not SUB_DIR.exists():
        sub_dir_warning = f"Sub-directory does not exist: {str(subdir)}."
        sub_dir_create = f"Creating sub-directory..."
        log.warning(f"{sub_dir_warning}\n\n{sub_dir_create}")
        try:
            SUB_DIR.mkdir(mode=0o775, parents=parents, exist_ok=exist_ok)
            log.success(
                gradient_panel(
                    f"Created sub-directory: {str(subdir)}.",
                    title=f"Created Sub-Directory!",
                    justify_text='center',
                    expand=True,
                    width=80,
                ),
                justify='center'
            )
        except OSError as ose:
            msg = f"Unable to create sub-directory {str(subdir)}"
            log.error(msg)
            raise ose(msg)

    if SUB_DIR.exists():
        return True
    else:
        return False

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


    def __init__(self, book: int, chapter: int, cvs_path:str, 
    filename: str, html:str, html_path: str, json_path: str, 
    md: str, md_path: str, section: int, tags: list[str], 
    text: str, text_path: str, title: str, unparsed_text: str, url: str) -> Self:
        """Un-parameterized constructor for the Chapter class."""
        super().__init__(book=book, chapter=chapter, cvs_path=cvs_path, 
        filename=filename, html=html, html_path=html_path, json_path=json_path, 
        md=md, md_path=md_path, section=section, tags=tags, 
        text=text, text_path=text_path, title=title, unparsed_text=unparsed_text, url=url)



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
        chapter_dict = {
            "book": self.book,
            "chapter": self.chapter,
            "csv_path": self.csv_path,
            "filename": self.filename,
            "html": self.html,
            "html_path": self.html_path,
            "json_path": self.json_path,
            "md": self.md,
            "md_path": self.md_path,
            "section": self.section,
            "tags": self.tags,
            "text": self.text,
            "text_path": self.text_path,
            "title": self.title,
            "unparsed_text": self.unparsed_text,
            "url": self.url
        }
        return dumps(chapter_dict, sort_keys=True, indent=4)


    def __csv__(self) -> str:
        """Export the given chapter to a Comma Separated Values (`CSV`) file.

        Returns:
            csv (`str`): The given chapter as a CSV formatted string.
        """
        chapter_dict = dict(loads(self.json()))
        with open (self.csv_path, 'w') as csv_file:
            writer = csv.Dict


    def __getattribute__(self, __name: str) -> Any:
        return super().__getattribute__(__name)


    def _generate_filename(self):
        """Generate the filename of the given chapter.

        Raises:
            Exception: Invalid value for `self.chapter`, unable to generate filename.
        """
        if not self.chapter:
            raise Exception(f"Unable to genereate filename for {self.json()}")
        else:
            chapter_zfill = str(self.chapter).zfill(4)
            self.filename = f"chapter-{chapter_zfill}"
            self.save()


    def _generate_path(self, path_type: str = "text", path_as_string: bool = True) -> str | Path:
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
        if not self.filename:
            msg = f"Chapter {self.chapter} does have a filename. Generating filename for Chapter {self.chapter}..."
            log.warning(msg)
        filename = self.filename
        book = int(self.book)
        book_zfill = f"book{str(book).zfill(2)}"
        
        # Current Working Directory
        CWD = Path.cwd()

        # supergene_classes/books directory
        BOOKS_DIR = CWD / 'books'
        if not BOOKS_DIR.exists():

            # Create directory if it does not exist
            _create_subdir(BOOKS_DIR, 'books')

        # supergene_classes/books/book** directory
        BOOK_DIR = BOOKS_DIR / book_zfill
        if not BOOK_DIR.exists():

            # Create directory if it does not exist
            _create_subdir(BOOKS_DIR, book_zfill)

        log.debug(f"Valid parent directory: True\nValid sub-directory: True\n\nAble to generate filepath.")

        # create book subdirectory if it does not exist
        match path_type:
            case 'csv':
                CSV_DIR = BOOK_DIR / 'csv'

                # Create the CSV Directory if it does not exist
                if not CSV_DIR.exists():
                    _create_subdir(BOOK_DIR, 'csv')

                # Generate CSV filepath
                path = CSV_DIR / f"{filename}.csv"

                if not path_as_string:
                    # Return path as `str`
                    return path
                else:
                    # Return path as `Path`
                    return str(path)

            case 'html':
                HTML_DIR = BOOK_DIR / 'html'

                # Create the HTML Directory if it does not exist
                if not HTML_DIR.exists():
                    _create_subdir(BOOK_DIR, 'html')
                
                # Generate HTML filepath
                path = HTML_DIR / f"{filename}.html"

                if not path_as_string:
                    # Return path as a `Path`
                    return path
                else:
                    # Return path as a `str`
                    return str(path)

            case 'json':
                JSON_DIR = BOOK_DIR / 'json'

                # Create the JSON directory if it does not exist
                if not JSON_DIR.exists():
                    _create_subdir(BOOK_DIR, 'json')

                # Generate JSON filepath
                path = JSON_DIR / f"{filename}.json"

                if not path_as_string:
                    # Return path as a `Path`
                    return path
                else:
                    # Return path as a `str`
                    return str(path)

            case 'md':
                MD_DIR = BOOK_DIR / 'md'

                # Generate MD Directory if it does not exist
                if not MD_DIR.exists():
                    _create_subdir(BOOK_DIR, 'md')

                # Generate MD filepath
                path = MD_DIR / f"{filename}.md"

                if not path_as_string:
                    # Return path as a `Path`
                    return path
                else:
                    # Return path as a `str`
                    return str(path)

            case 'text':
                TEXT_DIR = BOOK_DIR / 'text'
                
                # Create text directory if it does not exist
                if not TEXT_DIR.exists():
                    _create_subdir(BOOK_DIR, 'text')

                # Generate Text filepath
                path = TEXT_DIR / f"{filename}.txt"

                if not path_as_string:
                    # Return path as a `Path`
                    return path
                else:
                    # Return path as a `str`
                    return str(path)

            case _:
                # Default case for invalid types
                msg = f"Invalid file format: {path_type}"
                log.error(msg)
                raise OSError(f"OSError: {msg}")

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


def generate_paths(chapter: int, path_type: str | None = None) -> None:

    """Update the paths for each chapter.
    Args:
        chapter (`int`)": The given chapter.
    """
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    chapter_zfill = str(doc.chapter).zfill(4)
    if not doc.filename:
        doc.filename = f"chapter-{chapter_zfill}"
        doc.save()
        log.debug(f"Updated Chapter {chapter}'s filename: {doc.filename}")
    
