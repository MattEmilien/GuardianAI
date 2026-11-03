#!/usr/bin/env python3
"""Compute the next SemVer, sync version files and write the changelog.

Used by .github/workflows/release.yml. Standard library only.

Inputs come from environment variables (never from ${{ }} in the shell):
  RELEASE_BUMP         patch | minor | major | prerelease | custom
  CUSTOM_VERSION       exact version without "v" when RELEASE_BUMP=custom
  ALLOW_EMPTY_RELEASE  "true" to allow a release with no new commits
  REPO_URL             https://github.com/<owner>/<repo> (for compare links)
  NOTES_FILE           where to write the release notes (default: release_notes.md)

Outputs (appended to $GITHUB_OUTPUT when set):
  prev_tag, next_version, next_tag, changed_files, commit_count
"""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
from pathlib import Path

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?$"
)
UNIT_SEP = "\x1f"
RECORD_SEP = "\x1e"

SECTIONS = [
    ("breaking", "Breaking Changes"),
    ("features", "Features"),
    ("fixes", "Bug Fixes"),
    ("security", "Security & Hardening"),
    ("perf", "Performance & Refactoring"),
    ("other", "Documentation, CI & Maintenance"),
]


class ReleaseError(Exception):
    pass


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True
    ).stdout


def parse(version: str) -> tuple[int, int, int, str | None] | None:
    m = SEMVER_RE.match(version)
    if not m:
        return None
    return int(m[1]), int(m[2]), int(m[3]), m[4]


