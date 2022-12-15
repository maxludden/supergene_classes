import os
import types
import csv
from io import StringIO
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv
from loguru import logger as log
from maxcolor import gradient, gradient_panel
from maxconsole import get_console, get_theme
from maxprogress import get_progress
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
from log import log
from pydantic import BaseModel

# Load Environmental Variables
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
