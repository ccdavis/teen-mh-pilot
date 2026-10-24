"""Export the assembled paper as Markdown and indexed, source-linked review chunks.

Requires pandoc, but no browser or raw data. The Python/HTML report sources remain
authoritative; see docs/review/README.md for the copy-edit and rebuild workflow.
"""

import argparse
import copy
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import unicodedata


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
REVIEW = DOCS / "review"
PAPER = DOCS / "Teen_Distress_Pilot.md"
TARGET_WORDS = 1200


def pandoc(text, reader, writer):
    return subprocess.run(
        ["pandoc", "--from", reader, "--to", writer, "--wrap=none"],
        input=text, text=True, encoding="utf-8", capture_output=True, check=True,
    ).stdout


def plain(value):
    """Readable AST text, excluding link destinations and formatting metadata."""
    if isinstance(value, list):
        return "".join(plain(item) for item in value)
    if not isinstance(value, dict):
        return ""
    kind, content = value.get("t"), value.get("c")
    if kind == "Str":
        return content
    if kind in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if kind in ("Code", "Math"):
        return content[-1]
    if kind in ("Link", "Image"):
        return plain(content[1])
    if kind == "Header":
        return plain(content[2])
    if kind in ("Span", "Quoted"):
        return plain(content[1])
    return plain(content) + (" " if kind in ("Plain", "Para") else "")


def normalize(text):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", "", text)).split())