def sort_key(version: str):
    major, minor, patch, pre = parse(version)
    # A release sorts after its own pre-releases.
    pre_key: tuple = (1,) if pre is None else (0, *[
        (0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split(".")
    ])
    return (major, minor, patch, pre_key)


def latest_tag() -> str | None:
    tags = [
        t.strip() for t in git("tag", "--list", "v*").splitlines()
        if t.strip().startswith("v") and parse(t.strip()[1:])
    ]
    if not tags:
        return None
    return max(tags, key=lambda t: sort_key(t[1:]))


def next_version(prev: str | None, bump: str, custom: str) -> str:
    if bump == "custom":
        custom = custom.strip().removeprefix("v")
        if not parse(custom):
            raise ReleaseError(
                f"custom_version '{custom}' is not a valid SemVer (expected e.g. 1.0.0)."
            )
        if prev and sort_key(custom) <= sort_key(prev[1:]):
            raise ReleaseError(
                f"custom_version {custom} is not greater than the latest tag {prev}."
            )
        return custom

    major, minor, patch, pre = parse(prev[1:]) if prev else (0, 0, 0, None)
    if bump == "major":
        return f"{major + 1}.0.0" if not (pre and minor == 0 and patch == 0) else f"{major}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0" if not (pre and patch == 0) else f"{major}.{minor}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}" if not pre else f"{major}.{minor}.{patch}"
    if bump == "prerelease":
        if pre:
            parts = pre.split(".")
            if parts[-1].isdigit():
                parts[-1] = str(int(parts[-1]) + 1)
            else:
                parts.append("0")
            return f"{major}.{minor}.{patch}-{'.'.join(parts)}"
        return f"{major}.{minor}.{patch + 1}-rc.0"
    raise ReleaseError(f"Unknown release_bump '{bump}'.")


def read_commits(prev: str | None) -> list[dict]:
    rev_range = f"{prev}..HEAD" if prev else "HEAD"
    raw = git(
        "log", "--no-merges",
        f"--pretty=format:%H{UNIT_SEP}%s{UNIT_SEP}%b{RECORD_SEP}",
        rev_range,
    )
    commits = []
    for record in raw.split(RECORD_SEP):
        record = record.strip("\n")
        if not record:
            continue
        sha, subject, body = (record.split(UNIT_SEP) + ["", ""])[:3]
        # Skip earlier release commits made by this workflow.
        if re.match(r"^chore\(release\):", subject):
            continue
        commits.append({"sha": sha.strip(), "subject": subject.strip(), "body": body.strip()})
    return commits


def categorize(subject: str, body: str) -> str:
    # This repo's older commits start with markers like "[+]"; ignore them.
    s = re.sub(r"^\[[^\]]{1,3}\]\s*", "", subject)
    lower = s.lower()
    if re.match(r"^[a-z]+(\([^)]*\))?!:", lower) or "BREAKING CHANGE" in body:
        return "breaking"
    if re.match(r"^feat(\([^)]*\))?:", lower) or re.match(r"^add(s|ed)?\b", lower):
        return "features"
    if re.match(r"^(fix|hotfix|bug)(\([^)]*\))?:", lower) or re.match(r"^fix(es|ed)?\b", lower):
        return "fixes"
    if re.match(r"^(sec|security)(\([^)]*\))?:", lower) or "security" in lower:
        return "security"
    if re.match(r"^(perf|refactor)(\([^)]*\))?:", lower):
        return "perf"
    return "other"


def render_notes(commits, prev, tag, repo_url) -> str:
    groups: dict[str, list[str]] = {key: [] for key, _ in SECTIONS}
    for c in commits:
        short = c["sha"][:7]
        link = f"[`{short}`]({repo_url}/commit/{c['sha']})" if repo_url else f"`{short}`"
        groups[categorize(c["subject"], c["body"])].append(f"- {c['subject']} ({link})")

    lines = []
    for key, title in SECTIONS:
        if groups[key]:
            lines += [f"### {title}", "", *groups[key], ""]
    if not commits:
        lines += ["_No changes since the previous release._", ""]
    if prev and repo_url:
        lines += [f"**Full diff:** {repo_url}/compare/{prev}...{tag}", ""]
    return "\n".join(lines).rstrip() + "\n"


def sync_manifests(version: str) -> list[str]:
    changed = []
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        new = re.sub(
            r'^(\[project\][\s\S]*?^version\s*=\s*")[^"]+(")',
            rf"\g<1>{version}\g<2>", text, count=1, flags=re.M,
        )
        if new != text:
            pyproject.write_text(new, encoding="utf-8")
            changed.append(str(pyproject))
    version_file = Path("VERSION")
    if version_file.exists():
        version_file.write_text(version + "\n", encoding="utf-8")
        changed.append(str(version_file))
    return changed


def update_changelog(tag: str, notes: str) -> None:
    path = Path("CHANGELOG.md")
    header = "# Changelog\n\nAll notable changes to this project are documented here. This file is updated by the release workflow; do not edit it by hand.\n"
    existing = path.read_text(encoding="utf-8") if path.exists() else header
    if not existing.startswith("# Changelog"):
        existing = header + "\n" + existing
    head, _, rest = existing.partition("\n## ")
    section = f"## {tag} - {dt.date.today().isoformat()}\n\n{notes}"
    body = section + ("\n## " + rest if rest else "")
    path.write_text(head.rstrip() + "\n\n" + body, encoding="utf-8")


def set_output(name: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")
    print(f"{name}={value}")


def main() -> int:
    bump = os.environ.get("RELEASE_BUMP", "patch").strip()
    custom = os.environ.get("CUSTOM_VERSION", "")
    allow_empty = os.environ.get("ALLOW_EMPTY_RELEASE", "false").lower() == "true"
    repo_url = os.environ.get("REPO_URL", "").rstrip("/")
    notes_file = Path(os.environ.get("NOTES_FILE", "release_notes.md"))

    try:
        prev = latest_tag()
        version = next_version(prev, bump, custom)
        tag = f"v{version}"

        if git("tag", "--list", tag).strip():
            raise ReleaseError(f"Tag {tag} already exists. Pick another bump or custom_version.")

        commits = read_commits(prev)
        if not commits and not allow_empty:
            raise ReleaseError(
                f"No new commits since {prev or 'the start of the repo'}. "
                "Merge your PR first, or re-run with allow_empty_release: true."
            )

        notes = render_notes(commits, prev, tag, repo_url)
        notes_file.write_text(notes, encoding="utf-8")
        changed = sync_manifests(version)
        update_changelog(tag, notes)
    except ReleaseError as err:
        print(f"::error title=Release blocked::{err}")
        return 1

    set_output("prev_tag", prev or "")
    set_output("next_version", version)
    set_output("next_tag", tag)
    set_output("changed_files", " ".join(["CHANGELOG.md", *changed]))
    set_output("commit_count", str(len(commits)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
