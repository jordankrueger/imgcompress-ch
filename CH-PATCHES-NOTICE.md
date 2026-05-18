# CH Patches Notice

This is the CampaignHelp fork of **imgcompress-ch** (upstream: https://github.com/karimz1/imgcompress).

## What this branch modifies

The `ch-patches` branch carries CampaignHelp branding and deployment configuration on top of the upstream `main`. Specifically:

- **Branding layer:** `public/ch-branding.css`, `public/ch-header.js`, `public/ch-footer.html`, `public/ch-logo.png` — a thin overlay injected into the upstream HTML. Does not modify upstream business logic.
- **Build config:** `vite.config` adjusted to emit assets under the deployed path prefix (e.g., `/pdf/`, `/image/`).
- **Container build:** `Dockerfile` and `nginx.conf` added/replaced for serving the fork under its prefix path.

## Viewing the diff

```bash
git fetch upstream
git diff upstream/main..ch-patches
```

## Licensing

This branch is provided under the same license as the upstream project. See `LICENSE` in this repo for the canonical text.

## Contact

Issues with the CH fork specifically (not upstream): https://campaign.help/contact

Upstream bug reports and feature requests should go to https://github.com/karimz1/imgcompress.

## Backend privacy patches (imgcompress-ch specific)

Beyond the standard CH branding overlay, this fork adds privacy guarantees consistent with the verifiable commitments on the `/privacy` page at tools.campaign.help:

- **ch_privacy.py** (`backend/image_converter/presentation/web/ch_privacy.py`): per-request UUID-keyed temp directories under `/tmp/imgcompress-uploads/<uuid>/`, automatic cleanup via Flask `teardown_request`, a background sweeper thread purging any directory older than 10 minutes, and `Cache-Control: no-store` on every `/api/*` response.
- **MAX_CONTENT_LENGTH** in `server.py` lowered to 100 MB (upstream is 40 GB).
- **Multi-process container** (supervisord managing nginx + Gunicorn) so the `/image-pro/*` path-prefix routing works with the broader CampaignHelp tools site.
