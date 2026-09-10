#!/usr/bin/env python3
import argparse
import collections
import json
import posixpath
import re
import secrets
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import (
    urljoin,
    urlsplit,
    urlunsplit,
    parse_qsl,
    urlencode,
)

import requests
from bs4 import BeautifulSoup

UA = "CVE-2026-32475-safe-crawler/2.0 (authorized security validation)"
BLOCKED_TEST_EXTENSION = "html"

SKIP_PATH_PREFIXES = (
    "/wp-admin",
    "/wp-login",
    "/wp-json",
    "/xmlrpc.php",
    "/feed",
)

SKIP_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico",
    ".pdf", ".zip", ".gz", ".rar", ".7z",
    ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".mov",
    ".css", ".js", ".map",
    ".woff", ".woff2", ".ttf", ".eot",
    ".xml", ".txt",
}

TRACKING_KEYS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_cid", "mc_eid",
}


def origin_key(url):
    p = urlsplit(url)
    if p.scheme not in ("http", "https") or not p.hostname or p.username or p.password:
        raise ValueError("Expected an HTTP(S) URL without credentials")
    return (p.scheme.lower(), p.hostname.lower(), p.port or (443 if p.scheme == "https" else 80))


class ScopedSession(requests.Session):
    """Check every request and redirect before any network contact."""
    def __init__(self, site):
        super().__init__()
        self.allowed_origin = origin_key(site)
        self.trust_env = False

    def request(self, method, url, **kwargs):
        redirects = kwargs.pop("allow_redirects", True)
        for _ in range(11):
            try:
                permitted = origin_key(url) == self.allowed_origin
            except ValueError:
                permitted = False
            if not permitted:
                raise requests.RequestException("Blocked URL outside the selected origin")
            response = super().request(method, url, allow_redirects=False, **kwargs)
            if not redirects or not response.is_redirect:
                return response
            # Never replay form uploads automatically.
            if method.upper() not in ("GET", "HEAD"):
                return response
            next_url = urljoin(url, response.headers["Location"])
            response.close()
            url = next_url
            kwargs.pop("params", None)
        raise requests.TooManyRedirects("Too many redirects")


def response_verdict(control, probe, control_hits=False, probe_hits=False):
    if control_hits:
        return "inconclusive"
    valid = (
        control["status"] == 200 and probe["status"] == 200
        and control["success"] is False
        and has_filetype_rejection(control)
    )
    if not valid:
        return "inconclusive"
    if probe_hits:
        return "vulnerable"
    if probe["success"] is True and not probe["errors"]:
        return "likely"
    if probe["success"] is False and has_filetype_rejection(probe):
        return "not_reproduced"
    return "inconclusive"


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def parse_field_overrides(items):
    out = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"Invalid --field value {item!r}; expected FIELD_ID=value")
        k, v = item.split("=", 1)
        k = k.strip()
        if not k:
            raise SystemExit("Field ID cannot be empty")
        out[k] = v
    return out

def field_id_from_name(name):
    if not name:
        return None
    m = re.search(r"form_fields\[([^\]]+)\]", name)
    return m.group(1) if m else None

def detect_elementor_pro_version(html):
    pats = [
        r"/wp-content/plugins/elementor-pro/[^\"']*[?&]ver=([0-9]+(?:\.[0-9]+){1,3})",
        r"elementor-pro[^\"']*[?&]ver=([0-9]+(?:\.[0-9]+){1,3})",
    ]
    for pat in pats:
        m = re.search(pat, html, re.I)
        if m:
            return m.group(1)
    return None

def normalize_url(url, origin):
    try:
        p = urlsplit(url)
    except Exception:
        return None

    if p.scheme not in ("http", "https"):
        return None

    o = urlsplit(origin)
    if origin_key(url) != origin_key(origin):
        return None

    path = p.path or "/"
    path = posixpath.normpath(path)
    if not path.startswith("/"):
        path = "/" + path
    if p.path.endswith("/") and not path.endswith("/"):
        path += "/"

    low = path.lower()
    if any(low.startswith(prefix) for prefix in SKIP_PATH_PREFIXES):
        return None

    suffix = Path(path).suffix.lower()
    if suffix in SKIP_EXTENSIONS:
        return None

    q = []
    for k, v in parse_qsl(p.query, keep_blank_values=True):
        if k.lower() not in TRACKING_KEYS:
            q.append((k, v))

                                              
    if len(q) > 4:
        q = q[:4]

    return urlunsplit((p.scheme, p.netloc, path, urlencode(q), ""))

