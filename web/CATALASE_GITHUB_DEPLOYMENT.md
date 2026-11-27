# Catalase Open Lab v1.1 — revised Git deployment
27 November 2026. Replaces raw-URL installation as the preferred route after a reported HTTP 404. The exact lab archive remains SHA-256 e2e0173c913f814d196a4c622f1ff1c8f0f8d471bb3c295bd0817e76537de84f. The supplied Windows publisher package includes the original archive, the standalone Open Lab exhibit, its installer and a checksum manifest. It publishes only four files under `web/releases/catalase-open-lab/v1.1/` on this branch, refuses differing existing files, and fetches the resulting remote commit to verify exact bytes. No forced push. The binary release is not yet present merely because this document is committed.

## Server installation (after publisher prints VERIFIED REMOTE RELEASE)
```bash
work=$(mktemp -d)
git clone --depth 1 --single-branch --branch atlas-web-preview https://github.com/RandoSY/project-atlas.git "$work/repo" && (
  cd "$work/repo/web/releases/catalase-open-lab/v1.1" &&
  sha256sum -c SHA256SUMS.txt &&
  python3 install.py
)
```
Default site directory /var/www/html/atlas; override ATLAS_SITE if necessary. The installer preserves unrelated gallery entries and existing research exhibit, backs up affected files and verifies local bytes. Public URL: https://project-atlas-lab.duckdns.org/atlas/catalase-fem/open-lab/. Verify actual served archive with curl and sha256sum. Public GitHub and live server access are not confirmed in the assistant environment. The publisher passed a local bare-Git push/fetch test and repeat execution, and the release installer passed two local installations preserving an existing gallery entry. No live deployment or bench experiment is asserted.