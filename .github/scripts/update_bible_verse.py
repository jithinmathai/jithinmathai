"""Rotate the Catholic Bible verse displayed at the top of README.md.

Picks one verse at random from `.github/bible-verses.json`
(Douay-Rheims-Challoner translation, public domain) and rewrites
the content between the `<!-- BIBLE-VERSE:START -->` and
`<!-- BIBLE-VERSE:END -->` markers in README.md.

Intended to be run from `.github/workflows/daily-bible-verse.yml`.
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSES_PATH = REPO_ROOT / ".github" / "bible-verses.json"
README_PATH = REPO_ROOT / "README.md"

START_MARKER = "<!-- BIBLE-VERSE:START -->"
END_MARKER = "<!-- BIBLE-VERSE:END -->"


def render_block(verse: dict) -> str:
    """Render the verse as a tasteful centered blockquote."""
    return (
        f"{START_MARKER}\n"
        f"<div align=\"center\">\n\n"
        f"> 📖 *\u201c{verse['text']}\u201d*  \n"
        f"> \u2014 **{verse['reference']}** &nbsp;·&nbsp; "
        f"<sub>*Douay-Rheims-Challoner (Catholic Bible)*</sub>\n\n"
        f"</div>\n"
        f"{END_MARKER}"
    )


def main() -> int:
    if not VERSES_PATH.exists():
        print(f"::error::Verse pool not found at {VERSES_PATH}", file=sys.stderr)
        return 1
    if not README_PATH.exists():
        print(f"::error::README not found at {README_PATH}", file=sys.stderr)
        return 1

    verses = json.loads(VERSES_PATH.read_text(encoding="utf-8"))
    if not verses:
        print("::error::Verse pool is empty", file=sys.stderr)
        return 1

    verse = random.choice(verses)
    new_block = render_block(verse)

    readme = README_PATH.read_text(encoding="utf-8")
    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        flags=re.DOTALL,
    )

    if not pattern.search(readme):
        print(
            f"::error::Could not find the {START_MARKER} \u2026 {END_MARKER} "
            "block in README.md. Add the markers first.",
            file=sys.stderr,
        )
        return 1

    updated = pattern.sub(new_block, readme, count=1)

    if updated == readme:
        print(f"No change \u2014 picked verse was identical to current one ({verse['reference']}).")
        return 0

    README_PATH.write_text(updated, encoding="utf-8")
    print(f"Rotated verse to: {verse['reference']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
