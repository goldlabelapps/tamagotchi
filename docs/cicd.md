# CI/CD with GitHub Actions

**CI/CD** stands for **Continuous Integration / Continuous Delivery** (or Deployment). It is the practice of automatically building, testing, and deploying your code every time you push a change. This document explains the concepts and shows how to set up a CI/CD pipeline for this project using **GitHub Actions**.

---

## 1. What is Continuous Integration (CI)?

Before CI, developers would work independently for days or weeks and then merge their branches — often discovering that the combined code was broken. CI solves this by:

1. Running automated tests on **every push** (and every pull request)
2. Reporting pass/fail status immediately
3. Blocking broken code from being merged into the main branch

> "Integrate early, integrate often."

For this project, CI means: *every time someone pushes code, pytest runs automatically*.

---

## 2. What is Continuous Delivery/Deployment (CD)?

- **Continuous Delivery** — after CI passes, a build artifact is prepared and *ready* to deploy with one click.
- **Continuous Deployment** — the deployment to production happens *automatically* after CI passes, with no human step.

For this project, CD means: *if the tests pass on the main branch, deploy to Render.com automatically*.

---

## 3. GitHub Actions

GitHub Actions is GitHub's built-in CI/CD platform. You define **workflows** in YAML files inside `.github/workflows/`. GitHub runs them on its cloud infrastructure whenever the trigger events occur (push, pull request, schedule, etc.).

Key concepts:

| Term | Meaning |
|------|---------|
| **Workflow** | A YAML file in `.github/workflows/` that defines a pipeline |
| **Event** | What triggers the workflow (e.g. `push`, `pull_request`) |
| **Job** | A group of steps that run on the same machine |
| **Step** | A single shell command or reusable Action |
| **Action** | A reusable unit of CI logic published on the GitHub marketplace |
| **Runner** | The virtual machine that executes the job (`ubuntu-latest`, `windows-latest`, etc.) |

---

## 4. Example CI Workflow

Create this file at `.github/workflows/ci.yml` in the repository:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      # 1. Check out the repository code
      - name: Checkout code
        uses: actions/checkout@v4

      # 2. Set up the correct Python version
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      # 3. Install dependencies
      - name: Install dependencies
        run: pip install -r requirements.txt

      # 4. Run the test suite
      - name: Run tests
        run: pytest tests/ -v
```

### What this does

1. **Triggers** on every push to `main` and every pull request targeting `main`.
2. **Checks out** the code so the runner has a copy.
3. **Sets up Python 3.12** (matching the project's runtime).
4. **Installs dependencies** from `requirements.txt`.
5. **Runs pytest** — if any test fails, the job fails and GitHub shows a red cross on the commit/PR.

---

## 5. Adding Automated Deployment to Render

Render supports deploy hooks — a URL you POST to in order to trigger a deployment.

```yaml
  deploy:
    runs-on: ubuntu-latest
    needs: test          # only runs if the test job succeeded
    if: github.ref == 'refs/heads/main'   # only on the main branch

    steps:
      - name: Trigger Render deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

**Steps to set this up:**
1. In the Render dashboard, go to your Web Service → *Settings* → *Deploy Hooks* → copy the URL.
2. In your GitHub repository, go to *Settings* → *Secrets and variables* → *Actions* → add a secret named `RENDER_DEPLOY_HOOK_URL` with the Render hook URL as the value.
3. Add the `deploy` job above to your workflow.

Now the full flow is:
```
Push to main → CI tests run → (if pass) → Render deployment triggered
```

---

## 6. GitHub Actions Secrets

Never hard-code API keys, tokens, or passwords in workflow files. Use **GitHub Actions secrets**:

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Secrets are encrypted, not visible in logs, and only accessible to the repository's workflows. Set them at *Settings → Secrets and variables → Actions*.

---

## 7. Status Badges

You can display the CI status in your `README.md` as a badge:

```markdown
![CI](https://github.com/goldlabelapps/tamagotchi/actions/workflows/ci.yml/badge.svg)
```

This badge turns green when tests pass and red when they fail — visible to anyone viewing the repository.

---

## 8. Pull Request Checks

When CI is set up, GitHub displays check results directly on pull requests:

```
✅ test (ubuntu-latest)   — All checks passed
❌ test (ubuntu-latest)   — 2 tests failed
```

You can configure **branch protection rules** (*Settings → Branches → Add rule*) to require CI to pass before a pull request can be merged. This prevents broken code from reaching `main`.

---

## 9. Full CI/CD Workflow File

Here is a complete `.github/workflows/ci.yml` combining tests and deploy:

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v

  deploy:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - name: Trigger Render deploy
        run: curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

---

## 10. CI/CD Benefits Summary

| Without CI/CD | With CI/CD |
|---------------|-----------|
| Tests run manually (or not at all) | Tests run automatically on every change |
| Broken code can reach production | Broken code is blocked before merge |
| Deployment is a manual, error-prone step | Deployment is automatic and reproducible |
| "Works on my machine" | Tested in a clean, consistent environment |

---

## Further Reading

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [GitHub Actions marketplace (reusable actions)](https://github.com/marketplace?type=actions)
- [Render deploy hooks](https://render.com/docs/deploy-hooks)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
