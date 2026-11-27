# C2G portal 1.2 — synchronized link audit
27 November 2026. Portal v1.0 remains in Git history. Visual revision 016e8cd2998b5fcbd30bdced6d1c39d0fcf8b743 provides distinct original SVG covers for both catalase exhibits and synchronizes their landing pages, the C2G portal and the gallery. The illustrations are conceptual, not atomic structure data or bench photographs. The lab PDFs and original v1.1 ZIP are unchanged.

## Install on Atlas Ubuntu
```bash
work=$(mktemp -d)
git clone --depth 1 --single-branch --branch atlas-web-preview https://github.com/RandoSY/project-atlas.git "$work/repo" && sudo python3 "$work/repo/web/deploy-c2g-portal.py"
```
Default site /var/www/html/atlas. Override --site and --url if necessary. Checks the installed lab archive and all seven members against their recorded SHA-256 hashes before modifying anything. Updates six assets and four pages; merges only the three relevant gallery cards, backs up files and checks live bytes. Rolls back on failure. Distinct versioned cover names avoid cached old graphics. Success message: C2G PORTAL v1.2 DEPLOYED. Production execution and browser inspection remain pending.

## Link audit — v1.2
All internal C2G GitHub paths were checked against the complete main tree; newer nonempty v12, v1.3 and v0.6 review PDFs are linked separately from verified/documented editions. Their content was not inspected. Current Paper 2 is peroxide management v0.1 Markdown. Source links point to atlas-web-preview, not main. Original lab release unchanged. Publication inventory and root README updated in C2G commit b8819c184177a939b9599c0b9de7b60caa08e0bd.
