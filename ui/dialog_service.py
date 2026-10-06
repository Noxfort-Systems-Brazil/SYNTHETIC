# SYNTHETIC  - An AI-Orchestrated Engine for Multi-Modal Traffic Scenario Synthesis
# Copyright (C) 2026 Noxfort Systems 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SOFTWARE.
#
# File: ui/dialog_service.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from abc import ABC, abstractmethod
from tkinter import filedialog, messagebox
from typing import Any, Callable, Dict, List, Optional

from src.core.map_provider import MapProvider
from ui.map_selector import MapSelectorWindow


class IDialogService(ABC):
    """
    Abstract interface for user interaction dialogs and modal windows.
    Enforces Dependency Inversion Principle (DIP) and enables headless testing.
    """

    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        """Displays an error alert to the user."""
        pass

    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        """Displays an informational alert to the user."""
        pass

    @abstractmethod
    def ask_directory(self, initial_dir: str) -> Optional[str]:
        """Prompts the user to select an output directory."""
        pass

    @abstractmethod
    def ask_map_file(self, title: str) -> Optional[str]:
        """Prompts the user to select a supported map file."""
        pass

    @abstractmethod
    def open_map_selector(
        self,
        parent: Any,
        map_provider: MapProvider,
        num_cameras: int,
        num_loops: int,
        on_complete: Callable[[Optional[List[Dict[str, float]]], Optional[List[Dict[str, float]]]], None],
    ) -> None:
        """Opens the interactive map sensor selection window."""
        pass


class TkDialogService(IDialogService):
    """
    Tkinter implementation of IDialogService using native Tkinter dialogs and MapSelectorWindow.
    """

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    def ask_directory(self, initial_dir: str) -> Optional[str]:
        chosen = filedialog.askdirectory(initialdir=initial_dir)
        return chosen if chosen else None

    def ask_map_file(self, title: str) -> Optional[str]:
        chosen = filedialog.askopenfilename(
            title=title,
            filetypes=[
                (
                    "Supported Maps (*.osm, *.net.xml, *.net.xml.gz)",
                    ("*.osm", "*.net.xml", "*.net.xml.gz", "*.osm.gz", "*.osm.xml", "*.xml", "*.gz"),
                ),
                ("OpenStreetMap (*.osm, *.osm.gz)", ("*.osm", "*.osm.xml", "*.osm.gz")),
                ("SUMO Network (*.net.xml, *.net.xml.gz)", ("*.net.xml", "*.net.xml.gz")),
                ("All files", "*.*"),
            ],
        )
        return chosen if chosen else None

    def open_map_selector(
        self,
        parent: Any,
        map_provider: MapProvider,
        num_cameras: int,
        num_loops: int,
        on_complete: Callable[[Optional[List[Dict[str, float]]], Optional[List[Dict[str, float]]]], None],
    ) -> None:
        MapSelectorWindow(parent, map_provider, num_cameras, num_loops, on_complete)