def extract_same_origin_links(html, base_url, origin):
    soup = BeautifulSoup(html, "html.parser")
    out = set()

    for a in soup.find_all("a", href=True):
        raw = a.get("href", "").strip()
        if not raw:
            continue
        if raw.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        absolute = urljoin(base_url, raw)
        normalized = normalize_url(absolute, origin)
        if normalized:
            out.add(normalized)

    return out

def parse_sitemap_xml(xml_text, base_url, origin):
    page_urls = set()
    sitemap_urls = set()

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return page_urls, sitemap_urls

    root_tag = root.tag.lower()

    for loc in root.iter():
        if not loc.tag.lower().endswith("loc"):
            continue
        if not loc.text:
            continue

        raw = loc.text.strip()
        if not raw:
            continue

        absolute = urljoin(base_url, raw)

        if root_tag.endswith("sitemapindex"):
            p = urlsplit(absolute)
            o = urlsplit(origin)
            if p.netloc.lower() == o.netloc.lower():
                sitemap_urls.add(absolute)
        else:
            normalized = normalize_url(absolute, origin)
            if normalized:
                page_urls.add(normalized)

    return page_urls, sitemap_urls

def discover_sitemap_urls(session, site):
    origin = f"{urlsplit(site).scheme}://{urlsplit(site).netloc}"
    candidates = {
        urljoin(origin + "/", "wp-sitemap.xml"),
        urljoin(origin + "/", "sitemap_index.xml"),
        urljoin(origin + "/", "sitemap.xml"),
    }

    try:
        r = session.get(urljoin(origin + "/", "robots.txt"), timeout=15)
        if r.ok:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    u = line.split(":", 1)[1].strip()
                    if u:
                        candidates.add(u)
    except requests.RequestException:
        pass

    return candidates

def crawl_sitemaps(session, site, max_sitemaps=100):
    origin = f"{urlsplit(site).scheme}://{urlsplit(site).netloc}"
    todo = collections.deque(discover_sitemap_urls(session, site))
    seen = set()
    pages = set()

    while todo and len(seen) < max_sitemaps:
        sm = todo.popleft()
        if sm in seen:
            continue
        seen.add(sm)

        try:
            r = session.get(sm, timeout=20, allow_redirects=True)
        except requests.RequestException:
            continue

        ctype = r.headers.get("content-type", "").lower()
        if not r.ok:
            continue
        if "xml" not in ctype and not r.text.lstrip().startswith("<?xml"):
            continue

        page_urls, sitemap_urls = parse_sitemap_xml(r.text, r.url, origin)
        pages.update(page_urls)

        for child in sitemap_urls:
            if child not in seen:
                todo.append(child)

    return pages, seen

