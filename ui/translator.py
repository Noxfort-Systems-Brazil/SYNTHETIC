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
# File: ui/translator.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import json
import os
from typing import Any, Dict, Optional

from src.core.logger import logger
from ui.interfaces import ITranslator


class Translator(ITranslator):
    """
    Singleton-like translator to manage UI localization strings.
    Implements ITranslator for Dependency Inversion and Open/Closed compliance.
    """

    _instance: Optional["Translator"] = None

    def __new__(cls) -> "Translator":
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self) -> None:
        self.locale: str = "en"  # default to english
        self.strings: Dict[str, str] = {}
        self._supported_locales: Dict[str, str] = {
            "English": "en",
            "Português (Brasil)": "pt-br",
            "Français": "fr",
            "中文 (简体)": "zh-cn",
            "Русский": "ru",
            "Español": "es",
        }
        self._load_strings()

    def get_supported_locales(self) -> Dict[str, str]:
        """Returns the dictionary mapping display names to locale codes."""
        return dict(self._supported_locales)

    def set_locale(self, locale_code: str) -> None:
        """Sets active locale code if supported."""
        if locale_code in self._supported_locales.values():
            self.locale = locale_code
            self._load_strings()

    def get_locale(self) -> str:
        """Returns the active locale code."""
        return self.locale

    def _load_strings(self) -> None:
        base_dir: str = os.path.dirname(__file__)
        path: str = os.path.join(base_dir, "locale", f"{self.locale}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.strings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"[Translator] Failed to load locale {self.locale}: {e}")
            self.strings = {}

    def t(self, key: str, *args: Any) -> str:
        """
        Translates a given key. Can format if arguments are provided.
        Example: t('err_osm_failed', 'file not found')
        """
        text: str = self.strings.get(key, f"[{key}]")
        if args:
            try:
                return text.format(*args)
            except Exception:
                return text
        return text


# Export global default instance for convenience
translator: Translator = Translator()
