# Development Environment Setup

This guide will help you set up your Python development environment for the TfL Bus Checker project.

## Prerequisites

### Check Python Installation

```bash
python3 --version
```

You should have Python 3.11 or later. If you have Python 3.9 or 3.10, it will work for development but CI runs on 3.11+.

### Install Python (if needed)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or download from python.org
# https://www.python.org/downloads/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked during installation.

## Step 1: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated from your system Python.

```bash
# Navigate to the project root
cd /Users/tomriddhmcts/twr/bus-voice-skill

# Create a virtual environment named 'venv'
python3 -m venv venv
```

This creates a `venv` directory containing an isolated Python environment.

## Step 2: Activate the Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

You'll see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

## Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

Now you have the latest version of pip in your virtual environment!

## Step 4: Install Project Dependencies

```bash
# Install production dependencies
cd lambda
pip install -r requirements.txt

# Install development dependencies (testing, linting, etc.)
pip install -r requirements-dev.txt
```

## Step 5: Verify Installation

```bash
# Check installed packages
pip list

# Run tests to verify everything works
cd ..
make test
# Or: cd lambda && python -m unittest discover -s tests -p "test_*.py" -v
```

## Step 6: Set Up Pre-Commit Hooks (Optional but Recommended)

```bash
# Install pre-commit hooks
pre-commit install

# Test it
pre-commit run --all-files
```

## Daily Workflow

### Starting Your Work Session

Every time you open a new terminal:

```bash
# Navigate to project
cd /Users/tomriddhmcts/twr/bus-voice-skill

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Now you can run make commands, pip, python, etc.
```

### Deactivating the Virtual Environment

When you're done working:

```bash
deactivate
```

## Troubleshooting

### "python3: command not found"

- **macOS:** Install Python via Homebrew: `brew install python@3.11`
- **Linux:** Install via package manager: `sudo apt install python3`
- **Windows:** Download from python.org and ensure it's added to PATH

### "pip: command not found" (after activating venv)

The virtual environment should include pip. Try:
```bash
python -m pip --version
```

If that works, use `python -m pip install` instead of `pip install`.

### Virtual environment not activating

Make sure you're in the project root directory and the path to the activate script is correct.

### Permission errors when installing packages

Don't use `sudo pip install`! Make sure your virtual environment is activated - the `(venv)` prefix should appear in your prompt.

### Wrong Python version

If `python3 --version` shows an old version:
```bash
# macOS - install specific version
brew install python@3.11

# Create venv with specific version
python3.11 -m venv venv
```

## IDE Setup

### VS Code

1. Install the Python extension
2. Open the project folder
3. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
4. Type "Python: Select Interpreter"
5. Choose the interpreter from `./venv/bin/python`

VS Code will now use your virtual environment automatically!

### PyCharm

1. Open the project
2. Go to Preferences → Project → Python Interpreter
3. Click the gear icon → Add
4. Select "Existing environment"
5. Choose `venv/bin/python`

## Quick Reference

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
cd lambda
pip install -r requirements.txt -r requirements-dev.txt

# Deactivate venv
deactivate

# Delete venv (if you need to start over)
rm -rf venv                       # macOS/Linux
rmdir /s venv                     # Windows
```

## What's in Your Virtual Environment?

After installation, you'll have:
- **Production dependencies** (from `requirements.txt`):
  - ask-sdk-core (Alexa SDK)
  - requests (HTTP client)
  - python-dateutil (date handling)

- **Development dependencies** (from `requirements-dev.txt`):
  - pytest, coverage (testing)
  - ruff (linting & formatting)
  - bandit, safety (security scanning)
  - mypy (type checking)
  - pre-commit (git hooks)

## Next Steps

Once your environment is set up:

1. Read [QUICKSTART.md](QUICKSTART.md) for common commands
2. Run `make help` to see all available commands
3. Run `make ci` to run all CI checks locally
4. Read [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for detailed CI/CD documentation

## Keep Your Environment Updated

Periodically update your dependencies:

```bash
# Activate venv first
source venv/bin/activate

# Update pip
pip install --upgrade pip

# Update all dependencies
cd lambda
pip install --upgrade -r requirements.txt -r requirements-dev.txt
```
