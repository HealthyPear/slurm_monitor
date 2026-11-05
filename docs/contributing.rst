Contributing to SLURM Monitoring
=================================

Thank you for your interest in contributing! This guide explains how to set up your development environment, run quality checks, and submit contributions.

Development Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- **Pixi**: Environment manager (see :doc:`installation`)
- **Git**: Version control
- **Python 3.9+**: Language requirement

Initial Setup
~~~~~~~~~~~~~

.. code-block:: bash

    # Clone the repository
    git clone <repository-url>
    cd slurm_monitoring

    # Install development environment
    pixi install

    # Install pre-commit hooks
    make pre-commit-install

Development Workflow
--------------------

1. Create a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git checkout -b feature/my-feature

2. Make Your Changes
~~~~~~~~~~~~~~~~~~~~

Edit code as needed. The pre-commit hooks will help maintain code quality.

3. Run Tests
~~~~~~~~~~~~

.. code-block:: bash

    # Run all tests
    pixi run test

    # Run specific test file
    pytest tests/test_analyzer.py -v

    # Run with coverage
    pixi run test

4. Check Code Quality
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Format your code
    pixi run format

    # Check linting
    pixi run lint

    # Type checking
    pixi run type-check

    # All quality checks
    pixi run quality

5. Commit Your Changes
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git add .
    git commit -m "Add feature: description"

Pre-commit hooks will automatically run. If they fail, fix the issues and try again.

.. code-block:: bash

    # If needed, skip hooks (not recommended)
    git commit --no-verify

6. Push and Create Pull Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git push origin feature/my-feature

Then create a pull request on GitHub with a clear description of changes.

Code Standards
--------------

Style Guide
~~~~~~~~~~~

We follow PEP 8 with these specific rules:

- **Line length**: 100 characters (enforced by Ruff)
- **Indentation**: 4 spaces
- **Imports**: Organized with ``isort`` (handled by Ruff)
- **Formatting**: Ruff autoformatting

Type Hints
~~~~~~~~~~

All functions should have type hints:

.. code-block:: python

    from typing import Optional, Dict, List
    import pandas as pd

    def analyze_jobs(
        jobs: pd.DataFrame,
        days: Optional[int] = 30,
    ) -> Dict[str, float]:
        """
        Analyze job data.

        Args:
            jobs: Job DataFrame
            days: Lookback period in days

        Returns:
            Statistics dictionary
        """
        pass

Docstrings
~~~~~~~~~~

Use Google-style docstrings:

.. code-block:: python

    def breakdown_by_user(self) -> Dict:
        """
        Get resource usage breakdown by user.

        Returns:
            Dictionary mapping usernames to usage statistics:
            - job_count: Number of jobs submitted
            - total_cores_allocated: Total cores used
            - average_cores_per_job: Average cores per job
            - total_cpu_hours: Total CPU hours consumed
        """
        pass

Error Handling
~~~~~~~~~~~~~~

Always handle errors gracefully:

.. code-block:: python

    try:
        data = collector.get_jobs()
    except subprocess.TimeoutExpired:
        logger.error(f"Collection timed out after {timeout}s")
        return pd.DataFrame()
    except Exception as e:
        logger.exception(f"Failed to collect data: {e}")
        return pd.DataFrame()

Pre-commit Hooks
----------------

What Gets Checked
~~~~~~~~~~~~~~~~~~

Hooks automatically run on each commit:

1. **Ruff** - Linting with auto-fix
2. **Ruff format** - Code formatting
3. **MyPy** - Type checking
4. **File checks** - YAML/JSON syntax, large files, merge conflicts
5. **Docstring coverage** - Minimum 25% documentation

Skip Hooks (If Needed)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Skip all hooks
    git commit --no-verify

    # Or temporarily disable pre-commit
    PRE_COMMIT=0 git commit

Manual Hook Execution
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Run all hooks on changed files
    pre-commit run

    # Run all hooks on all files
    make pre-commit
    # or
    pixi run pre-commit-run

    # Run specific hook
    pre-commit run ruff-format --all-files

Troubleshooting Hooks
~~~~~~~~~~~~~~~~~~~~~

**Hooks fail on commit**:

.. code-block:: bash

    # View the error
    pixi run pre-commit-run

    # Fix the issues (many are auto-fixable)
    pixi run format
    pixi run lint

    # Try committing again
    git commit -m "message"

**MyPy complaining about imports**:

Update ``.mypy.ini`` with the module:

.. code-block:: ini

    [mypy-package_name.*]
    ignore_missing_imports = True

Type Checking with MyPy
-----------------------

Running Type Checks
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Check entire project
    pixi run type-check

    # Check specific module
    mypy src/slurm_monitoring/analyzer/

    # Show detailed errors
    mypy src/ --show-error-codes

