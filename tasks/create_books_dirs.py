# supergene_classes/tasks/create_books_dirs.py
from pathlib import Path
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from maxcolor import gradient, gradient_panel
from supergene_classes.log import log
from supergene_classes.chapter import sg, Chapter
from dotenv import load_dotenv

load_dotenv()
console = get_console(get_theme())
progress = get_progress(console)

CWD = Path.cwd()
console.print(
    gradient_panel(
        CWD,
        title="Current Working Directory"
    )
)

