# IBKR Frontend Refresh - Part 4: Git Strategy

Version control workflow and conventions.

---

## Branching Model

Using **GitHub Flow** with feature-named branches:

```
main (production)
  │
  ├── develop (integration branch)
  │     │
  │     ├── foundation
  │     ├── authentication
  │     ├── portfolio-management
  │     ├── auto-invest
  │     ├── position-building
  │     ├── dashboard-ui
  │     └── launch-prep
  │
  └── hotfix/<description> (branches from main for critical fixes)
```

---

## Branch Naming Conventions

### Feature Branches (Primary Development)

Feature branches use the **feature name only** - clean and simple:

| Phase | Branch Name |
|-------|-------------|
| Phase 1 | `foundation` |
| Phase 2 | `authentication` |
| Phase 3 | `portfolio-management` |
| Phase 4 | `auto-invest` |
| Phase 5 | `position-building` |
| Phase 6 | `dashboard-ui` |
| Phase 7 | `launch-prep` |

### Sub-Feature Branches

For smaller tasks within a phase, branch from the feature branch:

| Pattern | Example |
|---------|---------|
| `<feature>/<sub-task>` | `portfolio-management/pie-crud` |
| `<feature>/<sub-task>` | `portfolio-management/slice-validation` |
| `<feature>/<sub-task>` | `auto-invest/allocation-engine` |
| `<feature>/<sub-task>` | `position-building/time-triggers` |
| `<feature>/<sub-task>` | `position-building/price-triggers` |

### Other Branch Types

| Type | Pattern | Example |
|------|---------|---------|
| Bug Fix | `fix/<description>` | `fix/weight-rounding-error` |
| Hotfix | `hotfix/<description>` | `hotfix/auth-token-expiry` |
| Release | `release/<version>` | `release/v1.0.0` |
| Chore | `chore/<description>` | `chore/update-dependencies` |

---

## Commit Message Format

Using **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes (formatting, etc.) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks |

**Scopes (by feature):**
| Scope | Feature Area |
|-------|--------------|
| `foundation` | Project setup, database schema |
| `auth` | Authentication, IBKR connection |
| `portfolio` | Portfolio, pie, slice management |
| `auto-invest` | Deposit allocation |
| `triggers` | Position building triggers |
| `dashboard` | Frontend UI |

**Examples:**
```
feat(portfolio): add pie creation endpoint
feat(auto-invest): implement allocation calculation engine
fix(triggers): correct price-based trigger evaluation
docs(foundation): add database schema documentation
test(portfolio): add unit tests for weight validation
```

---

## Pull Request Workflow

### Standard Flow

1. Create feature branch from `develop`
2. Make changes with atomic commits
3. Push branch and open PR against `develop`
4. Automated checks run (tests, linting, build)
5. Request code review (minimum 1 approval required)
6. Squash and merge after approval
7. Delete feature branch

### Sub-Feature Flow

1. Create sub-feature branch from parent feature branch
2. Complete sub-task with atomic commits
3. Open PR against parent feature branch
4. Review and merge
5. When feature complete, PR feature branch to `develop`

```
Example:
  develop
    └── portfolio-management
          ├── portfolio-management/pie-crud (PR → portfolio-management)
          ├── portfolio-management/slice-crud (PR → portfolio-management)
          └── portfolio-management/weight-validation (PR → portfolio-management)
          
  When all complete: portfolio-management (PR → develop)
```

---

## PR Requirements

- [ ] All tests passing
- [ ] Code coverage maintained or improved
- [ ] Linting passes (ESLint, Black, Flake8)
- [ ] At least 1 approving review
- [ ] No merge conflicts
- [ ] Linked to relevant issue(s)

### PR Title Format

```
[<feature>] <description>
```

**Examples:**
```
[foundation] Set up PostgreSQL database schema
[authentication] Implement IBKR OAuth flow
[portfolio-management] Add pie CRUD endpoints
[auto-invest] Build allocation calculation engine
[position-building] Implement time-based triggers
```

---

## Release Process

1. Create release branch from `develop`: `release/v1.x.x`
2. Final testing and bug fixes on release branch
3. Merge release branch to `main`
4. Tag release: `git tag -a v1.x.x -m "Release v1.x.x"`
5. Merge release branch back to `develop`
6. Deploy to production

---

## Protected Branches

| Branch | Rules |
|--------|-------|
| `main` | Require PR, require reviews (2), require status checks, no force push |
| `develop` | Require PR, require reviews (1), require status checks |

---

## CI/CD Pipeline

```yaml
# Triggered on PR and push to develop/main
Pipeline Steps:
  1. Lint (ESLint, Black, Flake8)
  2. Unit Tests
  3. Integration Tests
  4. Build
  5. Security Scan
  6. Deploy to Preview (PRs)
  7. Deploy to Staging (develop)
  8. Deploy to Production (main)
```

### Pipeline by Branch

| Branch | Pipeline Actions |
|--------|------------------|
| Feature branches | Lint, Test, Build, Preview Deploy |
| `develop` | Lint, Test, Build, Security Scan, Staging Deploy |
| `main` | Lint, Test, Build, Security Scan, Production Deploy |

---

## Quick Reference

### Create a new feature branch
```bash
git checkout develop
git pull origin develop
git checkout -b portfolio-management
```

### Create a sub-feature branch
```bash
git checkout portfolio-management
git pull origin portfolio-management
git checkout -b portfolio-management/pie-crud
```

### Commit with conventional format
```bash
git commit -m "feat(portfolio): add pie creation endpoint"
```

### Push and create PR
```bash
git push -u origin portfolio-management/pie-crud
# Then create PR via GitHub UI or CLI
```

---

## Related Documents

- [Part 1: Overview & Features](./plan-part1-overview.md)
- [Part 2: Development Phases](./plan-part2-development-phases.md)
- [Part 3: Testing Strategy](./plan-part3-testing-strategy.md)