Type Hint Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

- Import types from ``typing`` module
- Use ``Optional[X]`` instead of ``X | None`` (Python 3.9 compatible)
- Specify return types for all functions
- Use descriptive type variables for generics

**Good**:

.. code-block:: python

    def get_users(
        self,
        days: int = 30,
    ) -> List[str]:
        pass

**Bad**:

.. code-block:: python

    def get_users(days=30):
        pass

Testing
-------

Writing Tests
~~~~~~~~~~~~~

Tests go in ``tests/`` directory:

.. code-block:: python

    import pytest
    from slurm_monitoring.analyzer import ClusterAnalyzer

    @pytest.fixture
    def sample_data():
        return pd.DataFrame({
            'JobID': ['1', '2'],
            'User': ['user1', 'user2'],
            # ...
        })

    def test_user_breakdown(sample_data):
        analyzer = ClusterAnalyzer(sample_data)
        result = analyzer.breakdown_by_user()
        assert 'user1' in result
        assert result['user1']['job_count'] == 1

Run Tests
~~~~~~~~~

.. code-block:: bash

    # All tests
    pixi run test

    # Specific test file
    pytest tests/test_analyzer.py -v

    # Specific test function
    pytest tests/test_analyzer.py::test_user_breakdown -v

    # With coverage report
    pixi run test

    # Coverage HTML report
    coverage html
    open htmlcov/index.html

Documentation
-------------

Building Docs
~~~~~~~~~~~~~

.. code-block:: bash

    # Build HTML documentation
    pixi run docs-build

    # View in browser
    open docs/_build/html/index.html

    # Serve locally
    pixi run docs-serve

Adding Documentation
~~~~~~~~~~~~~~~~~~~~~

- **Code docstrings**: Required for all functions and classes
- **RST files**: Add documentation in ``docs/`` for new features
- **README**: Update for major changes

Docstring Requirements
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def my_function(
        param: str,
        optional: Optional[int] = None,
    ) -> bool:
        """
        One-line summary.

        Longer description explaining what this does,
        including important details.

        Args:
            param: Description of param
            optional: Description of optional parameter

        Returns:
            Description of return value

        Raises:
            ValueError: When something is wrong

        Example:
            >>> result = my_function("test")
            >>> assert result is True
        """
        pass

Common Development Tasks
------------------------

Add a New Collector
~~~~~~~~~~~~~~~~~~~

1. Create file in ``src/slurm_monitoring/collector/``
2. Implement collector class with ``collect()`` method
3. Integrate into ``SlurmCollector``
4. Add unit tests
5. Update documentation

Add a New Analysis Method
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add method to appropriate analyzer class in ``analyzer/``
2. Add unit tests in ``tests/``
3. Update ``ClusterAnalyzer`` if adding major analysis
4. Document in docstring
5. Update usage guide

Add a New CLI Command
~~~~~~~~~~~~~~~~~~~~~

1. Add command function in ``cli.py``
2. Use ``@cli.command()`` and ``@click.option()`` decorators
3. Add help text
4. Implement functionality
5. Add tests (optional)
6. Update README

Pull Request Checklist
----------------------

Before submitting a PR:

- ☐ Tests pass: ``pixi run test``
- ☐ Code is formatted: ``pixi run format``
- ☐ No linting errors: ``pixi run lint``
- ☐ Types are correct: ``pixi run type-check``
- ☐ Pre-commit hooks pass: ``make pre-commit``
- ☐ Documentation updated (if needed)
- ☐ Commit messages are clear
- ☐ Branch is up to date with main

Code Review Process
-------------------

1. Maintainer reviews your code
2. Feedback provided for any changes needed
3. Address feedback and push updates
4. Maintain clean commit history if squashing needed
5. Merge once approved

Release Process
---------------

Maintainers handle releases:

1. Update version in ``pyproject.toml`` and ``pixi.toml``
2. Update ``CHANGELOG.md``
3. Create git tag
4. Build and publish to PyPI
5. Create GitHub release

Getting Help
------------

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue with reproducible example
- **Suggestions**: Open an Issue with context
- **Documentation**: See docs/ directory

Code of Conduct
---------------

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Report issues through appropriate channels

Resources
---------

- `Sphinx Documentation <https://www.sphinx-doc.org/>`_
- `MyPy Documentation <https://mypy.readthedocs.io/>`_
- `Pre-commit Documentation <https://pre-commit.com/>`_
- `Ruff Linter <https://docs.astral.sh/ruff/>`_

Additional Notes
----------------

- Keep PRs focused on single features
- Add tests for new functionality
- Update docs alongside code changes
- Follow existing code patterns
- Run ``make quality`` before pushing

Thank you for contributing!
