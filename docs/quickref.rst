Quick Reference for Developers
================================

Essential Commands
-------------------

Initial Setup
~~~~~~~~~~~~~

.. code-block:: bash

    pixi install
    pixi run pre-commit-install

Before Committing
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pixi run quality              # Run all checks
    pixi run format && pixi run lint  # Auto-fix issues
    pixi run test                 # Run tests

Commit Workflow
~~~~~~~~~~~~~~~

.. code-block:: bash

    git add .
    git commit -m "message"       # Pre-commit hooks run automatically

If hooks fail, fix and retry:

.. code-block:: bash

    pixi run format
    pixi run lint
    git add .
    git commit -m "message"

Development Tasks
------------------

+-------------------+-------------------------------------+
| Task              | Command                             |
+===================+=====================================+
| Run tests         | ``pixi run test``                   |
+-------------------+-------------------------------------+
| Format code       | ``pixi run format``                 |
+-------------------+-------------------------------------+
| Lint              | ``pixi run lint``                   |
+-------------------+-------------------------------------+
| Type check        | ``pixi run type-check``             |
+-------------------+-------------------------------------+
| All checks        | ``pixi run quality``                |
+-------------------+-------------------------------------+
| Pre-commit setup  | ``pixi run pre-commit-install``     |
+-------------------+-------------------------------------+
| Pre-commit check  | ``pixi run pre-commit-run``         |
+-------------------+-------------------------------------+
| Build docs        | ``pixi run docs-build``             |
+-------------------+-------------------------------------+
| Serve docs        | ``pixi run docs-serve``             |
+-------------------+-------------------------------------+

Or use Make:

.. code-block:: bash

    make test                    # Run tests
    make lint                    # Lint code
    make format                  # Format code
    make quality                 # All checks
    make pre-commit-install      # Setup pre-commit
    make pre-commit              # Run pre-commit checks
    make docs                    # Build docs
    make docs-serve              # Serve docs locally

Pre-commit Hooks
----------------

Hooks automatically run on commit:

- ✅ **Ruff format**: Code formatting
- ✅ **Ruff**: Linting with fixes
- ✅ **MyPy**: Type checking
- ✅ **File checks**: YAML, JSON, large files, merge conflicts
- ✅ **Documentation**: Coverage >25%

Skip hooks if needed: ``git commit --no-verify``

Type Hints
----------

All functions should have type hints:

.. code-block:: python

    from typing import Optional, Dict, List
    import pandas as pd

    def analyze(
        jobs: pd.DataFrame,
        days: Optional[int] = 30,
    ) -> Dict[str, float]:
        """Analyze jobs and return statistics."""
        pass

Check types:

.. code-block:: bash

    pixi run type-check

Testing
-------

.. code-block:: bash

    # All tests
    pixi run test

    # Specific test
    pytest tests/test_analyzer.py::test_name -v

    # Coverage report
    coverage report
    coverage html && open htmlcov/index.html
