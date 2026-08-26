# Local source-paper storage

Place the 19 source PDFs in this directory using the filenames in
`paper_manifest.csv` (for example, `P001.pdf`). PDF files are copyright-bearing
review inputs and **must not be committed to Git**; `.gitignore` excludes every
`data/raw/papers/*.pdf` file.

After copying PDFs, run:

```bash
python scripts/prepare_pdf_recovery.py --verify-pdfs
```

The check compares PDF metadata only where safely available and otherwise leaves
verification fields pending for manual review. A file's presence is not evidence
that its DOI or title matches. Do not enter recovered scientific values until a
page/figure/table/section location and extraction method have been recorded.
