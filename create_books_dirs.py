# supergene_classes/tasks/create_books_dirs.py
from pathlib import Path
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from maxcolor import gradient, gradient_panel
from chapter import sg, Chapter
from dotenv import load_dotenv
from log import log

load_dotenv()
console = get_console(get_theme())
progress = get_progress(console)

# Current Working Directory
CWD = Path.cwd()
# console.print(gradient_panel(str(CWD), title="Current Working Directory"), justify='center')

# Books Directory
BOOKS_DIR = CWD / 'books'

# Books
for book, x in enumerate(range(1,11)):
    if x < 10:
        book = f"book{str(book).zfill(2)}"
    elif x == 10:
        book = "book10"

    BOOK_DIR = BOOKS_DIR / book
    BOOK_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)
    
    with progress:
        progress.add_task(description="Creating sub-directories", total=5)
    for dir in ['text', 'md', 'html', 'Styles', 'Images']:
        BOOK_SUBDIR = BOOK_DIR / dir
        try:
            BOOK_SUBDIR.mkdir(mode=0o777, parents=True, exist_ok=True)
            if BOOK_SUBDIR.exists():
                result = True
                log.success(f"Created the {dir} directory in Book {book}!")
        except:
            if not BOOK_SUBDIR.exists():
                log.error(f"Could not create the {dir} directory in Book {book}.")
                raise Exception(f"Could not create the {dir} directory in Book {book}.")
