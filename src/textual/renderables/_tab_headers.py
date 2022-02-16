from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from textual.renderables.opacity import Opacity


@dataclass
class Tab:
    label: str
    name: str | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.label

    def __str__(self):
        return self.label


class TabHeadersRenderable:
    def __init__(
        self,
        tabs: Iterable[Tab],
        *,
        active_tab_name: str | None = None,
        width: int | None = None,
        tab_padding: int | None = None,
        inactive_tab_opacity: float = 0.5,
    ):
        self.tabs = {tab.name: tab for tab in tabs}
        self.active_tab_name = active_tab_name or next(iter(self.tabs))
        self.width = width
        self.tab_padding = tab_padding
        self.inactive_tab_opacity = inactive_tab_opacity

        self._range_cache: dict[str, tuple[int, int]] = {}

    def get_active_range(self) -> tuple[int, int]:
        return self._range_cache[self.active_tab_name]

    def get_ranges(self):
        return self._range_cache

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        tabs = self.tabs
        tab_values = self.tabs.values()

        if self.tab_padding is None:
            total_len = sum(cell_len(header.label) for header in tab_values)
            free_space = width - total_len
            label_pad = (free_space // len(tabs) + 1) // 2
        else:
            label_pad = self.tab_padding

        pad = Text(" " * label_pad, end="")

        char_index = label_pad
        for tab_index, tab in enumerate(tab_values):
            yield pad
            tab_content = Text(
                tab.label,
                end="",
                style=Style(
                    color="#f0f0f0",
                    bgcolor="#262626",
                    meta={"@click": f"activate_tab('{tab.name}')"},
                ),
            )

            # Cache and move to next label
            len_label = cell_len(tab.label)
            self._range_cache[tab.name] = (char_index, char_index + len_label)
            char_index += len_label + label_pad * 2

            if tab.name == self.active_tab_name:
                yield tab_content
            else:
                dimmed_tab_content = Opacity(
                    tab_content, opacity=self.inactive_tab_opacity
                )
                segments = list(console.render(dimmed_tab_content))
                yield from segments

            yield pad


if __name__ == "__main__":
    console = Console()

    h = TabHeadersRenderable(
        [
            Tab("One"),
            Tab("Two"),
            Tab("Three"),
        ]
    )

    console.print(h)
