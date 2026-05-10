# Contributing to SELMA

Thank you for your interest in contributing to SELMA!

## How to Contribute

1. **Fork** the repository on Codeberg
2. **Create a branch** for your feature or fix
3. **Make your changes** with clear commit messages
4. **Run tests** to ensure nothing is broken
5. **Submit a pull request** with a description of your changes

## Development Setup

```bash
git clone https://codeberg.org/Ronin48/SELMA.git
cd SELMA
pip install -r requirements.txt
python tests/test_schema.py
```

## Areas for Contribution

- **Additional jurisdictions** — Add criminal codes from other states
- **Training data** — Create high-quality incident-to-charge training examples
- **Evaluation** — Expand the benchmark suite with new test scenarios
- **Documentation** — Improve guides and examples
- **Model improvements** — Experiment with training configurations

## Code Style

- Follow PEP 8
- Add docstrings to all public functions
- Include type hints
- Write tests for new functionality

## License

By contributing, you agree that your contributions will be licensed under
the Apache License 2.0.
