# Documentation

Comprehensive Sphinx-based documentation for SLURM Monitoring.

## Building Documentation

### Using Pixi

```bash
# Build HTML documentation
pixi run docs-build

# View the documentation
open docs/_build/html/index.html

# Or serve locally and open in browser
pixi run docs-serve
# Then visit http://localhost:8000
```

### Using Make

```bash
# Build documentation
make docs

# Serve locally
make docs-serve

# Clean build artifacts
make docs-clean
```

### Manual Build

```bash
# Ensure Sphinx is installed
pixi install

# Build documentation
cd docs
sphinx-build -b html . _build/html

# View
open _build/html/index.html
```

## Documentation Structure

- **index.rst** - Main documentation index and overview
- **installation.rst** - Installation and setup instructions
- **usage.rst** - Command-line, Python, and REST API usage guide
- **deployment.rst** - Production deployment and operational guidelines
- **architecture.rst** - System architecture and design decisions
- **api.rst** - Auto-generated API reference documentation
- **faq.rst** - Frequently asked questions and troubleshooting

## Documentation Features

✨ **Comprehensive Coverage**
- Installation and setup guides
- Usage examples (CLI, REST API, Python library)
- Production deployment instructions
- Architecture and design documentation
- Complete API reference with auto-documentation
- Frequently asked questions and troubleshooting

📚 **Auto-Generated API Docs**
- Automatic extraction from docstrings
- Full API method references
- Parameter and return type documentation

🎨 **Professional Theme**
- Read the Docs theme
- Mobile-friendly responsive design
- Full-text search
- Code syntax highlighting

## Viewing Documentation

### Online in Browser

1. Build the docs: `pixi run docs-build`
2. Open `docs/_build/html/index.html` in your browser

### Local HTTP Server

Serve docs locally for better performance:

```bash
# Build and serve
pixi run docs-serve

# Then visit http://localhost:8000
```

### PDF Generation (Optional)

To generate PDF documentation, install LaTeX and use:

```bash
pixi run docs -b pdf
```

## Contributing to Documentation

### Adding New Pages

1. Create `.rst` file in `docs/` directory
2. Add to `index.rst` toctree
3. Build and verify: `pixi run docs-build`

### Restructured Text (reST) Basics

```rst
Section Title
=============

Subsection
^^^^^^^^^^

**Bold text** and *italic text*

- Bullet point
- Another point

1. Numbered list
2. Second item

.. code-block:: python

    code_example = True

.. note::
   Important note
```

### Code Examples

Include working examples:

```rst
.. code-block:: bash

    pixi run cli stats --days 30
```

### API Documentation

Use Sphinx autodoc directives:

```rst
.. automodule:: slurm_monitoring.analyzer
   :members:
   :undoc-members:
```

## Configuration

Documentation settings in `conf.py`:

- **Project info**: Name, version, author
- **Extensions**: Autodoc, autodoc summary, RTD theme
- **Theme**: Read the Docs with custom colors
- **Build options**: Output formats, exclusions

## Troubleshooting

### Build Fails

```bash
# Clean build
make docs-clean

# Full rebuild
make docs

# Check for errors
pixi run docs-build 2>&1 | grep -i error
```

### Module Import Errors

Ensure `conf.py` correctly adds source directory:

```python
import sys
sys.path.insert(0, os.path.abspath("../src"))
```

### Links Not Working

- Use relative paths in reST
- Use `:doc:` for internal links: `:doc:usage`
- Use `:ref:` for reference labels

## Building for CI/CD

Example GitHub Actions workflow:

```yaml
name: Build Docs
on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: prefix-dev/setup-pixi@v0.4.1
      - run: pixi run docs-build
      - uses: actions/upload-artifact@v3
        with:
          name: html-docs
          path: docs/_build/html/
```

## Hosting Documentation

### GitHub Pages

```bash
# Build docs
pixi run docs-build

# Commit to gh-pages branch
git checkout --orphan gh-pages
git rm -rf .
cp -r docs/_build/html/* .
git add .
git commit -m "Deploy documentation"
git push origin gh-pages
```

### Read the Docs

Connect repository to [readthedocs.org](https://readthedocs.org):
1. Push `.rtd.yml` configuration
2. Link repository to Read the Docs
3. Documentation auto-builds on push

### Self-Hosted

Use any web server (Nginx, Apache):

```bash
# Build static docs
pixi run docs-build

# Copy to web root
cp -r docs/_build/html/* /var/www/html/slurm-docs/
```

## See Also

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
