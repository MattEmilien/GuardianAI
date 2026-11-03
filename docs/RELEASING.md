# Releasing GuardianAI

Releases are made by the **Automated SemVer Release & Changelog** workflow (`.github/workflows/release.yml`). It is started by hand from the Actions tab.

## What one run does

1. Runs the quality gates: lint (`ruff`, fatal errors only), tests (`pytest tests`) and build (`python -m compileall`). If any gate fails, nothing is tagged.
2. Works out the next version from the latest `vX.Y.Z` tag.
3. Writes a new section at the top of `CHANGELOG.md`, grouped by commit type.
4. Dry run: shows the version and changelog in the run Summary, then stops.
   Real run: commits `chore(release): vX.Y.Z [skip ci]`, creates the tag, pushes both, and creates the GitHub Release.
5. With `release_files: windows_exe`, a second job builds `GuardianAI-vX.Y.Z.exe` with PyInstaller on Windows and attaches it with a `.sha256` file.

## Inputs

| Input | Default | Meaning |
| :--- | :--- | :--- |
| `release_bump` | `patch` | `patch`, `minor`, `major`, `prerelease` (adds or bumps `-rc.N`), or `custom` |
| `custom_version` | empty | Exact version without `v` when `release_bump` is `custom` |
| `prerelease` | false | Mark the GitHub Release as a pre-release |
| `dry_run` | false | Preview only; push nothing |
| `release_files` | `none` | `none` for no attached files, `windows_exe` to attach the Windows build |
| `allow_empty_release` | false | Allow a release with no commits since the last tag |

## One-time setup

1. Merge the workflow into `main`. The **Run workflow** button only appears for workflows on the default branch.
2. **Settings → Actions → General → Workflow permissions → Read and write permissions.**
3. If `main` is protected, add **GitHub Actions** to the ruleset bypass list, or the release commit push fails with `GH006`.

## First release

1. **Actions → Automated SemVer Release & Changelog → Run workflow** on `main` with `release_bump: custom`, `custom_version: 0.1.0`, `dry_run: true`.
2. Check the run Summary, then run again with `dry_run: false`.

After that: merge PRs → dry run → real run.

## Commit messages and changelog headings

| Commit | Heading |
| :--- | :--- |
| `feat!:` or `BREAKING CHANGE` in the body | Breaking Changes |
| `feat:` or starts with "Add"/"Added" | Features |
| `fix:` / `hotfix:` / `bug:` or starts with "Fix"/"Fixed" | Bug Fixes |
| `sec:` / `security:` or mentions security | Security & Hardening |
| `perf:` / `refactor:` | Performance & Refactoring |
| anything else | Documentation, CI & Maintenance |

A leading marker such as `[+]` is ignored when choosing the heading. Do not edit `CHANGELOG.md` by hand; the workflow owns it.

## When a release is blocked

Open the run's Summary page. The **Release blocked** table shows which stage failed and the usual fix.
