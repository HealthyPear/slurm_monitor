Code Quality & Pre-commit Setup
================================

This guide explains the code quality infrastructure, how to use it, and how to integrate it with your development workflow.

What Was Added
--------------

Configuration Files
~~~~~~~~~~~~~~~~~~~

1. **``.pre-commit-config.yaml``** - Git hook configurations
   - Ruff: Code formatting (100 char lines, Python style)
   - Ruff: Fast Python linter with auto-fix
   - MyPy: Static type checking
   - File checks: YAML/JSON syntax, large files, merge conflicts
   - Docstring coverage: Ensures >25% documentation

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
    pixi run format     # Ruff formatting
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
    pre-commit run ruff-format --all-files

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

✅ **Code Formatting** - Ruff ensures consistent style
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
      "[python]": {"editor.defaultFormatter": "charliermarsh.ruff"},
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

Testing Your Code
-----------------

Running Tests on Your Laptop (Without SLURM)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The SLURM Monitoring package is designed to run tests on non-SLURM systems by using mocked SLURM commands and sample data.

Run all tests with coverage:

.. code-block:: bash

    pixi run test

This runs:
- Unit tests for analyzers
- Collector tests with mocked SLURM
- History collection tests
- Coverage analysis

Key Testing Principles
~~~~~~~~~~~~~~~~~~~~~~

#. **Mock SLURM Commands**: Tests use ``unittest.mock`` to simulate SLURM commands
#. **Sample Data**: Tests work with pandas DataFrames containing sample job data
#. **Fixtures**: Reusable test data in ``conftest.py``
#. **No Dependencies**: Tests run on laptops, CI systems, anywhere without SLURM

Test Files Overview
~~~~~~~~~~~~~~~~~~~

**``tests/test_analyzer.py``** - Analyzer logic tests
- Core utilization computation
- User breakdowns
- Peak time detection
- Job duration statistics

**``tests/test_history.py``** - Historical snapshot collection
- Recording snapshots to JSONL files
- Trend analysis calculations
- Empty data handling
- Multi-snapshot scenarios

**``tests/test_collectors.py``** - Collector mocking examples
- Mocking squeue output
- Handling timeouts
- Queue state parsing

**``tests/conftest.py``** - Shared test fixtures
- Sample job data
- Mock collectors
- Temporary directories
- Queue state samples

Writing New Tests
~~~~~~~~~~~~~~~~~

Example: Testing a new analyzer function

.. code-block:: python

    def test_my_new_analyzer_function(sample_jobs_data):
        """Test my new function with sample data"""
        analyzer = ClusterAnalyzer(sample_jobs_data)
        result = analyzer.my_new_function()

        # Assertions
        assert result is not None
        assert result["key"] > 0

Use the ``sample_jobs_data`` fixture (provided in conftest.py) instead of querying real SLURM.

Testing with Mock Subprocess
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When testing code that calls subprocess to run SLURM commands:

.. code-block:: python

    from unittest.mock import patch, MagicMock

    @patch("subprocess.run")
    def test_with_mocked_slurm(mock_run):
        """Test with mocked SLURM command output"""
        # Set up mock output
        mock_output = "JobID,State\n100,RUNNING\n101,PENDING"
        mock_run.return_value = MagicMock(
            stdout=mock_output,
            returncode=0
        )

        # Now your code can call "squeue" without SLURM installed
        collector = SqueueCollector()
        # ... test your code

Running Specific Tests
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run specific test file
    pytest tests/test_analyzer.py -v

    # Run specific test class
    pytest tests/test_history.py::TestHistoryCollector -v

    # Run specific test function
    pytest tests/test_history.py::TestHistoryCollector::test_record_snapshot -v

    # Run with coverage for specific file
    pytest src/slurm_monitoring/analyzer.py --cov=src/slurm_monitoring/analyzer -v

Coverage Analysis
~~~~~~~~~~~~~~~~~

The test runner generates coverage reports:

.. code-block:: bash

    # Generate HTML coverage report
    pixi run test

    # View coverage for specific modules
    coverage report -m src/slurm_monitoring/analyzer.py

The goal is >80% coverage for critical modules (collectors, analyzers).

Continuous Testing with Watch Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install pytest-watch for automatic test reruns:

.. code-block:: bash

    # Not included by default, but you can install:
    pixi add --features dev pytest-watch

    # Then run tests automatically on file change:
    ptw tests/

Testing Strategy Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~

✅ **Unit Tests** - Test individual functions with sample data
✅ **Fixtures** - Reuse test data across tests
✅ **Mocking** - Mock subprocess calls to SLURM commands
✅ **Coverage** - Aim for >80% code coverage
✅ **CI/CD** - Tests run in GitHub Actions without SLURM
✅ **Documentation** - Tests serve as usage examples

Common Testing Patterns
~~~~~~~~~~~~~~~~~~~~~~~~

**Testing data transformations:**

.. code-block:: python

    def test_data_transformation(sample_jobs_data):
        # Input: sample data
        # Process: run transformation
        # Output: assert expected results
        result = analyzer.transform_data(sample_jobs_data)
        assert len(result) == len(sample_jobs_data)

**Testing error handling:**

.. code-block:: python

    def test_graceful_error_handling(sample_jobs_data):
        # Test with empty data
        empty_data = pd.DataFrame()
        result = analyzer.process(empty_data)
        assert result is not None  # Should not crash

**Testing with time-based data:**

.. code-block:: python

    def test_time_window(sample_snapshots, temp_data_dir):
        # Snapshots already have timestamps in fixtures
        collector = HistoryCollector(data_dir=str(temp_data_dir))
        trends = collector.get_trends(hours=24)
        assert "avg_running" in trends

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
