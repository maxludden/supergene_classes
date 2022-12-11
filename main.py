import os
from chapter import (
    Chapter,
    chapter_gen
)
from rich.markdown import Markdown
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from log import log
from dotenv import load_dotenv
from mongoengine import connect

load_dotenv()

console = get_console(get_theme())
progress = get_progress(console)

def sg(database: str="SUPERGENE"):
    match database:
        case "SUPERGENE":
            URI = os.environ.get("SUPERGENE")
        case "LOCALDB":
            URI = os.environ.get("LOCALDB")
        case _:
            raise ValueError(f"Invalid database: {database}")
    if URI:
        connect(name=database, host=URI)



chapters = chapter_gen()


def chapter_print(chapter: int) -> None:
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    if doc:
        log.debug(f"Found chapter {chapter} in MongoDB")
        console.print(
            Markdown(doc.md)
        )

chapter_print(4)