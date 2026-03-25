---
apply: by file patterns
patterns: .github/**/*, .gitea/**/*, docker/**/*, .pre-commit-config.yaml, .env.example, CODEOWNERS, CONTRIBUTING.md, Makefile, SECURITY.md, template.meta.toml, scripts/check_adrs.py, scripts/check_ci_symmetry.py, scripts/check_environment.py, scripts/check_repo_structure.py, scripts/check_specs.py, scripts/check_template_consistency.py, scripts/template_meta.py, scripts/run_docker_builds.sh, scripts/run_hadolint.sh, scripts/run_shellcheck.sh, scripts/run_trivy_fs.sh
---

# Repo Governance And CI

Path scope:

- `.github/**`
- `.gitea/**`
- `docker/**`
- `.pre-commit-config.yaml`
- `.env.example`
- `CODEOWNERS`
- `CONTRIBUTING.md`
- `Makefile`
- `SECURITY.md`
- `template.meta.toml`
- `scripts/check_adrs.py`
- `scripts/check_ci_symmetry.py`
- `scripts/check_environment.py`
- `scripts/check_repo_structure.py`
- `scripts/check_specs.py`
- `scripts/check_template_consistency.py`
- `scripts/template_meta.py`
- `scripts/run_docker_builds.sh`
- `scripts/run_hadolint.sh`
- `scripts/run_shellcheck.sh`
- `scripts/run_trivy_fs.sh`

Применяй это правило при изменении CI, governance, repo-wide automation и container tooling.

Обязательные ADR:

- [ADR-0001](../../docs/adr/architecture/0001-monorepo-and-bounded-contexts.md)
- [ADR-0012](../../docs/adr/architecture/0012-define-repository-layout-and-file-placement-rules.md)
- [ADR-0015](../../docs/adr/architecture/0015-enforce-template-quality-gates-and-governance-baseline.md)
- [ADR-0016](../../docs/adr/architecture/0016-support-github-and-gitea-ci-for-template-repositories.md)

Правила:

- локальные hooks и CI не должны расходиться по смыслу;
- GitHub и Gitea pipelines должны оставаться эквивалентными по quality gates;
- любые новые repo-wide каталоги и mandatory artifacts сначала отражаются в ADR и индексах;
- security и quality checks нельзя ослаблять без явного ADR или явного решения пользователя;
- container, shell и filesystem scans считаются частью baseline, а не optional tooling.
