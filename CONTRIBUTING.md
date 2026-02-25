# Contributing to LunarTech

Thank you for your interest in contributing to LunarTech Deep RAG!

We welcome bug reports, feature requests, and code contributions. This document outlines the process for contributing to the repository.

## Finding Issues to Work On

Look at the GitHub Issues tab. Issues labeled `good first issue` are a great place to start. If you want to build a new feature (like a new *Smart Feature* or *Shadow Agent* type), please open a "Feature Request" issue first to discuss the implementation strategy with the maintainers.

## Development Workflow

1. **Fork the repository** to your own GitHub account.
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/yourusername/lunartech-deep-rag.git
   ```

3. **Create a new branch** for your feature or bug fix:

   ```bash
   git checkout -b feature/dynamic-ollama-routing
   ```

4. **Install dependencies** in a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Make your changes**. Ensure you follow the [Coding Standards](docs/development/coding_standards.md) strictly. Do not embed LLM calling logic inside UI view files (`app/views/`); keep it separated in `services/`.
6. **Test your code**. Run the Streamlit app locally (`streamlit run app/main.py`) and ensure there are no breaking changes in the navigation state.
7. **Commit your changes** with clear, descriptive commit messages.
8. **Push to your fork** and open a Pull Request against the `main` branch of the upstream repository.

## Submitting Pull Requests

- Provide a detailed description of what your PR accomplishes in the PR description body.
- If your PR introduces visual changes (UI adjustments), **please include before and after screenshots**.
- Ensure you have not committed any `.env` secrets or `.lightrag` document caches in your PR.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
