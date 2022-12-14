# supergene_classes/main.py
import os
import csv
from chapter import Chapter, chapter_gen
from rich.text import Text
from rich.markdown import Markdown
from rich.style import Style
from rich.panel import Panel
from rich.table import Table, Column
from rich.box import ROUNDED
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from maxcolor import gradient, gradient_panel
from log import log
from dotenv import load_dotenv
from mongoengine import connect
from io import StringIO

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




@log.catch
def get_chapter_dict(chapter: int) -> dict:
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    chapter_dict = Chapter(
        book=doc.book,
        chapter=doc.chapter,
        csv_path=doc.csv_path,
        filename=doc.filename,
        html=doc.html,
        html_path=doc.html_path,
        json_path=doc.json_path,
        md=doc.md,
        md_path=doc.md_path,
        section=doc.section,
        tags=doc.tags,
        text=doc.text,
        text_path=doc.text_path,
        title=doc.title,
        unparsed_text=doc.unparsed_text,
        url=doc.url
    )
    return chapter_dict

    
@log.catch
def print_paths(chapter: int=1):
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    
    chapter_doc = Chapter(
        book=doc.book,
        chapter=doc.chapter,
        csv_path=doc.csv_path,
        filename=doc.filename,
        html=doc.html,
        html_path=doc.html_path,
        json_path=doc.json_path,
        md=doc.md,
        md_path=doc.md_path,
        section=doc.section,
        tags=doc.tags,
        text=doc.text,
        text_path=doc.text_path,
        title=doc.title,
        unparsed_text=doc.unparsed_text,
        url=doc.url
    )
    if chapter_doc:
        table = Table(
            header_style="bold #ffffff on #7f008b", 
            style="#f200ff",
            border_style="dim white", 
            show_header=True, 
            show_edge=True, 
            show_lines=True,
            row_styles=['bright', 'dim']
        )

        table.add_column(
            f"Type of Filepath", 
            justify='left', 
            ratio=1, 
            style=Style(
                color='#7f008b',
                bgcolor='#000000',
                dim=True, 
                italic=True,
                bold=False
            )
        )
        table.add_column(
            f"Filepath", 
            justify='left', 
            ratio=4, 
            style=Style(
                color='#7f008b',
                bgcolor='#000000',
                bold=False
            )
        )

        csv_path = chapter_doc._generate_path('csv')
        table.add_row("CSV Path", csv_path)

        html_path = chapter_doc._generate_path('html')
        table.add_row("HTML Path", html_path)

        json_path = chapter_doc._generate_path('json')
        table.add_row("JSON Path", json_path)

        md_path = chapter_doc._generate_path('md')
        table.add_row("Markdown Path", md_path)

        text_path = chapter_doc._generate_path('text')
        table.add_row("Text Path", text_path)

    gradient_title = gradient(f"{doc.title}")
    console.print(
        Panel(
            table,
            title=gradient_title,
            expand=False,
            border_style=Style(
                color="white",
                dim = True
            )
        ),
        justify='center'
    )

if __name__ == "__main__":
    chapters = chapter_gen()
    for chapter in chapters:
        chapter_dict = get_chapter_dict(chapter)
        fieldnames = chapter_dict.keys()
        csv_stream = StringIO()
        csv_writer = csv.DictWriter(csv_stream, fieldnames=fieldnames)
