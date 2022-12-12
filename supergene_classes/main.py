# supergene_classes/main.py
import os
from chapter import Chapter, chapter_gen
from rich.markdown import Markdown
from rich.style import Style
from rich.panel import Panel
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from maxcolor import gradient, gradient_panel
from log import log
from dotenv import load_dotenv
from mongoengine import connect

load_dotenv()

console = get_console(get_theme())
progress = get_progress(console)


def sg(database: str = "SUPERGENE"):
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


chapter_print(4, "text")
