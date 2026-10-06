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
# File: tests/test_telemetry.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import os
import tempfile
import time
import unittest
from unittest.mock import patch, MagicMock

from src.core.telemetry import HardwareTelemetry


class TestHardwareTelemetry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_filename = "test_telemetry.log"

    def tearDown(self):
        log_path = os.path.join(self.temp_dir, self.log_filename)
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except OSError:
                pass
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    def test_telemetry_start_and_stop_lifecycle(self):
        telemetry = HardwareTelemetry(log_filename=self.log_filename, interval_sec=1)
        # Point log file to our temp directory
        telemetry.log_file = os.path.join(self.temp_dir, self.log_filename)

        telemetry.start()
        self.assertTrue(telemetry._running)
        self.assertIsNotNone(telemetry._thread)

        # Call start again (idempotent)
        telemetry.start()

        # Let the loop run at least once
        time.sleep(0.3)

        telemetry.stop()
        self.assertFalse(telemetry._running)

        # Call stop again (idempotent)
        telemetry.stop()

        self.assertTrue(os.path.exists(telemetry.log_file))
        with open(telemetry.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Telemetry Session Started", content)
        self.assertIn("RAM:", content)
        self.assertIn("Telemetry Session Ended", content)

    @patch("subprocess.run")
    def test_telemetry_with_nvidia_smi_mock(self, mock_subproc):
        mock_subproc.return_value = MagicMock(stdout="4096 MiB, 8192 MiB\n")

        telemetry = HardwareTelemetry(log_filename=self.log_filename, interval_sec=1)
        telemetry.log_file = os.path.join(self.temp_dir, self.log_filename)

        telemetry.start()
        time.sleep(0.3)
        telemetry.stop()

        with open(telemetry.log_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("4096 MiB, 8192 MiB", content)


if __name__ == "__main__":
    unittest.main()
