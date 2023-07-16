# Hermes

HERON orbit analysis for mission OPS.

Hermes uses [supernova](https://github.com/utat-ss/supernova) and [celest](https://github.com/JaiWillems/Celest) to perform analysis on HERON orbit, and passes over the ground station.

![image](https://github.com/utat-ss/hermes/assets/54449457/6344c177-958b-4fc3-a800-f8d008e06866)

It's still in development.

## Installation

### Requirements

- Python 3.8 - 3.10
- C compiler (e.g. GCC, MSVC, Clang)
  - On linux, GCC should already be installed by default
  - On Windows, install [MSVC](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019)

### Steps

0. **Make doubly sure that you have a C compiler installed!**
1. Clone the repo and open a terminal in the resository root
2. Make a virtual environment (optional, but recommended, especially on Windows)
3. Run `pip install -e .`

The installation script will automatically compile the C extension.

That's it! You're ready to go.

### Usage

Still working on an actual API, but for now, open `mission.py`, fill in your initial state vector etc., and run the script to get a list of imaging windows.