def slug(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")[:80].rstrip("-") or "introduction"


def source_entries():
    paths = [ROOT / "scripts/report/90_build_report.py"]
    paths.extend(sorted((ROOT / "scripts/report/sections").glob("*.html")))
    return [(p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")) for p in paths]


def locate_sources(blocks, entries):
    """Find heading and opening-prose entry points in editable templates."""
    found = set()
    for block in blocks:
        if block["t"] not in ("Header", "Para", "Plain"):
            continue
        probe = normalize(plain(block))[:100]
        if len(probe) < 12:
            continue
        for path, text in entries:
            for number, line in enumerate(text.splitlines(), 1):
                if probe in normalize(line):
                    found.add((path, number))
                    break
    if not found:
        found.add(("scripts/report/90_build_report.py", 1))
    return [{"path": path, "line": line} for path, line in sorted(found)]


def read_document(source):
    # Remove presentation chrome. Preserve all prose, captions, tables and links.
    cleaned = re.sub(r"<(script|style|nav|title)\b[^>]*>.*?</\1\s*>", "", source, flags=re.S | re.I)
    figure_ids = []

    def figure(match):
        key = match[1]
        figure_ids.append(key)
        return f'<p><img src="figures/{key}.png" alt="Chart: {key}" /></p>'

    cleaned = re.sub(r'<div class="chart" id="fig-([a-z_0-9]+)"></div>', figure, cleaned)
    document = json.loads(pandoc(cleaned, "html-native_divs-native_spans", "json"))
    document["meta"] = {}
    # A silent chart loss would make the review edition incomplete.
    if source.count('class="chart"') != len(figure_ids):
        raise ValueError("Unrecognized chart markup; update the review exporter")
    return document


def split_document(document, target_words=TARGET_WORDS):
    """Split at headings and block boundaries; never cut a table/list/paragraph."""
    chunks, blocks, context = [], [], []
    current_context, words = [], 0

    def flush():
        nonlocal blocks, words
        if blocks:
            chunks.append({"context": current_context[:], "blocks": blocks})
        blocks, words = [], 0

    for block in document["blocks"]:
        if block["t"] == "Header":
            level, attr, _ = block["c"]
            context = [heading for heading in context if heading["level"] < level]
            context.append({"level": level, "title": plain(block), "anchor": attr[0]})
            if level <= 3:
                flush()
        count = len(plain(block).split())
        if blocks and words + count > target_words:
            flush()
        if not blocks:
            current_context = context[:]
        blocks.append(block)
        words += count
    flush()
    # Exact ordered coverage, including blocks preceding the first heading.
    assert [b for chunk in chunks for b in chunk["blocks"]] == document["blocks"]
    return chunks


def source_link(entry, base):
    path = os.path.relpath(ROOT / entry["path"], base)
    return f'[{entry["path"]}:{entry["line"]}]({path}#L{entry["line"]})'


def build_outputs(source):
    document = read_document(source)
    chunks = split_document(document)
    entries = source_entries()
    outputs, records, used_ids = {}, [], {}
    full = "<!-- Generated by scripts/report/95_build_review.py; edit the linked Python/HTML sources. -->\n\n"
    full += "[Review index and editing instructions](review/README.md)\n\n"
    for number, chunk in enumerate(chunks, 1):
        context = chunk["context"]
        heading = context[-1] if context else {"title": "Publication note", "anchor": "publication-note"}
        base_id = slug(heading["anchor"] or heading["title"])
        used_ids[base_id] = used_ids.get(base_id, 0) + 1
        chunk_id = base_id + (f'-{used_ids[base_id]}' if used_ids[base_id] > 1 else "")
        ast = {**document, "blocks": chunk["blocks"]}
        markdown = pandoc(json.dumps(ast), "json", "gfm").strip() + "\n"
        sources = locate_sources(chunk["blocks"], entries)
        filename = f"chunks/{chunk_id}.md"
        full += f'<a id="review-{chunk_id}"></a>\n\n'
        start = len(full.splitlines()) + 1
        full += markdown + "\n"
        end = start + len(markdown.splitlines()) - 1
        record = {
            "id": chunk_id, "order": number, "title": heading["title"],
            "context": [h["title"] for h in context], "file": filename,
            "words": len(plain(chunk["blocks"]).split()),
            "paper_lines": [start, end], "sources": sources,
            "paper_content_sha256": hashlib.sha256(markdown.encode()).hexdigest(),
        }
        records.append(record)
        # Fix image and local-link paths for the deeper chunk directory via AST.
        local_ast = copy.deepcopy(ast)

        def adjust_links(node):
            if isinstance(node, list):
                for item in node:
                    adjust_links(item)
            elif isinstance(node, dict):
                if node.get("t") in ("Image", "Link"):
                    target = node["c"][2][0]
                    if target and not re.match(r"[a-zA-Z][\w+.-]*:|/|#", target):
                        node["c"][2][0] = "../../" + target
                for value in node.values():
                    adjust_links(value)

        adjust_links(local_ast)
        local_markdown = pandoc(json.dumps(local_ast), "json", "gfm").strip() + "\n"
        entry_points = {}
        for entry in sources:
            entry_points.setdefault(entry["path"], entry)
        outputs[REVIEW / filename] = (
            f'<!-- Generated review chunk: {chunk_id} -->\n\n'
            f'[Index](../README.md) · [Full paper](../../{PAPER.name}#review-{chunk_id})\n\n'
            f'Context: {" → ".join(record["context"]) or "Publication note"}\n\n'
            'Editable source entry points: ' + ", ".join(source_link(s, REVIEW / "chunks") for s in entry_points.values()) + "\n\n"
            "---\n\n" + local_markdown
        )
        record["sha256"] = hashlib.sha256(outputs[REVIEW / filename].encode()).hexdigest()

    outputs[PAPER] = full
    manifest = {
        "schema_version": 1, "input": "build/report.html",
        "input_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "source_sha256": {path: hashlib.sha256(text.encode()).hexdigest() for path, text in entries},
        "paper": "../" + PAPER.name,
        "paper_sha256": hashlib.sha256(full.encode()).hexdigest(),
        "target_words": TARGET_WORDS,
        "chunks": records,
    }
    outputs[REVIEW / "manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    index = """# Paper review index

This is a generated review edition of the complete assembled paper, including
tables, captions, citations and links to static chart images. Start here to select
chunks, or read the [complete Markdown paper](../Teen_Distress_Pilot.md).

## Copy-edit and regenerate

1. Read the relevant chunks and their neighboring sections. Each chunk gives its
   heading context, a link to the full paper, and editable source entry points.
2. Record suggested edits using the chunk ID, an exact quotation, the replacement,
   and a reason. Check repeated claims against the summary and conclusion. Open
   the linked chart images when reviewing claims about figures; the images are
   not transcribed into Markdown.
3. Apply accepted prose edits to `scripts/report/90_build_report.py` or the
   hand-written HTML in `scripts/report/sections/`. Source links are entry points;
   locate the quoted text there. Preserve Python interpolation and HTML markup.
   Numerical tables come from `results/tables/`; correct their producing analysis
   if a computed result must change.
4. From the repository root, run `bash scripts/report/rebuild.sh`. This rebuilds
   the HTML, PDF, Word, complete Markdown, chunks and this index together. It uses
   the committed result tables and does not rerun microdata analysis.
5. Review the source and generated diffs, then repeat the review as needed.

Edit the Python/HTML sources, rather than these generated Markdown files:
Markdown edits are overwritten on regeneration. The source links identify the
templates used by all editions, so accepted copy edits persist in every format.

## Faster text review

To rebuild HTML and Markdown during editing without rendering print editions:

```sh
bash scripts/report/rebuild.sh --review-only
```

PDF, Word and chart images are refreshed by the full rebuild. For an already
assembled `build/report.html`, export only the review edition with
`uv run python scripts/report/95_build_review.py`. Check that its outputs match
the assembled HTML and source fingerprints without writing files with
`uv run python scripts/report/95_build_review.py --check`.

## Chunk index

Chunks follow document order, split at major headings and then at block boundaries
near 1,200 words. Tables, lists and paragraphs remain intact and can exceed that
target. Heading-based IDs remain stable across prose edits; continuation chunks
get numeric suffixes. Context headings in chunk metadata are not extra paper text.
The [JSON manifest](manifest.json) records order, context, word counts, full-paper
line ranges, source locations and SHA-256 fingerprints. Line ranges refer to the
complete Markdown file; its paper content covers every parsed block exactly once.

| Order | Chunk | Words | Full-paper lines |
| --- | --- | ---: | --- |
"""
    for record in records:
        start, end = record["paper_lines"]
        index += f'| {record["order"]} | [{record["title"]}]({record["file"]}) | {record["words"]} | {start}–{end} |\n'
    outputs[REVIEW / "README.md"] = index
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if review outputs are missing or stale")
    args = parser.parse_args()
    source = (ROOT / "build/report.html").read_text(encoding="utf-8")
    outputs = build_outputs(source)
    stale = sorted(set((REVIEW / "chunks").glob("*.md")) - set(outputs))
    changed = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
    if args.check:
        if changed or stale:
            parser.exit(1, "Review outputs are stale; rebuild them:\n" + "".join(f"  {p.relative_to(ROOT)}\n" for p in changed + stale))
        print("Review outputs match the assembled paper and source fingerprints.")
        return
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for path in stale:
        path.unlink()
    print(f"Wrote {PAPER.relative_to(ROOT)} and {len(outputs) - 3} review chunks, index and manifest.")


if __name__ == "__main__":
    main()
