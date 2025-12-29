# CI/CD Quick Start Guide

Get started with the CI/CD pipeline in 5 minutes!

## Prerequisites

**First time setup?** Read [SETUP.md](SETUP.md) for complete environment setup instructions including Python installation and virtual environment setup.

**Already have Python?** Continue below:

## 0. Set Up Virtual Environment (Required)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (do this every time you work on the project)
source venv/bin/activate   # macOS/Linux
# or
venv\Scripts\activate      # Windows

# You should see (venv) in your terminal prompt
```

## 1. Install Development Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
cd lambda
pip install -r requirements.txt -r requirements-dev.txt
cd ..
```

## 2. Set Up Pre-Commit Hooks (Optional but Recommended)

Pre-commit hooks automatically check your code before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Test it (optional)
pre-commit run --all-files
```

Now every time you commit, your code will be automatically checked!

## 3. Run Tests Locally

```bash
# Using Make (recommended)
make test

# Or directly
cd lambda
python -m unittest discover -s tests -p "test_*.py" -v
```

## 4. Check Code Quality

```bash
# Run all CI checks
make ci

# Or run individual checks:
make lint          # Check code quality
make format        # Check formatting
make security      # Security scan
make coverage      # Test coverage
```

## 5. Fix Issues Automatically

```bash
# Auto-fix linting issues
make lint-fix

# Auto-format code
make format-fix
```

## 6. Push to GitHub

Once your code passes all checks:

```bash
git add .
git commit -m "Your message"
git push
```

The CI pipeline will automatically run on GitHub Actions!

## 7. Set Up AWS Deployment (Optional)

To enable automatic deployment:

1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. Create `samconfig.toml`:
   ```bash
   cp samconfig.toml.example samconfig.toml
   # Edit samconfig.toml with your AWS details
   ```

4. Deploy:
   ```bash
   # Via GitHub Actions (manual trigger)
   # Go to Actions → Deploy to AWS Lambda → Run workflow

   # Or deploy locally
   make deploy-dev
   ```

## Quick Reference

### Most Common Commands

```bash
make help           # Show all available commands
make install-dev    # Install all dependencies
make test           # Run tests
make ci             # Run all CI checks
make lint-fix       # Fix linting issues
make format-fix     # Format code
make coverage       # Test coverage report
make clean          # Clean temporary files
```

### Pre-Commit Hooks

```bash
pre-commit install              # Install hooks
pre-commit run --all-files      # Run on all files
pre-commit uninstall            # Remove hooks
```

### Viewing CI Results

1. Go to your GitHub repository
2. Click the "Actions" tab
3. Select a workflow run to see results

### Next Steps

- Read [CI_CD_GUIDE.md](CI_CD_GUIDE.md) for detailed documentation
- Review the workflow files in `.github/workflows/`
- Customize settings in `pyproject.toml`

## Troubleshooting

**Tests failing?**
```bash
cd lambda
python -m unittest discover -s tests -p "test_*.py" -v
```

**Linting errors?**
```bash
make lint-fix
make format-fix
```

**Import errors?**
```bash
pip install -r requirements.txt -r requirements-dev.txt
```

**Pre-commit failing?**
```bash
pre-commit run --all-files --verbose
```

## Tips

- Run `make ci` before pushing to catch issues early
- Use pre-commit hooks to catch issues before committing
- Check the Actions tab on GitHub to see CI results
- Review the coverage report at `lambda/htmlcov/index.html`
