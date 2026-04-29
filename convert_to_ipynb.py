"""
Converts dental_site_analysis.Rmd → dental_site_analysis.ipynb
Produces a Jupyter notebook with R kernel ready for Kaggle upload.
"""

import json, re, hashlib, sys

RMD  = "/Users/danielona/Documents/dental_site_analysis.Rmd"
OUT  = "/Users/danielona/Documents/dental_site_analysis.ipynb"

# ── helpers ──────────────────────────────────────────────────────────────────

def uid(text):
    return hashlib.md5(text.encode()).hexdigest()[:8]

def md_cell(source):
    source = source.strip()
    if not source:
        return None
    lines = source.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return {
        "cell_type": "markdown",
        "id": uid(source),
        "metadata": {},
        "source": lines
    }

def code_cell(source):
    source = source.strip()
    if not source:
        return None
    lines = source.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": uid(source),
        "metadata": {},
        "outputs": [],
        "source": lines
    }

# ── parse .Rmd ────────────────────────────────────────────────────────────────

with open(RMD, encoding="utf-8") as f:
    raw = f.read()

# Strip YAML front matter (between first and second ---)
raw = re.sub(r"^---\n.*?---\n", "", raw, count=1, flags=re.DOTALL).strip()

# Split on code fence openings  ```{r ...}
FENCE_OPEN  = re.compile(r"```\{r[^}]*\}\n")
FENCE_CLOSE = "```"

cells = []
pos   = 0

for m in FENCE_OPEN.finditer(raw):
    # markdown before this chunk
    before = raw[pos:m.start()]
    c = md_cell(before)
    if c:
        cells.append(c)

    # find closing fence
    code_start = m.end()
    close_pos  = raw.find(FENCE_CLOSE, code_start)
    if close_pos == -1:
        break
    code_src = raw[code_start:close_pos]
    c = code_cell(code_src)
    if c:
        cells.append(c)

    pos = close_pos + len(FENCE_CLOSE)

# remaining markdown after last chunk
tail = raw[pos:]
c = md_cell(tail)
if c:
    cells.append(c)

# ── assemble notebook ─────────────────────────────────────────────────────────

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "R",
            "language": "R",
            "name": "ir"
        },
        "language_info": {
            "codemirror_mode": "r",
            "file_extension": ".r",
            "mimetype": "text/x-r-source",
            "name": "R",
            "pygments_lexer": "r",
            "version": "4.3.3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print(f"Done — {len(cells)} cells written to:")
print(f"  {OUT}")
code_cells = sum(1 for c in cells if c["cell_type"] == "code")
md_cells   = sum(1 for c in cells if c["cell_type"] == "markdown")
print(f"  {md_cells} markdown cells  |  {code_cells} code cells")
