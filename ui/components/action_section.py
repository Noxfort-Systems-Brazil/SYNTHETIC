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
# File: ui/components/action_section.py
# Author: Gabriel Moraes
# Date: 2026-08-16

from tkinter import ttk
from typing import Callable, Optional

from ui.interfaces import ITranslator


class ActionSection(ttk.Frame):
    """
    Visual component managing the primary execution button and its interactive states.
    """

    def __init__(self, parent: ttk.Frame, on_start_generation: Callable[[], None]) -> None:
        super().__init__(parent)
        self.pack(fill="x", expand=True, ipady=10, pady=10)

        self.on_start_generation = on_start_generation

        self.action_button = ttk.Button(self, command=self.on_start_generation)
        self.action_button.pack(fill="x", expand=True)

    def set_action_state(
        self, state: str, text_key: Optional[str] = None, translator: Optional[ITranslator] = None
    ) -> None:
        """Configures the button state ('normal', 'disabled') and optional translated text."""
        self.action_button.config(state=state)
        if text_key and translator:
            self.action_button.config(text=translator.t(text_key))

    def update_ui_texts(self, translator: ITranslator) -> None:
        """Updates the button label if enabled."""
        if str(self.action_button.cget("state")) != "disabled":
            self.action_button.config(text=translator.t("btn_generate"))
