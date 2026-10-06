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
# File: tests/test_optimizer_callbacks.py
# Author: Gabriel Moraes
# Date: 2026-09-29

import unittest
from unittest.mock import MagicMock
import optuna

from src.optimizer.callbacks import PruningCallback, EarlyStopping, StudyEarlyStoppingCallback


class TestOptimizerCallbacks(unittest.TestCase):
    def test_pruning_callback_not_pruned(self):
        mock_trial = MagicMock()
        mock_trial.should_prune.return_value = False

        cb = PruningCallback(mock_trial, monitor="loss")
        cb.check_pruned(current_step=1, current_score=0.45)

        mock_trial.report.assert_called_once_with(0.45, 1)
        mock_trial.should_prune.assert_called_once()

    def test_pruning_callback_triggers_prune(self):
        mock_trial = MagicMock()
        mock_trial.should_prune.return_value = True

        cb = PruningCallback(mock_trial, monitor="val_loss")
        with self.assertRaises(optuna.exceptions.TrialPruned):
            cb.check_pruned(current_step=2, current_score=1.5)

    def test_early_stopping_improvement_and_stagnation(self):
        es = EarlyStopping(patience=3, min_delta=0.05)
        self.assertFalse(es.early_stop)

        # Epoch 1: initial score
        es(1.0)
        self.assertEqual(es.best_score, 1.0)
        self.assertEqual(es.counter, 0)

        # Epoch 2: significant improvement (1.0 -> 0.9, delta=0.1 > 0.05)
        es(0.9)
        self.assertEqual(es.best_score, 0.9)
        self.assertEqual(es.counter, 0)
        self.assertFalse(es.early_stop)

        # Epoch 3: insignificant improvement (0.9 -> 0.88, delta=0.02 < 0.05) -> counter=1
        es(0.88)
        self.assertEqual(es.counter, 1)
        self.assertFalse(es.early_stop)

        # Epoch 4: degradation (0.88 -> 0.95) -> counter=2
        es(0.95)
        self.assertEqual(es.counter, 2)
        self.assertFalse(es.early_stop)

        # Epoch 5: degradation -> counter=3 >= patience -> early_stop=True
        es(0.92)
        self.assertEqual(es.counter, 3)
        self.assertTrue(es.early_stop)

    def test_study_early_stopping_callback(self):
        callback = StudyEarlyStoppingCallback(patience=2, min_delta=0.01)
        mock_study = MagicMock()
        mock_trial = MagicMock()

        # Trial 1: initial best
        mock_study.best_value = 0.50
        callback(mock_study, mock_trial)
        self.assertEqual(callback.best_value, 0.50)
        self.assertEqual(callback.counter, 0)

        # Trial 2: no significant improvement (0.495 is delta 0.005 < 0.01)
        mock_study.best_value = 0.495
        callback(mock_study, mock_trial)
        self.assertEqual(callback.counter, 1)
        mock_study.stop.assert_not_called()

        # Trial 3: still no improvement -> should trigger stop
        mock_study.best_value = 0.50
        callback(mock_study, mock_trial)
        self.assertEqual(callback.counter, 2)
        mock_study.stop.assert_called_once()

    def test_study_early_stopping_callback_no_trials_graceful(self):
        callback = StudyEarlyStoppingCallback()
        mock_study = MagicMock()
        # study.best_value raises ValueError when no trials are complete
        type(mock_study).best_value = unittest.mock.PropertyMock(side_effect=ValueError("No trials"))
        mock_trial = MagicMock()

        # Should not raise exception
        callback(mock_study, mock_trial)
        self.assertIsNone(callback.best_value)


if __name__ == "__main__":
    unittest.main()
