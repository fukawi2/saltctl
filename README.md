# SaltCtl

Interactive shell for managing Salt minions with command history logging and output archiving.

## Features

- **Interactive shell** with readline support (command history, tab completion)
- **Host selection** with partial pattern matching (wildcards added automatically)
- **Salt operations** - Test and Apply your Salt states
- **Command history** - all actions logged to SQLite database
- **Salt output archive** - full salt command output stored in database for later review/audit

## Requirements

- Python 3
- Salt (`salt-key` and `salt` commands must be available)

## Quick Start

```
$ ./saltctl.py
SaltCtl - Salt Minion Management
Type 'help' for available commands.

saltctl> select web
Selected 3 host(s):
  - web01
  - web02
  - web03

saltctl [3 host(s)]> push test
Running: sudo salt --list web01,web02,web03 state.test
Command completed successfully. Run 'output' to show results.

saltctl [3 host(s)]> push apply
Running: sudo salt --list web01,web02,web03 state.apply
Command completed successfully. Run 'output' to show results.
```

## Configuration

SaltCtl reads configuration from the following locations in order (later files override earlier ones):

1. `/etc/saltctl.conf` (system-wide configuration)
2. `~/.config/saltctl.conf` (user-specific configuration)

### Configuration Format

Configuration files use INI format:

```ini
[salt]
# Use `sudo` when running salt commands.
# Set to `true` unless your user has permission to execute salt commands without sudo.
use_sudo = true

[history]
# Number of days to keep in command history before the 'history trim' command will delete entries (default: 90)
trim_days = 90
```

## Installation

### From .deb Package (Recommended)

Download the latest `.deb` package from the [Releases](https://github.com/fukawi2/saltctl/releases) page and install:

```bash
sudo dpkg -i saltctl_*.deb
```

The `saltctl` command will be available system-wide.

### From Source

Install using pip:

```bash
pip install .
```

Or run directly from the repository:

```bash
./saltctl.py
```

## Available Commands

- **select** `[pattern...]` - Select hosts with partial matching (e.g., `select fw`, `select web1 web2`). Use explicit wildcards for prefix/suffix matching (e.g., `fw*`, `*.nyc`)
- **push** `[test|apply]` - Run salt `state.test` or `state.apply` on selected hosts
- **list** - Show all available minions
- **status** - Show currently selected hosts
- **ping** - Ping salt-minion process on selected hosts
- **history** `[full|trim]` - View command history or trim old entries
- **output** `<command_id>` - View saved salt output from a previous command
- **help** `[command]` - Show help for all commands or a specific command
- **exit** - Exit the shell

Type `help <command>` within the shell for detailed usage of any command.

## Database

SaltCtl maintains a SQLite database at `~/.saltctl.db` containing:

- **Command history** - timestamp, user, selected hosts, command, and execution duration
- **Salt outputs** - full output from all salt test/apply commands with return codes

Use `history trim` to delete entries older than 90 days.

## Command History

The shell maintains persistent command history in `~/.saltctl_history` with readline support for:
- Up/down arrow navigation through previous commands
- Ctrl-R for reverse history search
- Tab completion for command names

## Output Paging

The `output` command automatically pages long output through a pager for easier viewing.

### Pager Configuration

Control paging behavior using environment variables:

- **SALTCTL_PAGER** - Application-specific pager (takes precedence)
- **PAGER** - System-wide pager setting (used if `SALTCTL_PAGER` not set)
- **Default** - Uses `less -RFX` if neither variable is set
  - `-R`: Preserve ANSI color codes
  - `-F`: Exit automatically if content fits on one screen
  - `-X`: Don't clear screen on exit

### Disabling Paging

To disable paging completely:

```bash
export SALTCTL_PAGER=""
```

Or for a single execution:

```bash
SALTCTL_PAGER="" saltctl
```

## Development

### Running Tests

Install test dependencies:

```bash
pip install pytest pytest-cov
pip install -e .
```

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=. --cov-report=html
```
