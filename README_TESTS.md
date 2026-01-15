Selenium test runner

How to run locally:

1. Install Python deps:

```bash
pip install -r requirements.txt
```

2. Start PHP built-in server from project root:

```bash
php -S 127.0.0.1:8000 -t .
```

3. Run tests:

```bash
pytest -q
```

GitHub Actions:

- Workflow file: [.github/workflows/selenium-tests.yml](.github/workflows/selenium-tests.yml)
- The workflow starts PHP and a MySQL service, imports `db/quiz_pengupil.sql`, creates a test user (`existinguser` / `TestPass1!`), runs the Selenium tests headless, and uploads a `pytest-report` artifact.
- To view results: open the repository's Actions tab, select the workflow run and download the `pytest-report` artifact.
