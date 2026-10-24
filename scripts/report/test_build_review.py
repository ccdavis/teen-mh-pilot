"""Checks for paper coverage, chunk boundaries, source links and stale outputs."""

import hashlib
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "build_review", Path(__file__).with_name("95_build_review.py")
)
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)

SAMPLE = """<title>Hidden title</title><style>Hidden CSS</style>
<script>Hidden data</script><div class="wrap">
<p>Publication note</p><h1>Paper title</h1><nav>Hidden navigation</nav>
<h2 id="findings">Findings &amp; limits</h2>
<p>Girls’ reported change was <em>−0.5 pp</em>, not zero.
<a href="https://example.org/study?q=one&amp;v=two">Study citation</a>.</p>
<div class="chart" id="fig-test"></div><p class="caption">A chart caption.</p>
<table><thead><tr><th>Sex</th><th>Estimate</th></tr></thead>
<tbody><tr><td>Girls</td><td>−0.5</td></tr><tr><td>Boys</td><td>0.2</td></tr></tbody></table>
<h3>Qualifications</h3><ol><li>First qualification.</li><li>Second qualification.</li></ol>
</div>"""


class ReviewTests(unittest.TestCase):
    def test_conversion_keeps_content_and_removes_chrome(self):
        document = review.read_document(SAMPLE)
        text = review.plain(document["blocks"])
        for hidden in ("Hidden title", "Hidden CSS", "Hidden data", "Hidden navigation"):
            self.assertNotIn(hidden, text)
        for expected in ("Findings & limits", "Girls’ reported change", "−0.5 pp",
                         "Study citation", "A chart caption.", "Girls", "0.2",
                         "First qualification.", "Second qualification."):
            self.assertIn(expected, text)
        self.assertEqual(sum(b["t"] == "Table" for b in document["blocks"]), 1)
        self.assertIn("figures/test.png", json.dumps(document))
        self.assertIn("https://example.org/study?q=one&v=two", json.dumps(document))
        markdown = review.pandoc(json.dumps(document), "json", "gfm")
        round_trip = json.loads(review.pandoc(markdown, "gfm", "json"))
        self.assertEqual(" ".join(text.split()),
                         " ".join(review.plain(round_trip["blocks"]).split()))

    def test_chunks_cover_every_block_in_order_without_cutting_tables(self):
        document = review.read_document(SAMPLE)
        chunks = review.split_document(document, target_words=5)
        self.assertGreater(len(chunks), 3)
        self.assertEqual(
            [block for chunk in chunks for block in chunk["blocks"]],
            document["blocks"],
        )
        table_chunks = [chunk for chunk in chunks if any(b["t"] == "Table" for b in chunk["blocks"])]
        self.assertEqual(len(table_chunks), 1)
        self.assertIn("Girls", review.plain(table_chunks[0]["blocks"]))
        self.assertIn("Boys", review.plain(table_chunks[0]["blocks"]))
        last_context = chunks[-1]["context"]
        self.assertEqual([h["title"] for h in last_context],
                         ["Paper title", "Findings & limits", "Qualifications"])

    def test_manifest_ranges_hashes_and_relative_links(self):
        with patch.object(review, "source_entries", return_value=[
            ("scripts/report/sections/sample.html", SAMPLE)
        ]):
            outputs = review.build_outputs(SAMPLE)
        full = outputs[review.PAPER].splitlines()
        manifest = json.loads(outputs[review.REVIEW / "manifest.json"])
        self.assertEqual(manifest["input_sha256"], hashlib.sha256(SAMPLE.encode()).hexdigest())
        previous_end = 0
        for record in manifest["chunks"]:
            start, end = record["paper_lines"]
            self.assertGreater(start, previous_end)
            previous_end = end
            body = "\n".join(full[start - 1:end]) + "\n"
            self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), record["paper_content_sha256"])
            chunk = outputs[review.REVIEW / record["file"]]
            self.assertEqual(hashlib.sha256(chunk.encode()).hexdigest(), record["sha256"])
            self.assertIn(f'#review-{record["id"]}', chunk)
            self.assertTrue(record["sources"])
        all_chunks = "\n".join(text for path, text in outputs.items() if path.parent.name == "chunks")
        self.assertIn("../../figures/test.png", all_chunks)
        self.assertIn("../Teen_Distress_Pilot.md", outputs[review.REVIEW / "README.md"])

    def test_check_detects_stale_content_and_prunes_only_obsolete_chunks(self):
        with tempfile.TemporaryDirectory() as directory, \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            root = Path(directory)
            (root / "build").mkdir()
            (root / "build/report.html").write_text(SAMPLE, encoding="utf-8")
            docs = root / "docs"
            target = docs / "review"
            with patch.multiple(review, ROOT=root, DOCS=docs, REVIEW=target,
                                PAPER=docs / "Teen_Distress_Pilot.md"), \
                    patch.object(review, "source_entries", return_value=[]) as source_entries, \
                    patch("sys.argv", ["95_build_review.py"]):
                review.main()
                obsolete = target / "chunks/obsolete.md"
                obsolete.write_text("old chunk")
                unrelated = target / "editor-notes.txt"
                unrelated.write_text("keep these notes")
                with patch("sys.argv", ["95_build_review.py", "--check"]):
                    with self.assertRaises(SystemExit) as error:
                        review.main()
                    self.assertEqual(error.exception.code, 1)
                review.main()
                self.assertFalse(obsolete.exists())
                self.assertEqual(unrelated.read_text(), "keep these notes")
                with patch("sys.argv", ["95_build_review.py", "--check"]):
                    review.main()
                    source_entries.return_value = [("scripts/report/90_build_report.py", "changed source")]
                    with self.assertRaises(SystemExit) as error:
                        review.main()
                    self.assertEqual(error.exception.code, 1)
                    source_entries.return_value = []
                review.PAPER.write_text("edited generated output")
                with patch("sys.argv", ["95_build_review.py", "--check"]):
                    with self.assertRaises(SystemExit) as error:
                        review.main()
                    self.assertEqual(error.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
