# Contributing to Puerto Rico Elections Platform

Thank you for your interest in contributing to this open data project!

## Ways to Contribute

### Data
- Report data quality issues
- Help validate scraped data against official sources
- Suggest additional data sources

### Code
- Improve the web scraper
- Enhance the R, Python, or JS packages
- Add tests and documentation

### Documentation
- Translate documentation to Spanish
- Write tutorials and examples
- Improve data dictionaries

## Development Setup

### Prerequisites
- Python 3.10+
- R 4.0+
- Node.js 18+
- Git

### Getting Started

```bash
# Clone the repository
git clone https://github.com/opendatapr/puerto-rico-elections-platform.git
cd puerto-rico-elections-platform

# Set up Python environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e ".[dev]"

# Set up R package development
# In R:
# install.packages("devtools")
# devtools::load_all("packages/r")

# Set up JS package
cd packages/js
npm install
```

## Code Style

- **Python**: Follow PEP 8, use `ruff` for linting
- **R**: Follow tidyverse style guide
- **JavaScript/TypeScript**: Use Prettier and ESLint

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`, `R CMD check`, `npm test`)
5. Commit with descriptive messages
6. Push to your fork
7. Open a Pull Request

## Reporting Issues

When reporting bugs, please include:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, language versions)

## Code of Conduct

Be respectful and inclusive. We're building tools for civic engagement and welcome contributors from all backgrounds.

## Questions?

Open an issue with the `question` label or reach out to the maintainers.
