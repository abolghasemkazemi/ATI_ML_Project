# Raw paper storage

This directory is the immutable landing area for source papers admitted to the
general HEA pilot. The pilot infrastructure is intentionally empty: no paper
was downloaded or added when it was created. Register a paper in
`data/manifests/paper_manifest.csv` before placing a locally and lawfully
obtained source file here. Do not commit copyright-bearing PDFs; `.gitignore`
excludes `data/raw/papers/*.pdf`.

The existing `paper_manifest.csv` in this directory is a historical recovery
manifest for the earlier P001--P019 workflow. It is preserved for provenance
and is not the intake manifest for the new pilot.

After copying PDFs, run:

```bash
python scripts/prepare_pdf_recovery.py --verify-pdfs
```

The legacy check compares PDF metadata only where safely available and otherwise
leaves verification fields pending for manual review. A file's presence is not
evidence that its DOI or title matches. Do not enter recovered scientific values
until a page/figure/table/section location and extraction method have been
recorded.

Raw files are immutable after registration. Corrections belong in a new,
versioned extraction artifact and its correction/decision record, never in the
source file.
