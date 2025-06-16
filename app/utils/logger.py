# /app/utils/logger.py
# This file is part of the Zeo++ API server project for logging and console management.
# Author: Shibo Li, logger.py code is from another project of mine.
# Date: 2025-06-16
# Version: 0.2.0

import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track as rich_track
from rich.theme import Theme
from rich.traceback import Traceback

SUCCESS_LEVEL_NUM = 25

if logging.getLevelName(SUCCESS_LEVEL_NUM) == f"Level {SUCCESS_LEVEL_NUM}":
    logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")

def success_log(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

if not hasattr(logging.Logger, 'success'):
    setattr(logging.Logger, 'success', success_log)


class ConsoleManager:
    """
    ConsoleManger is a singleton class that manages a Rich Console instance
    and provides a unified interface for logging and console output.
    Attributes:
        _instance (ConsoleManager): The singleton instance of ConsoleManager.
        _console (Console): The Rich Console instance with custom theme.
        _logger (logging.Logger): The logger instance configured with RichHandler.
        _initialized (bool): Flag to prevent re-initialization.
    Methods:
        __new__(cls, *args, **kwargs): Ensures only one instance of ConsoleManager exists.
        __init__(self): Initializes the Rich Console and logger if not already done.
        _setup_logger(): Configures the logger with RichHandler.
        info(message): Logs an info message.
        success(message): Logs a success message.
        warning(message): Logs a warning message.
        error(message): Logs an error message.
        exception(message): Logs an exception message with traceback.
        rule(title, style): Prints a horizontal rule with a title.
        display_data_as_table(data, title): Displays dictionary data as a formatted table.
        display_error_panel(title, error_message): Displays an error message in a red panel.
        display_traceback(): Displays a formatted traceback panel for exceptions.
        track(*args, **kwargs): Provides a progress bar using Rich's track function.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConsoleManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # initialize only once
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        custom_theme = Theme({
            "logging.level.success": "bold green"
        })
        self._console = Console(theme=custom_theme)
        self._logger = self._setup_logger()
        self._initialized = True

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("zeopp-api")
        
        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.INFO)
        handler = RichHandler(
            console=self._console,
            rich_tracebacks=True,
            tracebacks_show_locals=False, # For debug when deploying.
            keywords=["INFO", "SUCCESS", "WARNING", "ERROR", "DEBUG", "CRITICAL"],
            show_path=False 
        )
        handler.setFormatter(logging.Formatter(fmt="%(message)s", datefmt="[%X]"))
        logger.addHandler(handler)
        return logger


    def info(self, message: str):
        self._logger.info(message)

    def success(self, message: str):
        if self._logger.isEnabledFor(SUCCESS_LEVEL_NUM):
            self._logger._log(SUCCESS_LEVEL_NUM, message, ())

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def exception(self, message: str):
        self._logger.exception(message)

    def rule(self, title: str, style: str = "cyan"):
        """
        A seperate line with rule and title
        Args:
            title (str): The title to display in the rule.
            style (str): The color style for the title. Default is "cyan".
"""
        self._console.rule(f"[bold {style}]{title}[/bold {style}]", style=style)

    def display_data_as_table(self, data: dict, title: str):
        """
        Dictionarize data as a formatted table in a panel.
        Args:
            data (dict): The data to display in the table.
            title (str): The title for the panel.
        """
        table = Table(show_header=True, header_style="bold magenta", box=None, show_edge=False)
        table.add_column("Parameter", style="cyan", no_wrap=True, width=25)
        table.add_column("Value", style="white")

        for key, value in data.items():
            table.add_row(key, str(value))
        
        panel = Panel(table, title=f"[bold green]✓ {title}[/bold green]", border_style="green", expand=False)
        self._console.print(panel)

    def display_error_panel(self, title: str, error_message: str):
        panel = Panel(error_message, title=f"[bold red]✗ {title}[/bold red]", border_style="red", expand=False)
        self._console.print(panel)

    def display_traceback(self):
        self._console.print(Traceback(show_locals=True))

    def track(self, *args, **kwargs):
        return rich_track(*args, console=self._console, **kwargs)


logger = ConsoleManager()
