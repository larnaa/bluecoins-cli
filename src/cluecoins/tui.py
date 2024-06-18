from dataclasses import dataclass
import functools
import sqlite3 as lite
import sys
from functools import partial
from typing import Any

from pytermgui.file_loaders import YamlLoader
from pytermgui.widgets import Label
from pytermgui.widgets.button import Button
from pytermgui.widgets.containers import Container
from pytermgui.widgets.input_field import InputField
from pytermgui.window_manager.manager import WindowManager
from pytermgui.window_manager.window import Window
import survey

import cluecoins.cli as cli
from cluecoins.database import get_accounts_list
from cluecoins.database import get_archived_accounts
from cluecoins.sync_manager import SyncManager


import os


@dataclass
class Context:
    db_path: str | None = None


def clear_screen(fn: Any) -> Any:

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        command = 'cls' if os.name == 'nt' else 'clear'
        os.system(command)
        return fn(*args, **kwargs)

    return wrapper

@clear_screen
def convert_menu(ctx):
    question = "Convert menu. Enter the base currency:"
    base_currency = survey.routines.input(question)

    cli._convert(base_currency, ctx.db_path)


@clear_screen
def main_menu(ctx):
    question = "Main menu. Choose an option:"
    options = (
        "Convert",
        "Archive",
        "Unarchive",
        "Exit",
    )

    action = survey.routines.select(question, options=options, index=0)

    if action == 0:
        convert_menu(ctx)


def close_session(sync: SyncManager) -> None:
    if sync.device is not None:
        # FIXME: hardcode
        sync.push_changes_to_app('.ui.activities.main.MainActivity')


def run_tui(db_path: str | None) -> None:

    sync = SyncManager()

    def get_db() -> str:
        if not db_path:
            return sync.prepare_local_db()
        return db_path

    def create_currency_window(manager: WindowManager) -> Window:
        '''Create the window to choose a currency and start convert.'''

        window = Window()

        def _start(base_currency: str) -> None:
            tmp_window = Window().center() + Label('Please wait...')
            manager.add(tmp_window)
            start_convert(base_currency)
            manager.remove(tmp_window)

        currency_field = InputField(prompt='Currency: ', value='USD')
        currency_window = (
            window
            + ""
            + currency_field
            + ""
            + Button('Convert', lambda *_: _start(currency_field.value))
            + ""
            + Button('Back', lambda *_: manager.remove(window))
        ).center()

        return currency_window

    def create_account_archive_window(manager: WindowManager) -> Window:
        """Create the window to choose an account by name and start archive.

        Create an accounts info table.
        """

        con = lite.connect(get_db())

        accounts_table = Container()

        for account in get_accounts_list(con):
            account_name = account[0]
            acc = Button(
                account_name,
                partial(start_archive_account, account_name=account_name),
            )
            accounts_table += acc

        window = Window(box="HEAVY")

        archive_window = (
            window + "" + accounts_table + "" + Button('Back', lambda *_: manager.remove(window))
        ).center()

        return archive_window

    def create_account_unarchive_window(manager: WindowManager) -> Window:
        """Create the window to choose an account by name and start unarchive.

        Create an accounts info table.
        """

        con = lite.connect(get_db())

        unarchive_accounts_table = Container()

        for account in get_archived_accounts(con):
            account_name = account[0]
            acc = Button(
                label=account_name,
                onclick=partial(start_unarchive_account, account_name=account_name),
            )
            unarchive_accounts_table += acc

        window = Window(box="HEAVY")

        unarchive_window = (
            window + "" + unarchive_accounts_table + "" + Button('Back', lambda *_: manager.remove(window))
        ).center()

        return unarchive_window

    def start_convert(base_currency: str) -> None:

        cli._convert(base_currency, get_db())

    def start_archive_account(button: Button, account_name: str) -> None:

        cli._archive(account_name, get_db())

    def start_unarchive_account(button: Button | None, account_name: str) -> None:

        cli._unarchive(account_name, get_db())

    ctx = Context()

    main_menu(ctx)
