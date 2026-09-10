# Elementor Pro Upload Checker

Discovery crawler and optional non-executing upload test for CVE-2026-32475. Discovery is the default. Finding an upload form or an asset version is not proof that a site is vulnerable.

The [Wordfence advisory](https://www.wordfence.com/blog/2026/09/attackers-actively-exploiting-critical-vulnerability-in-elementor-pro-plugin/) identifies Elementor Pro through 4.2.1 as affected and 4.2.2 as patched. Updating is preferable to relying on a negative test.

## Install

Requires Python 3.9 or newer:

```sh
python -m pip install -r requirements.txt
```

## Discover forms

```sh
python cve_2026_32475_crawl_probe.py --site https://example.com/ --discover --max-pages 50 --delay 1
```

Replace the example with your authorized site. This requests pages and sitemaps but does not submit forms. The boundary is the exact scheme, hostname, and effective port, checked before requests and each redirect. Redirects to a www hostname, another port, or another scheme are blocked; specify the canonical origin initially.

## Optional upload test

```sh
python cve_2026_32475_crawl_probe.py --site https://example.com/ --probe --max-pages 50 --delay 1
```

**Probe mode submits real forms.** It can trigger email, integrations, or submissions and leave non-executing marker files on the server. Use a staging copy where possible. The test does not upload PHP or execute server commands.

- Control and probe files contain different random markers.
- No automatic redirect replay for submitted forms.
- Required values can be supplied using repeated `--field FIELD_ID=value`.
- `--wp-root /path/to/wordpress` checks a local or mounted upload directory for exact marker contents.
- `--cleanup` requires `--wp-root` and removes only matching marker files after checking their contents again. Otherwise remove test artifacts manually.
- TLS verification is on by default. The original `--insecure` option remains available for controlled environments.

## Results

- **vulnerable:** rejected control plus exact probe marker on disk, without a control marker.
- **likely:** rejected control and an explicit successful application response for the probe; file storage remains unconfirmed.
- **not_reproduced:** both requests show file-type rejection. This does not certify the site is safe.
- **inconclusive:** server errors, challenges, ambiguous results, or an accepted control.
- **skipped/error:** conditions were unsuitable or a request failed.

## Remaining limitations

- No JavaScript rendering or authenticated crawling.
- Requires the optional + multiple upload configuration to select a test candidate; other configurations are not ruled out.
- Assumes WordPress AJAX is at the origin's /wp-admin/admin-ajax.php; subdirectory installations require adaptation.
- Uses English response-message heuristics and does not guarantee comprehensive CAPTCHA detection.
- Sitemaps have a separate 100-file cap; page limits do not bound total response size or sitemap URL memory.
- Asset versions can be stale or absent.
- Requests may trigger application behavior even when the script only performs GET discovery.
- Marker cleanup is not a defense against concurrent hostile filesystem changes.

## Validation

Python syntax and offline regression checks passed for origin boundaries, off-origin redirects, ambiguous response classification, separate control/probe outcomes, and exact marker matching. Tests used a mocked HTTP transport and temporary local files. No website was crawled or probed, and the full network workflow has not been integration-tested.
