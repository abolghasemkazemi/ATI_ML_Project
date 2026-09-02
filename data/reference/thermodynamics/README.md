# CALPHAD capability registry

This directory inventories thermodynamic capability; it contains **no thermodynamic database** and no calculated scientific values. The 2026-09-02 audit searched the repository and common `/opt` and `/usr/local` locations for case-insensitive `.tdb` files, checked PATH for Thermo-Calc and OpenCALPHAD executables, and checked Python import metadata for `tc_python` and `pycalphad`.

No usable engine/database pair was found (**STATE C**). Commercial licences are not inferred from an installation and are never circumvented. An engine alone does not qualify a database. A future database must have traceable name, version, source/licence, covered elements and phases, and evidence that its assessed multicomponent space supports the requested alloy. Merely finding element declarations and `FCC_A1`/`BCC_A2`/`HCP_A3` names is insufficient.

The CSV uses `NOT_AVAILABLE` rather than fabricated blanks. `LICENSE_REQUIRED` means legitimate commercial entitlement would be required; it does not assert that a licence exists. Update the dated provenance whenever the environment changes.
