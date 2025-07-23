# GitHub Branching Strategy & Workflow

## Branch Naming Convention

Follow conventional branch naming with descriptive prefixes:

### Feature Development
- `feat/` - New features and functionality
  - `feat/user-authentication`
  - `feat/todo-crud-operations`
  - `feat/data-persistence`

### Documentation
- `docs/` - Documentation updates and additions
  - `docs/api-documentation`
  - `docs/readme-update`
  - `docs/contributing-guide`

### Testing
- `test/` - Test-related changes and improvements
  - `test/unit-tests`
  - `test/integration-tests`
  - `test/coverage-improvement`

### Bug Fixes
- `fix/` - Bug fixes and issue resolution
  - `fix/validation-error`
  - `fix/persistence-issue`
  - `fix/memory-leak`

### Code Quality
- `refactor/` - Code refactoring without changing functionality
  - `refactor/repository-pattern`
  - `refactor/service-layer`
  - `refactor/error-handling`

### Maintenance
- `chore/` - Maintenance tasks, dependencies, CI/CD
  - `chore/dependency-update`
  - `chore/ci-setup`
  - `chore/build-optimization`

## Commit Message Convention

Use conventional commits for clear history:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Examples:
- `feat(domain): add TodoItem model with Pydantic validation`
- `test(repository): add unit tests for JSON persistence`
- `fix(cli): resolve input validation error handling`
- `docs(readme): update installation instructions`
- `chore(deps): update pytest to v7.4.0`

## Workflow Process

### 1. Branch Creation
```bash
# Create and switch to new feature branch
git checkout -b feat/feature-name

# Push branch to remote
git push -u origin feat/feature-name
```

### 2. Development Cycle
- Make small, focused commits
- Write descriptive commit messages
- Run tests before committing
- Push changes regularly

### 3. Pull Request Process
- Create PR from feature branch to `main`
- Use descriptive PR title following conventional format
- Include detailed description with:
  - What changes were made
  - Why the changes were necessary
  - How to test the changes
  - Any breaking changes or migration notes

### 4. Code Review
- Request review from team members
- Address feedback and make necessary changes
- Ensure all CI checks pass
- Squash commits if needed for clean history

### 5. Merge Strategy
- Use "Squash and merge" for feature branches
- Use "Merge commit" for release branches
- Delete feature branch after successful merge

## Branch Protection Rules

Configure the following for `main` branch:
- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Restrict pushes that create files larger than 100MB
- Require signed commits (recommended)

## Release Strategy

### Version Tagging
- Use semantic versioning (e.g., `v1.0.0`, `v1.1.0`, `v1.0.1`)
- Create release tags from `main` branch
- Include release notes with changelog

### Hotfix Process
```bash
# Create hotfix branch from main
git checkout -b fix/critical-bug main

# After fix, merge to main and tag
git checkout main
git merge fix/critical-bug
git tag v1.0.1
git push origin main --tags
```

## Best Practices

### Branch Management
- Keep branches focused and short-lived
- Delete merged branches to keep repository clean
- Use draft PRs for work-in-progress features
- Rebase feature branches on main before merging

### Commit Hygiene
- Make atomic commits (one logical change per commit)
- Write clear, descriptive commit messages
- Avoid committing generated files or secrets
- Use `.gitignore` to exclude unnecessary files

### Collaboration
- Communicate changes that affect multiple developers
- Use GitHub issues to track bugs and feature requests
- Link PRs to related issues using keywords (fixes #123)
- Review code thoroughly and provide constructive feedback