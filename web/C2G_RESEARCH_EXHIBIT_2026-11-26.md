# C2G research exhibit — 26 November 2026

Source revision: `2439de4e8e271d111ccb1f0bcda4c3be0929dccd` (atlas-web-preview). Canonical C2G revision: `b418b4c8ed95fb63163c11636d6dec11e0c85ffc`.

The revised exhibit links Paper 1 v11 (33 pages), Paper 2 v1.2 (21 pages), Paper 3 v0.5 (19 pages), the H100 laboratory, matrix pilot, source and review records. The thumbnail is a real PDP-8 photograph with attribution and original SHA-1; new SVGs explain reciprocal inquiry and dependency-sensitive failure. Earlier paper figures retain their actual historical version labels.

Deploy from a terminal on the Atlas server with `bash web/deploy-c2g-research.sh` as root, or download the pinned script from the repository. The script stages the exact four HTML pages and assets, verifies all three latest manuscript hashes, backs up the affected files, and verifies the public site's served bytes. A deployment or verification failure restores the previous affected files. The site generator now preserves the home, exhibit and inventory references. The dedicated research exhibit remains a maintained static page. Its photograph and historical figure crops are reconstructed by the deployment script.

This is a website/source revision, not scientific validation. Actual H100 testing and independent review remain outstanding. Live deployment has not yet been confirmed. The script requires curl, standard GNU utilities and Poppler (pdftoppm).
