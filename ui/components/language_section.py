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
# File: ui/components/language_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ui.interfaces import ITranslator


class LanguageSection(ttk.Frame):
    """
    Visual component for language selection.
    Dynamically discovers supported locales from the injected translator service.
    """

    def __init__(
        self,
        parent: ttk.Frame,
        translator: ITranslator,
        on_locale_changed: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self.pack(fill="x", pady=(0, 10))

        self.translator = translator
        self.on_locale_changed = on_locale_changed

        self.lang_map = self.translator.get_supported_locales()
        self.reverse_lang_map = {v: k for k, v in self.lang_map.items()}

        self.lbl_lang = ttk.Label(self, text="")
        self.lbl_lang.pack(side="left", padx=5)

        self.combo_lang = ttk.Combobox(self, values=list(self.lang_map.keys()), state="readonly")
        self.combo_lang.pack(side="left")
        self.combo_lang.bind("<<ComboboxSelected>>", self._on_combo_select)
        self.combo_lang.set(self.reverse_lang_map.get(self.translator.get_locale(), "English"))

    def _on_combo_select(self, event: Optional[tk.Event] = None) -> None:
        selected_display = self.combo_lang.get()
        new_locale = self.lang_map.get(selected_display)
        if new_locale:
            self.on_locale_changed(new_locale)

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates language label."""
        self.lbl_lang.config(text=translator.t("lang_label"))
