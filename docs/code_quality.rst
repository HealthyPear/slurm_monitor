Code Quality & Pre-commit Setup
================================

This guide explains the code quality infrastructure, how to use it, and how to integrate it with your development workflow.

What Was Added
--------------

Configuration Files
~~~~~~~~~~~~~~~~~~~

1. **``.pre-commit-config.yaml``** - Git hook configurations
   - Black: Code formatting (100 char lines, Python style)
   - Ruff: Fast Python linter with auto-fix
   - MyPy: Static type checking
   - File checks: YAML/JSON syntax, large files, merge conflicts
   - Docstring coverage: Ensures >50% documentation

2. **``.mypy.ini``** - Type checking configuration
   - Python 3.9+ compatibility
   - Strict type checking with nullable types
   - Per-module import handling
   - Configured to ignore missing stubs for major libraries

Documentation Files
~~~~~~~~~~~~~~~~~~~

1. **``CONTRIBUTING.md``** - Comprehensive development guide
   - Development workflow and setup
   - Code standards and style guide
   - Type hints best practices
   - Testing guidelines
   - Pre-commit hook usage
   - Common development tasks
   - Pull request checklist

2. **``DEV_QUICKREF.md``** - Quick reference for developers
   - Essential commands table
   - Common development tasks
   - Pre-commit hook reference
   - Type hints examples
   - Common issues and solutions

Configuration Updates
~~~~~~~~~~~~~~~~~~~~~

1. **``pixi.toml``** - Added development tasks
   - ``pre-commit-install`` - Install hooks
   - ``pre-commit-run`` - Run checks on all files
   - Updated ``type-check`` - Uses .mypy.ini config
   - Development dependencies: pre-commit (>=3.0.0)

2. **``Makefile``** - Added pre-commit targets
   - ``make pre-commit-install`` - Install hooks
   - ``make pre-commit`` - Run checks
   - Updated help message

3. **``README.md``** - Updated with development info
   - Quick link to CONTRIBUTING guide
   - Development tools overview
   - Code quality tools list
   - Simplified quick start

4. **``DEVELOPMENT.md``** - Enhanced with pre-commit guides
   - MyPy configuration details
   - Type checking examples
   - Pre-commit installation and usage
   - Hook reference and configuration

5. **``.gitignore``** - Added pre-commit artifacts
   - ``.pre-commit-config.yaml.bak`` exclusion

Documentation Integration
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **``docs/usage.rst``** - Added code quality section
   - Type hints best practices
   - Pre-commit workflow examples
   - Development tools reference table
   - Full development workflow example

How to Use
----------

First Time Setup
~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Install environment
    pixi install

    # Install pre-commit hooks
    pixi run pre-commit-install
    # or
    make pre-commit-install

Development Workflow
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Before committing
    pixi run quality    # Run all checks

    # Or individually
    pixi run format     # Black formatting
    pixi run lint       # Ruff linting
    pixi run type-check # MyPy type checking
    pixi run test       # Run tests

    # Commit (pre-commit hooks run automatically)
    git add .
    git commit -m "message"

    # If hooks fail, fix and retry
    pixi run format
    pixi run lint
    git add .
    git commit -m "message"

Useful Commands
~~~~~~~~~~~~~~~

.. code-block:: bash

    # Type check with details
    mypy src/ --show-error-codes

    # Run specific pre-commit hook
    pre-commit run black --all-files

    # Skip hooks temporarily
    git commit --no-verify

    # Run all hooks on specific file
    pre-commit run --files src/file.py

File Reference
---------------

+------------------------------+-------------------------------------+
| File                         | Purpose                             |
+==============================+=====================================+
| ``.pre-commit-config.yaml``  | Pre-commit hook definitions         |
+------------------------------+-------------------------------------+
| ``.mypy.ini``                | Type checking configuration         |
+------------------------------+-------------------------------------+
| ``CONTRIBUTING.md``          | Full development guide              |
+------------------------------+-------------------------------------+
| ``DEV_QUICKREF.md``          | Quick command reference             |
+------------------------------+-------------------------------------+
| ``Makefile``                 | Make targets for development        |
+------------------------------+-------------------------------------+
| ``pixi.toml``                | Pixi tasks and dependencies         |
+------------------------------+-------------------------------------+
| ``README.md``                | Project overview (updated)          |
+------------------------------+-------------------------------------+
| ``DEVELOPMENT.md``           | Development notes (updated)         |
+------------------------------+-------------------------------------+
| ``docs/usage.rst``           | Usage documentation (updated)       |
+------------------------------+-------------------------------------+

Quality Checks Included
-----------------------

✅ **Code Formatting** - Black ensures consistent style
✅ **Linting** - Ruff catches issues and suggests fixes  
✅ **Type Checking** - MyPy ensures type safety
✅ **YAML/JSON** - Syntax validation
✅ **Large Files** - Prevents accidental binary/large file commits
✅ **Merge Conflicts** - Catches forgotten conflict markers
✅ **Documentation** - Ensures minimum docstring coverage
✅ **Trailing Whitespace** - Cleans up formatting

Integration with Development Tools
-----------------------------------

IDE Integration
~~~~~~~~~~~~~~~

Most IDEs can be configured to use these tools:

**VSCode**:

.. code-block:: json

    {
      "python.formatting.provider": "black",
      "python.linting.ruffEnabled": true,
      "python.linting.mypyEnabled": true
    }

**PyCharm**:

- Settings → Tools → Python Integrated Tools → Linter: Ruff
- Settings → Tools → Python → Default test runner: pytest

CI/CD Integration
~~~~~~~~~~~~~~~~~

Pre-commit hooks can run in CI pipelines:

.. code-block:: yaml

    # GitHub Actions example
    - run: pixi run quality
    - run: pixi run test

Common Workflows
----------------

Adding a New Feature
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Create branch
    git checkout -b feature/my-feature

    # Make changes and test
    pixi run test
    pixi run quality

    # Commit (hooks run automatically)
    git commit -m "Add feature: description"

    # Push and create PR
    git push origin feature/my-feature

Fixing Pre-commit Issues
~~~~~~~~~~~~~~~~~~~~~~~~

If pre-commit fails:

.. code-block:: bash

    # See what's wrong
    pixi run pre-commit-run

    # Most issues auto-fixable
    pixi run format
    pixi run lint

    # Re-add and commit
    git add .
    git commit -m "Fix formatting"

Before Pushing to Main
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run full quality suite
    pixi run quality

    # Run tests
    pixi run test

    # Build docs should work
    pixi run docs-build

    # Now safe to push
    git push origin feature/my-feature

Documentation Links
-------------------

- **:doc:`contributing`** - Full development guide
- **:doc:`quickref`** - Quick reference
- **:doc:`usage`** - Usage with code quality section
- See GitHub repository for additional guides

Questions?
----------

See:
- :doc:`quickref` for quick answers
- :doc:`contributing` for detailed guidance
- :doc:`faq` for common issues
