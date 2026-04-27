# SYNTHETIC  - An AI-Orchestrated Engine for Multi-Modal Traffic Scenario Synthesis
# Copyright (C) 2026 Noxfort Systems 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# File: optimizer/callbacks.py
# Author: Gabriel Moraes
# Date: 2025-11-27

import optuna

class PruningCallback:
    """
    Custom callback to integrate PyTorch training loops with Optuna's Pruning mechanism.
    It checks intermediate results and decides whether to stop the trial early.
    """

    def __init__(self, trial: optuna.trial.Trial, monitor: str = "val_loss"):
        """
        Args:
            trial (optuna.trial.Trial): The current optimization trial.
            monitor (str): The metric name to monitor (mostly 'loss' for GANs).
        """
        self.trial = trial
        self.monitor = monitor

    def check_pruned(self, current_step: int, current_score: float) -> None:
        """
        Reports the current score to Optuna and checks if the trial should be pruned.
        
        Args:
            current_step (int): The current epoch or iteration number.
            current_score (float): The value of the monitored metric (e.g., Loss).
        
        Raises:
            optuna.exceptions.TrialPruned: If Optuna decides this trial is not promising.
        """
        # Report the current value to Optuna
        self.trial.report(current_score, current_step)

        # Check if the trial should be pruned based on the configured Pruner (e.g., MedianPruner)
        if self.trial.should_prune():
            message = f"Trial pruned at step {current_step} with {self.monitor}={current_score:.4f}"
            print(f"[AutoML] {message}")
            raise optuna.exceptions.TrialPruned(message)

class EarlyStopping:
    """
    Standard Early Stopping mechanism independent of Optuna.
    Stops training if the loss does not improve after a set number of epochs (patience).
    """

    def __init__(self, patience: int = 10, min_delta: float = 1e-4):
        """
        Args:
            patience (int): How many epochs to wait after last improvement.
            min_delta (float): Minimum change to qualify as an improvement.
        """
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_score = None
        self.early_stop = False

    def __call__(self, current_loss: float):
        """
        Call at the end of each epoch to check status.
        
        Args:
            current_loss (float): The validation loss of the current epoch.
        """
        if self.best_score is None:
            self.best_score = current_loss
        elif current_loss > self.best_score - self.min_delta:
            # Loss did not decrease significantly
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
                print("[EarlyStopping] Patience limit reached. Stopping training.")
        else:
            # Loss improved
            self.best_score = current_loss
            self.counter = 0