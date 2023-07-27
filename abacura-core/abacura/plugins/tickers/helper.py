from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from rich.table import Table

from abacura.plugins import Plugin, command, CommandError

if TYPE_CHECKING:
    pass


class TickerCommand(Plugin):

    def show_tickers(self):
        tbl = Table(title="All tickers")
        tbl.add_column("Name")
        tbl.add_column("Callback")
        tbl.add_column("Source")
        tbl.add_column("Repeats", justify="right")
        tbl.add_column("Seconds", justify="right")
        tbl.add_column("Next Tick")

        for ticker in self.director.ticker_manager.tickers:
            callback_name = getattr(ticker.callback, "__qualname__", str(ticker.callback))
            source = ticker.source.__class__.__name__ if ticker.source else ""
            if isinstance(ticker.source, TickerCommand):
                callback_name = f"'{ticker.commands}'"

            tbl.add_row(ticker.name, callback_name, source,
                        str(ticker.repeats), format(ticker.seconds, "7.3f"), str(ticker.next_tick))

        self.output(tbl)

    @command
    def ticker(self, name: str = '', commands: str = '', seconds: float = 0, repeats: int = -1, delete: bool = False):
        """
        View/Create/delete tickers

        :param name: Name of the ticker
        :param commands: Commands to issue each tick (separated by ;)
        :param seconds: How often to repeat the ticker
        :param repeats: How many times to repeat the ticker
        :param delete: Delete a ticker by name
        """

        if delete:
            if not name:
                raise CommandError("Must specify ticker name")
            self.remove_ticker(name)
            return

        if not name:
            self.show_tickers()
            return

        if not commands:
            raise CommandError("Must specify a message")

        if seconds <= 0:
            raise CommandError("Seconds must be more than 0")

        # always remove an existing ticker with this name
        self.remove_ticker(name)

        def ticker_callback():
            for cmd in commands.split(";"):
                self.session.player_input(cmd, echo_color="orange1")

        self.add_ticker(seconds=seconds, callback_fn=ticker_callback, repeats=repeats, name=name, commands=commands)