def find_elementor_upload_forms(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for idx, form in enumerate(soup.find_all("form"), start=1):
        file_inputs = form.find_all("input", {"type": re.compile(r"^file$", re.I)})
        if not file_inputs:
            continue

        hidden = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            if name:
                hidden[name] = inp.get("value", "")

        form_id = hidden.get("form_id")
        post_id = hidden.get("post_id")

                                          
        form_classes = " ".join(form.get("class", []))
        form_id_attr = form.get("id", "")
        form_html = str(form)[:10000].lower()

        is_elementor = (
            bool(form_id and post_id)
            or "elementor" in form_classes.lower()
            or "elementor" in form_id_attr.lower()
            or "elementor" in form_html
        )
        if not is_elementor:
            continue

        uploads = []
        for inp in file_inputs:
            name = inp.get("name", "")
            fid = field_id_from_name(name)

                                                              
            if not fid:
                continue

            uploads.append({
                "id": fid,
                "name": name,
                "required": inp.has_attr("required") or inp.get("aria-required") == "true",
                "multiple": inp.has_attr("multiple") or name.endswith("[]"),
                "accept": inp.get("accept"),
            })

        if not uploads:
            continue

        results.append({
            "page": page_url,
            "index": idx,
            "form_id": form_id,
            "post_id": post_id,
            "uploads": uploads,
            "form_tag": form,
        })

    return results

def discover_required_fields(form_tag, upload_id, overrides):
    data = {}
    unresolved = []
    captcha_like = []

    def add_field(fid, value):
        if fid and fid != upload_id:
            data[f"form_fields[{fid}]"] = value

    for inp in form_tag.find_all("input"):
        typ = (inp.get("type") or "text").lower()
        name = inp.get("name")
        if not name or typ == "file":
            continue

        fid = field_id_from_name(name)
        if not fid:
            continue

        if fid in overrides:
            add_field(fid, overrides[fid])
            continue

        if typ == "hidden":
            add_field(fid, inp.get("value", ""))
            continue

        required = inp.has_attr("required") or inp.get("aria-required") == "true"
        if not required:
            continue

        low = (
            fid + " "
            + (" ".join(inp.get("class")) if inp.get("class") else "")
        ).lower()

        if "captcha" in low or "recaptcha" in low or "hcaptcha" in low:
            captcha_like.append(fid)
            continue

        if typ == "email":
            value = "authorized-probe@example.com"
        elif typ in ("tel", "number"):
            value = "1"
        elif typ == "url":
            value = "https://example.com/"
        elif typ in ("checkbox", "radio"):
            value = inp.get("value", "1")
        else:
            value = "Authorized security test"

        add_field(fid, value)

    for ta in form_tag.find_all("textarea"):
        name = ta.get("name")
        fid = field_id_from_name(name)
        if not fid or fid == upload_id:
            continue
        if fid in overrides:
            add_field(fid, overrides[fid])
        elif ta.has_attr("required") or ta.get("aria-required") == "true":
            add_field(fid, "Authorized security test")

    for sel in form_tag.find_all("select"):
        name = sel.get("name")
        fid = field_id_from_name(name)
        if not fid or fid == upload_id:
            continue

        if fid in overrides:
            add_field(fid, overrides[fid])
            continue

        if sel.has_attr("required") or sel.get("aria-required") == "true":
            selected = sel.find("option", selected=True)
            if selected and selected.get("value"):
                add_field(fid, selected.get("value"))
                continue

            for opt in sel.find_all("option"):
                if opt.get("value"):
                    add_field(fid, opt.get("value"))
                    break
            else:
                unresolved.append(fid)

    for fid, value in overrides.items():
        if fid != upload_id:
            add_field(fid, value)

    return data, unresolved, captcha_like

def build_base_data(form_record, upload_id, overrides):
    form_tag = form_record["form_tag"]
    required_data, unresolved, captcha_like = discover_required_fields(
        form_tag, upload_id, overrides
    )

    base_data = {}

                                               
    for inp in form_tag.find_all("input"):
        typ = (inp.get("type") or "text").lower()
        name = inp.get("name")
        if (
            name
            and typ == "hidden"
            and not field_id_from_name(name)
        ):
            base_data[name] = inp.get("value", "")

    base_data.update({
        "action": "elementor_pro_forms_send_form",
        "post_id": str(form_record["post_id"] or ""),
        "form_id": str(form_record["form_id"] or ""),
        "queried_id": str(form_record["post_id"] or ""),
        "referer_title": "Authorized CVE-2026-32475 validation",
    })
    base_data.update(required_data)

    return base_data, unresolved, captcha_like

def classify_response(resp):
    body = resp.text
    result = {
        "status": resp.status_code,
        "success": None,
        "message": "",
        "errors": {},
        "raw_prefix": body[:500],
    }

    try:
        j = resp.json()
        result["success"] = j.get("success")
        data = j.get("data")
        if isinstance(data, dict):
            result["message"] = str(data.get("message", ""))
            errors = data.get("errors")
            if isinstance(errors, dict):
                result["errors"] = errors
    except Exception:
        pass

    return result

def has_filetype_rejection(info):
    blob = json.dumps(info, ensure_ascii=False).lower()
    needles = [
        "file type",
        "not allowed",
        "invalid file",
        "extension",
        "allowed file",
        "upload failed",
    ]
    return any(n in blob for n in needles)

def post_probe(session, endpoint, base_data, upload_name, marker_name, marker_bytes, crafted):
    data = list(base_data.items())

    if crafted:
        files = [
            (upload_name, ("", b"", "application/octet-stream")),
            (upload_name, (marker_name, marker_bytes, "text/plain")),
        ]
    else:
        files = [
            (upload_name, (marker_name, marker_bytes, "text/plain")),
        ]

    t0 = time.time()
    resp = session.post(
        endpoint,
        data=data,
        files=files,
        timeout=30,
        allow_redirects=True,
    )
    return resp, time.time() - t0

def find_marker_on_disk(wp_root, marker_bytes):
    root = Path(wp_root).expanduser().resolve()
    d = root / "wp-content" / "uploads" / "elementor" / "forms"

    if not d.is_dir():
        return d, []

    hits = []
    for p in d.rglob("*"):
        if not p.is_file():
            continue

        try:
            if p.stat().st_size > 1024 * 1024:
                continue
            if not p.is_symlink() and p.resolve().is_relative_to(d.resolve()) and p.read_bytes() == marker_bytes:
                hits.append(p)
        except (OSError, PermissionError):
            pass

    return d, hits

def crawl_site(session, site, max_pages, delay, include_sitemaps=True):
    start = normalize_url(site, site)
    if not start:
        raise SystemExit("Invalid --site URL")

    origin = f"{urlsplit(start).scheme}://{urlsplit(start).netloc}"

    queue = collections.deque([start])
    queued = {start}
    visited = set()

    if include_sitemaps:
        print("[*] Checking WordPress sitemaps...")
        sitemap_pages, sitemap_files = crawl_sitemaps(session, start)
        print(
            f"[*] Sitemaps: {len(sitemap_files)} XML file(s), "
            f"{len(sitemap_pages)} page URL(s)"
        )
        for u in sorted(sitemap_pages):
            if u not in queued:
                queue.append(u)
                queued.add(u)

    candidates = []
    seen_candidate_keys = set()
    versions = set()

    while queue and len(visited) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue

        visited.add(url)
        n = len(visited)
        print(f"[CRAWL {n}/{max_pages}] {url}")

        try:
            r = session.get(url, timeout=20, allow_redirects=True)
        except requests.RequestException as exc:
            print(f"    [!] request failed: {exc}")
            continue

        if not r.ok:
            print(f"    [!] HTTP {r.status_code}")
            continue

        ctype = r.headers.get("content-type", "").lower()
        if "text/html" not in ctype and "<html" not in r.text[:1000].lower():
            continue

        final_url = normalize_url(r.url, origin)
        if final_url and final_url not in visited:
                                           
            queued.add(final_url)

        version = detect_elementor_pro_version(r.text)
        if version:
            versions.add(version)

        forms = find_elementor_upload_forms(r.text, r.url)

        for form in forms:
            for upload in form["uploads"]:
                key = (
                    form["page"],
                    form["form_id"],
                    form["post_id"],
                    upload["id"],
                )
                if key in seen_candidate_keys:
                    continue

                seen_candidate_keys.add(key)
                record = dict(form)
                record["upload"] = upload
                candidates.append(record)

                print("    [+] Elementor File Upload candidate")
                print(f"        post_id  : {form['post_id']}")
                print(f"        form_id  : {form['form_id']}")
                print(f"        field_id : {upload['id']}")
                print(f"        required : {upload['required']}")
                print(f"        multiple : {upload['multiple']}")

        for link in extract_same_origin_links(r.text, r.url, origin):
            if link not in visited and link not in queued:
                queue.append(link)
                queued.add(link)

        if delay:
            time.sleep(delay)

    return visited, candidates, versions

def probe_candidate(session, candidate, overrides, wp_root=None, cleanup=False):
    upload = candidate["upload"]
    page = candidate["page"]
    form_id = candidate["form_id"]
    post_id = candidate["post_id"]

    print("\n" + "=" * 78)
    print(f"[*] Candidate page : {page}")
    print(f"[*] post_id        : {post_id}")
    print(f"[*] form_id        : {form_id}")
    print(f"[*] upload field   : {upload['id']}")
    print(f"[*] required       : {upload['required']}")
    print(f"[*] multiple       : {upload['multiple']}")

    if not form_id or not post_id:
        print("[-] Skipping: missing post_id/form_id.")
        return "skipped"

    if upload["required"]:
        print("[-] Skipping: upload field is required; documented optional-field branch absent.")
        return "skipped"

    if not upload["multiple"]:
        print("[-] Skipping: upload field does not appear to allow multiple files.")
        return "skipped"

    base_data, unresolved, captcha_like = build_base_data(
        candidate, upload["id"], overrides
    )

    if captcha_like:
        print(
            "[-] Skipping: CAPTCHA-like required field(s) detected: "
            + ", ".join(captcha_like)
        )
        return "skipped"

    if unresolved:
        print(
            "[-] Skipping: unresolved required field(s): "
            + ", ".join(unresolved)
        )
        print("    Supply with --field FIELD_ID=value")
        return "skipped"

    p = urlsplit(page)
    endpoint = f"{p.scheme}://{p.netloc}/wp-admin/admin-ajax.php"

    token = secrets.token_hex(12)
    control_marker = f"CVE-2026-32475-CONTROL:{token}\n".encode()
    control_name = f"cve-2026-32475-control-{token}.{BLOCKED_TEST_EXTENSION}"
    marker = f"CVE-2026-32475-SAFE-MARKER:{token}\n".encode()
    marker_name = f"cve-2026-32475-safe-{token}.{BLOCKED_TEST_EXTENSION}"

    print(f"[*] AJAX endpoint   : {endpoint}")
    print(f"[*] marker          : {marker.decode().strip()}")
    print("[*] Sending plain-text blocked-extension control...")

    try:
        cr, celapsed = post_probe(
            session,
            endpoint,
            base_data,
            upload["name"],
            control_name,
            control_marker,
            crafted=False,
        )
    except requests.RequestException as exc:
        print(f"[-] Control request failed: {exc}")
        return "error"

    cinfo = classify_response(cr)
    creject = has_filetype_rejection(cinfo)

    print(f"    HTTP {cr.status_code} in {celapsed:.2f}s")
    if cinfo["message"]:
        print(f"    message: {cinfo['message']}")
    if cinfo["errors"]:
        print(f"    errors: {json.dumps(cinfo['errors'], ensure_ascii=False)}")
    print(f"    file-type rejection: {creject}")

    print("[*] Sending crafted empty-first-entry differential probe...")

    try:
        tr, telapsed = post_probe(
            session,
            endpoint,
            base_data,
            upload["name"],
            marker_name,
            marker,
            crafted=True,
        )
    except requests.RequestException as exc:
        print(f"[-] Crafted request failed: {exc}")
        return "error"

    tinfo = classify_response(tr)
    treject = has_filetype_rejection(tinfo)

    print(f"    HTTP {tr.status_code} in {telapsed:.2f}s")
    if tinfo["message"]:
        print(f"    message: {tinfo['message']}")
    if tinfo["errors"]:
        print(f"    errors: {json.dumps(tinfo['errors'], ensure_ascii=False)}")
    print(f"    file-type rejection: {treject}")

    control_hits = []
    probe_hits = []
    if wp_root:
        _, control_hits = find_marker_on_disk(wp_root, control_marker)
        _, probe_hits = find_marker_on_disk(wp_root, marker)
        print(f"[*] Exact control files: {len(control_hits)}; probe files: {len(probe_hits)}")
        if cleanup:
            for expected, hits in ((control_marker, control_hits), (marker, probe_hits)):
                for hit in hits:
                    try:
                        # Recheck immediately before deleting.
                        if not hit.is_symlink() and hit.read_bytes() == expected:
                            hit.unlink()
                            print(f"[+] Removed marker: {hit}")
                    except OSError as exc:
                        print(f"[!] Marker cleanup failed: {exc}")

    verdict = response_verdict(cinfo, tinfo, bool(control_hits), bool(probe_hits))
    print(f"[{verdict.upper()}] Differential test result.")
    if verdict == "likely":
        print("[*] Application reported success; storage is not confirmed.")
    elif verdict == "inconclusive":
        print("[*] Errors, challenges, or ambiguous responses are not evidence of a bypass.")
    print(f"[*] Probe marker for manual verification: {marker.decode().strip()}")
    return verdict


def main():
    ap = argparse.ArgumentParser(
        description="Safe crawler + differential probe for CVE-2026-32475"
    )
    ap.add_argument(
        "--site",
        required=True,
        help="Site root, e.g. https://example.com/",
    )
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument(
        "--discover",
        action="store_true",
        help="Crawl and report Elementor File Upload forms only",
    )
    mode.add_argument(
        "--probe",
        action="store_true",
        help="Submit real forms with non-executing marker uploads; may trigger emails and create files",
    )
    ap.add_argument(
        "--max-pages",
        type=int,
        default=250,
        help="Maximum HTML pages to crawl (default: 250)",
    )
    ap.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="Delay between crawl GETs in seconds (default: 0.15)",
    )
    ap.add_argument(
        "--no-sitemaps",
        action="store_true",
        help="Do not seed crawl from WordPress sitemaps",
    )
    ap.add_argument(
        "--field",
        action="append",
        default=[],
        help="Set required Elementor field value as FIELD_ID=value; repeatable",
    )
    ap.add_argument(
        "--wp-root",
        help="Optional local/mounted WordPress root for definitive marker verification",
    )
    ap.add_argument(
        "--cleanup",
        action="store_true",
        help="With --wp-root, delete only exact marker files created by this run",
    )
    ap.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification",
    )
    args = ap.parse_args()

    if args.delay < 0:
        raise SystemExit("--delay must be >= 0")
    if args.cleanup and not args.wp_root:
        raise SystemExit("--cleanup requires --wp-root")
    try:
        origin_key(args.site)
    except ValueError as exc:
        raise SystemExit(str(exc))

    if args.max_pages < 1:
        raise SystemExit("--max-pages must be >= 1")

    if not args.discover and not args.probe:
        args.discover = True

    overrides = parse_field_overrides(args.field)

    s = ScopedSession(args.site)
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
    })
    s.verify = not args.insecure

    print("=" * 78)
    print("CVE-2026-32475 SAFE ELEMENTOR PRO CRAWLER")
    print("=" * 78)
    print(f"[*] Site       : {args.site}")
    print(f"[*] Max pages  : {args.max_pages}")
    print(f"[*] Crawl delay: {args.delay:.2f}s")
    print(f"[*] Mode       : {'PROBE' if args.probe else 'DISCOVER ONLY'}")
    print("[*] Scope      : same origin only")
    print("[*] Probe file : plain text with .html extension (expected to be blocked)")
    if args.probe:
        print("[!] Probe mode submits forms, may trigger notifications, and may leave files.")
    print("[*] No PHP / no shell / no filename brute force")

    visited, candidates, versions = crawl_site(
        s,
        args.site,
        args.max_pages,
        args.delay,
        include_sitemaps=not args.no_sitemaps,
    )

    print("\n" + "=" * 78)
    print("DISCOVERY SUMMARY")
    print("=" * 78)
    print(f"Pages crawled          : {len(visited)}")
    print(f"Upload candidates found: {len(candidates)}")

    if versions:
        print("Elementor Pro asset version(s): " + ", ".join(sorted(versions)))
    else:
        print("Elementor Pro asset version   : not exposed during crawl")

    if not candidates:
        print(
            "\n[+] No Elementor File Upload forms were discovered in the crawled pages."
        )
        print(
            "[*] This does not prove none exist if they are behind authentication, "
            "rendered only after JavaScript interaction, or omitted from links/sitemaps."
        )
        return

    eligible = [
        c for c in candidates
        if not c["upload"]["required"]
        and c["upload"]["multiple"]
        and c["form_id"]
        and c["post_id"]
    ]

    print(f"Eligible optional+multiple candidates: {len(eligible)}")

    for i, c in enumerate(candidates, 1):
        u = c["upload"]
        print(
            f"[{i}] {c['page']}\n"
            f"    post_id={c['post_id']} form_id={c['form_id']} "
            f"field={u['id']} required={u['required']} multiple={u['multiple']}"
        )

    if not args.probe:
        print(
            "\n[*] Discovery-only mode. Re-run with --probe to perform the "
            "non-executing differential test."
        )
        return

    if not eligible:
        print(
            "\n[+] No candidates matched the documented optional + multiple-file "
            "configuration. No POST probes were sent."
        )
        return

    results = collections.Counter()

    for candidate in eligible:
        result = probe_candidate(
            s,
            candidate,
            overrides,
            wp_root=args.wp_root,
            cleanup=args.cleanup,
        )
        results[result] += 1

    print("\n" + "=" * 78)
    print("PROBE SUMMARY")
    print("=" * 78)

    for k in (
        "vulnerable",
        "likely",
        "not_reproduced",
        "inconclusive",
        "skipped",
        "error",
    ):
        if results[k]:
            print(f"{k:16s}: {results[k]}")

    if results["vulnerable"] or results["likely"]:
        print(
            "\n[!] At least one form showed evidence consistent with "
            "CVE-2026-32475."
        )
        print(
            "[*] Patch Elementor Pro to 4.2.2 or newer and inspect "
            "wp-content/uploads/elementor/forms/."
        )
    else:
        print(
            "\n[*] No discovered candidate produced positive evidence in this run."
        )

if __name__ == "__main__":
    main()

