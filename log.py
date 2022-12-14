# supergene_classes/log.py

from functools import wraps
from os import environ
from pathlib import Path
from time import perf_counter
from typing import Tuple
import re

from dotenv import load_dotenv
from loguru import logger as log
from maxcolor import gradient, gradient_panel
from maxconsole import get_console, get_theme
from maxprogress import get_progress
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Column
from rich.text import Text
from ujson import dump, load

load_dotenv()
console = get_console(get_theme())
progress = get_progress(console)

BASE = Path.cwd()
LOGS_DIR = BASE / "logs"
RUN_FILE = LOGS_DIR / "run.txt"


def validate_paths() -> None:
    """
    Validate that the necessary directories exist.
    """

    class DirectoryNotFound(Exception):
        pass

    class FileNotFound(Exception):
        pass

    if not LOGS_DIR.exists():
        raise DirectoryNotFound(f"LOG Directory: {LOGS_DIR} - does not exist.")
    if not RUN_FILE.exists():
        raise FileNotFound(f"Run Dictionary: {RUN_FILE} - does not exist.")


# > Current Run
def get_last_run() -> int:
    """
    Get the last run of the script.
    """
    with open(RUN_FILE, "r") as infile:
        last_run_str = infile.read()
        last_run = int(last_run_str)
    return last_run


def increment_run(last_run: int) -> int:
    """
    Increment the last run of the script.
    """
    run = last_run + 1
    return run


def record_run(run: int) -> None:
    """
    Record the last run of the script.
    """
    with open(RUN_FILE, "w") as outfile:
        outfile.write(str(run))


def new_run() -> int:
    """
    Create a new run of the script.
    """
    # > RUN
    last_run = get_last_run()
    run = increment_run(last_run)
    record_run(run)

    # > Clear and initialize console
    console.clear()
    RUN = gradient(f"Run {run}", 3)
    console.rule(title=RUN, style="bold bright_white")
    return run


current_run = new_run()


def filename_log_patcher(record: dict) -> dict:
    """Patch the filename of every record to ensure that filenames generated by vscode fit in log format.

    Args:
        record (`dict`): The record dict of a logged message.

    Returns:
        record (`dict`): The patched record dict or a logged message with a formatted filename.
    """
    input_filename = record["file"].name
    ipython_regex = r"\<ipython\-input\-.*?\>"
    if re.match(ipython_regex, input_filename, re.I) != None:
        filename = "iPython"
    else:
        filename = input_filename
    record["extra"]["filename"] = filename
    return record


# > Configure Loguru Logger Sinks
sinks = log.configure(
    handlers=[
        dict(  # . debug.log
            sink=f"{BASE}/logs/verbose.log",
            level="DEBUG",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: <8} -> {message}",
            mode="w",
        ),
        dict(  # . info.log
            sink=f"{BASE}/logs/info.log",
            level="INFO",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: <8} -> {message}",
            mode="w",
        ),
        dict(  # . Rich Console Log > INFO
            sink=(
                lambda msg: console.log(
                    msg, markup=True, highlight=True, log_locals=False
                )
            ),
            level="INFO",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: ^8} -> [info]{message}[/info]",
            diagnose=True,
            catch=True,
            backtrace=True,
        ),
        dict(
            sink=(
                lambda msg: console.log(
                    msg, markup=True, highlight=True, log_locals=False
                )
            ),
            level="SUCCESS",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: ^8} -> [success]{message}[/success]",
        ),
        dict(  # Rich Console Log > WARNING
            sink=(
                lambda msg: console.log(
                    msg, markup=True, highlight=True, log_locals=True
                )
            ),
            level="WARNING",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: ^8} -> [warning]{message}[/warning]",
            backtrace=True,
        ),
        dict(  # . Rich Console Log > ERROR
            sink=(
                lambda msg: console.log(
                    msg, markup=True, highlight=True, log_locals=True
                )
            ),
            level="ERROR",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: ^8} -> [error]{message}[/error]",
            diagnose=True,
            catch=True,
            backtrace=True,
        ),
        dict(  # . Rich Console Log > Critical
            sink=(
                lambda msg: console.log(
                    msg, markup=True, highlight=True, log_locals=True
                )
            ),
            level="CRITICAL",
            format="Run {extra[run]} | {time:hh:mm:ss:SSS A} | {extra[filename]: ^13} |  Line {line: ^5} | {level: ^8} -> [bold #ffffff on #5e0000]{message}[/]",
            diagnose=True,
            catch=True,
            backtrace=True,
        ),
    ],
    patcher=filename_log_patcher,
    extra={
        "run": current_run,  # > Current Run
    },
)
log.debug("Initialized Logger")
# End of handlers

# > Decorators
@log.catch
def check(*, entry=True, exit=True, level="DEBUG"):
    """Create a decorator that can be used to record the entry, `*args`, `**kwargs`, as well ass the exit and results of a decorated function.

    Args:
        entry (`bool`):
            Should the entry, `*args`, and `**kwargs` of given decorated function be logged? Optional argument, defaults to `True`.

        exit (`bool`):
            Should the exit and the result of given decorated function be logged? Optional argument, defaults to `True`.

        level (`str`):
            The level at which to log to be recorded. Optional argument, defaults to `DEBUG`.
    """

    def wrapper(func):
        name = func.__name__
        log.debug(f"Entered function `{name}`.")

        @wraps(func)
        def wrapped(*args, **kwargs):
            check_log = log.opt(depth=1)
            if entry:
                check_log.log(
                    level,
                    f"Entering '{name}'\n<code>\nargs:\n{args}'\nkwargs={kwargs}</code>",
                )
            result = func(*args, **kwargs)
            if exit:
                check_log.log(
                    level, f"Exiting '{name}'<code>\nresult:\n<{result}</code>"
                )
            return result

        return wrapped

    return wrapper


def time(*, level="DEBUG"):
    """Create a decorator that can be used to record the entry and exit of a decorated function.
    Args:
        level (str, optional):
            The level at which to log to be recorded.. Defaults to "DEBUG".
    """

    def wrapper(func):
        name = func.__name__
        log.debug(f"Timing function {name}.")

        @wraps(func)
        def wrapped(*args, **kwargs):
            time_log = log.opt(depth=1)
            start = perf_counter()
            result = func(*args, **kwargs)
            end = perf_counter()
            time_log.log(level, f"{name} took {end - start} seconds.")
            return result

        return wrapped

    return wrapper
