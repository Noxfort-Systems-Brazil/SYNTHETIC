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
# File: core/cuda_loader.py
# Author: Gabriel Moraes
# Date: 2026-08-16

import ctypes
import os
import site
import sys
from typing import List

def preload_cuda_libraries() -> List[str]:
    """
    Scans site-packages for nvidia pip packages and preloads shared libraries
    (libcudart, libcublas, libnvrtc, libcusparse, etc.) into the global dynamic linker space.
    This resolves shared library dependencies for libraries like llama-cpp-python and torch.
    """
    if not sys.platform.startswith("linux"):
        return []

    search_dirs = []
    try:
        if hasattr(site, "getsitepackages"):
            search_dirs.extend(site.getsitepackages())
        if hasattr(site, "getusersitepackages"):
            search_dirs.append(site.getusersitepackages())
    except Exception:
        pass

    loaded = []
    for sp in search_dirs:
        nvidia_root = os.path.join(sp, "nvidia")
        if not os.path.isdir(nvidia_root):
            continue

        for root, _, files in os.walk(nvidia_root):
            for file in sorted(files):
                if (file.startswith("libcudart.so") or 
                    file.startswith("libcublas.so") or 
                    file.startswith("libnvrtc.so") or 
                    file.startswith("libcusparse.so")) and ".so" in file:
                    full_path = os.path.join(root, file)
                    try:
                        ctypes.CDLL(full_path, mode=ctypes.RTLD_GLOBAL)
                        loaded.append(file)
                    except Exception:
                        pass
    return loaded

# Automatically run library preloading when module is loaded
preload_cuda_libraries()
