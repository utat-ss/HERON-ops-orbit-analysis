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

### Package Installation - Steps

0. **Make doubly sure that you have a C compiler installed!**
1. Clone the repo and open a terminal in the resository root
2. Make a virtual environment (optional, but recommended, especially on Windows)
3. Run `pip install -e .`

The installation script will automatically compile the C extension.

That's it! You're ready to go. If you need to pull TLEs from Space-Track, see the next section.

### Authentication for Space-Track
If you want to use anything under `hermes.spacetrack`, you will need to give your Space-Track credentials. There are two ways to do this:
#### Option 1
Create environment variables called `SPACETRACK_EMAIL` and `SPACETRACK_PASSWORD`.

#### Option 2
Create a file called `.env` in the repository root, and add the following lines:
```
SPACETRACK_EMAIL=<your email>
SPACETRACK_PASSWORD=<your password>
```

## Usage
There are two demo scripts which show off the functionality of Hermes:

### `demos/propagate_and_analyze_heron.py`
This script propagates the HERON orbit for 50 days, starting from an initial state vector. It plots the orbit, initial/final TLEs, and finds times when the spacecraft is in view of the ground station.

### `demos/pull_tle_from_spacetrack.py`
This script finds the latest TLE for the ISS. Make sure to set your Space-Track credentials first!

### Remaining functionality
If you need something custom, there are probably bits and pieces in the existing codebase that may suit your needs. Take a look, and get in touch if you need something specific.