import time
import random
import re
import json
import hashlib
import urllib.robotparser
from collections import deque
from urllib.parse import urljoin, urlparse, quote_plus, unquote

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

# ====================== PAGE CONFIG ======================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
    }
    div[data-testid="stMetric"] div {
        color: #38bdf8 !important;
        font-weight: 600;
    }
    .stButton > button {
        background: linear-gradient(180deg, #808080, #4c5055);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    .stDownloadButton > button {
        background: linear-gradient(180deg, #021024, #052659);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
    }
    .welcome-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }
    .welcome-title {
        font-size: 1.6rem;38bdf8
        font-weight: 700;
        color: #291C0E;
        margin-bottom: 6px;
    }
    .welcome-subtitle {
        color: #6E473B;
        font-size: 1rem;
        margin-bottom: 14px;
    }
    .quote {
        font-style: italic;
        color: #A78D78;
        border-left: 4px solid #3b82f6;
        padding-left: 16px;
        margin-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== NO PAID/API BUSINESS SEARCH ======================
# Google Maps / Places business search has been removed.
# Business leads are collected from public Uganda directories and registries.

# ====================== QUOTES & WELCOME ======================
@st.cache_data(ttl=60)
def get_live_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and data[0].get("q"):
                return f'"{data[0]["q"]}" — {data[0].get("a", "Unknown")}'
    except Exception:
        pass
    return '"Dream big. Start small. Act now."'


def get_greeting():
    eat_timezone = timezone(timedelta(hours=3))
    hour = datetime.now(eat_timezone).hour
    if 5 <= hour < 12:
        return "Good morning Alison"
    elif 12 <= hour < 17:
        return "Good afternoon Alison"
    elif 17 <= hour < 22:
        return "Good evening Alison"
    else:
        return "Hello Alison"


quote = get_live_quote()
greeting = get_greeting()

st.markdown(f"""
<div class="welcome-card">
    <div class="welcome-title">{greeting} Ready to generate leads?</div>
    <div class="welcome-subtitle">Full coverage across Kampala, Wakiso, Mukono & Regional Directories</div>
    <div class="quote">{quote}</div>
</div>
""", unsafe_allow_html=True)

st.title("Full Region Business Lead Generator")
st.caption("Direct Uganda Directory & Registry Search • Multi-Source Expansion • Deduplicated results")

# ====================== SIDEBAR ======================
st.sidebar.markdown("### ⚙️ Search Settings")

region = st.sidebar.selectbox(
    "Select Region",
    ["Kampala", "Wakiso", "Mukono", "Western Uganda", "Masaka", "Jinja"]
)

search_query = st.sidebar.text_input(
    "Business Type / Keyword",
    value="Hardware",
    help="e.g. School, Hardware, Pharmacy, Bank, Supermarket, Clinic..."
)

st.sidebar.markdown("---")
st.sidebar.info("Direct public-directory mode active. Every new region/keyword combination starts a fresh search across the configured sources.")

# ====================== UGANDA SOURCE REGISTRY ======================
# Verified source catalog. Each source is searched independently and the
# returned records are normalized into the same table. We do not fabricate
# records when a source is empty or inaccessible.
DIRECTORY_SOURCES = [
    {"name": "URSB Official Registry", "url": "https://eregistry.ursb.go.ug/search", "mode": "generic", "search_patterns": ["https://eregistry.ursb.go.ug/search?q={query}"]},
    {"name": "KCCA Licensed Businesses", "url": "https://www.kcca.go.ug/businesses", "mode": "kcca"},
    {"name": "Uganda Investment Authority", "url": "https://ugandainvest.go.ug/", "mode": "generic", "search_patterns": ["https://ugandainvest.go.ug/?s={query}"]},
    {"name": "National NGO Bureau", "url": "https://www.ngobureau.go.ug/en/updated-national-ngo-register", "mode": "generic"},
    {"name": "Yellow Pages Uganda", "url": "https://www.yellowpages-uganda.com/", "mode": "yellowpages"},
    {"name": "FinderAfrica Uganda", "url": "https://finderafrica.com/location/business-directory-uganda/", "mode": "finderafrica"},
    {"name": "HelloUganda", "url": "https://www.hellouganda.com/", "mode": "generic"},
    {"name": "B2BMAP Uganda", "url": "https://www.b2bmap.com/uganda", "mode": "generic"},
    {"name": "Uganda Manufacturers Association", "url": "https://uma.or.ug/", "mode": "uma"},
    {"name": "Cylex Uganda", "url": "https://www.cylex-uganda.com/", "mode": "generic"},
    {"name": "Yelu Uganda", "url": "https://www.yelu.ug/", "mode": "generic"},
    {"name": "Hotfrog Uganda", "url": "https://www.hotfrog.ug/", "mode": "hotfrog"},
    {"name": "Opendi Uganda", "url": "https://www.opendi.ug/", "mode": "generic"},
    {"name": "BusinessList Uganda", "url": "https://www.businesslist.co.ug/", "mode": "generic"},
    {"name": "InfoGuide Uganda", "url": "https://www.infoguideuganda.com/", "mode": "generic"},
    {"name": "Africa2Trust", "url": "https://africa2trust.com/", "mode": "generic"},
    {"name": "Yellow Uganda", "url": "https://www.yellow.ug/", "mode": "yellow_ug", "search_patterns": ["https://www.yellow.ug/search?query={query}"]},
    {"name": "Yellow Pages Uganda (co.ug)", "url": "https://www.yellowpages.co.ug/", "mode": "generic"},
    {"name": "Afrikta Uganda", "url": "https://afrikta.com/listing-locations/uganda/", "mode": "generic"},
    {"name": "Sokoni Links Uganda", "url": "https://www.sokoni-links.com/", "mode": "generic"},
    {"name": "East Africa Tenders Uganda Business Directory", "url": "https://eastafricatenders.com/businesses/", "mode": "generic"},
    {"name": "Uganda Cargo Consolidators Association Members", "url": "https://ucca.org.ug/members-directory/", "mode": "generic"},
    {"name": "FIATA Uganda Members Directory", "url": "https://fiata.org/directory/ug/", "mode": "generic"},
    {"name": "Uganda Tourism Board Licensed Accommodation", "url": "https://utb.go.ug/licensed-facilities/", "mode": "table"},
    {"name": "National Drug Authority Licensed Outlets", "url": "https://www.nda.or.ug/licensed-outlets/", "mode": "table"},
    {"name": "Bank of Uganda Supervised Institutions", "url": "https://bou.or.ug/supervision", "mode": "table"},
    {"name": "Insurance Regulatory Authority Licensed Insurers", "url": "https://ira.go.ug/", "mode": "generic"},
    {"name": "Electricity Regulatory Authority Certified Installers", "url": "https://www.era.go.ug/certified-installation-permit-holders/", "mode": "table"},
    {"name": "Uganda National Bureau of Standards Certified Companies", "url": "https://unbs.go.ug/", "mode": "generic"},
    {"name": "CompanyData Uganda Directory", "url": "https://companydata.com/directory/business-directory-uganda/", "mode": "generic"},
    {"name": "Uganda Revenue Authority Pharmacy/Drug Shop Information", "url": "https://ura.go.ug/en/pharmacy-and-drug-shops/", "mode": "generic"},
    {"name": "Uganda Revenue Authority Licensed Customs Agents", "url": "https://ura.go.ug/en/choose-agents/licensed-list-of-agents-updated/", "mode": "table"},
    {"name": "Uganda Revenue Authority Tax Agents", "url": "https://ura.go.ug/en/choose-agents/?agent_type=dt_agents", "mode": "table"},
    {"name": "National Health Facility Registry", "url": "https://nhfr-staging.health.go.ug/", "mode": "generic"},
    {"name": "Ministry of Education and Sports Institutions", "url": "https://www.education.go.ug/schools-institutions/", "mode": "generic"},
    {"name": "Uganda Communications Commission Licensed Telecoms", "url": "https://www.ucc.co.ug/wp-content/uploads/2026/02/LIST-OF-TELECOMS-LICENSED-AS-AT-31st-JANUARY-2026.pdf", "mode": "generic"},
    {"name": "Uganda Communications Commission", "url": "https://www.ucc.co.ug/", "mode": "generic"},
    {"name": "Uganda Revenue Authority", "url": "https://ura.go.ug/", "mode": "generic"},
]


# Conservative request settings: direct scraping is not a paid API, but it
# still needs to respect servers and public access rules.
REQUEST_DELAY_MIN = 0.8
REQUEST_DELAY_MAX = 1.6
REQUEST_TIMEOUT = 20
MAX_GENERIC_DISCOVERY_PAGES = None
MAX_SITEMAP_URLS = None
USER_AGENT = "Mozilla/5.0 (compatible; UgandaBusinessDirectoryResearch/1.0; +https://example.com/bot-info)"

session = requests.Session()
ROBOTS_CACHE = {}
session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
})


def clean_text(value):
    if value is None:
        return "N/A"
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value if value else "N/A"


def slugify(value):
    value = unquote(str(value)).lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def make_id(source, name, address="", website=""):
    raw = "|".join([source, clean_text(name).lower(), clean_text(address).lower(), clean_text(website).lower()])
    return "dir_" + hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:24]


def allowed_by_robots(url):
    try:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain not in ROBOTS_CACHE:
            robots_url = f"{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            ROBOTS_CACHE[domain] = rp
        return ROBOTS_CACHE[domain].can_fetch(USER_AGENT, url)
    except Exception:
        # If robots.txt cannot be read, do not bypass access controls; allow
        # ordinary public pages but still obey normal request throttling.
        return True


def fetch_url(url, accept_xml=False):
    if not allowed_by_robots(url):
        return None, None
    try:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return None, None
        content_type = response.headers.get("content-type", "").lower()
        if not accept_xml and "text/html" not in content_type and "application/xhtml" not in content_type:
            return None, None
        return response.text, content_type
    except Exception:
        return None, None


def fetch_html(url):
    html, _ = fetch_url(url)
    return html


def parse_jsonld(soup):
    objects = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.get_text())
            if isinstance(data, list):
                objects.extend(data)
            else:
                objects.append(data)
        except Exception:
            continue
    return objects


def extract_business_from_jsonld(data, source, region_name, keyword, page_url):
    records = []
    if not isinstance(data, dict):
        return records

    candidates = [data]
    if isinstance(data.get("@graph"), list):
        candidates.extend(x for x in data["@graph"] if isinstance(x, dict))

    for item in candidates:
        item_type = item.get("@type", "")
        types = item_type if isinstance(item_type, list) else [item_type]
        if not any(t in {"Organization", "LocalBusiness", "Corporation", "Store", "Restaurant", "MedicalBusiness", "EducationalOrganization", "NGO"} for t in types):
            continue

        name = clean_text(item.get("name"))
        if name == "N/A":
            continue

        address = item.get("address", {})
        if isinstance(address, dict):
            address = ", ".join(filter(lambda x: clean_text(x) != "N/A", [
                address.get("streetAddress"), address.get("addressLocality"),
                address.get("addressRegion"), address.get("addressCountry")
            ]))
        else:
            address = clean_text(address)

        telephone = clean_text(item.get("telephone"))
        website = clean_text(item.get("url"))
        category = clean_text(item.get("category"))
        rating = "N/A"
        aggregate = item.get("aggregateRating")
        if isinstance(aggregate, dict):
            rating = clean_text(aggregate.get("ratingValue"))

        records.append({
            "Company Name": name,
            "Region": region_name,
            "Category": category if category != "N/A" else keyword.capitalize(),
            "Business Deals In": category if category != "N/A" else "N/A",
            "Phone Contact": telephone,
            "Website": website,
            "Physical Address": address,
            "Rating": rating,
            "Place ID": make_id(source, name, address, website),
            "Lat": "N/A",
            "Lng": "N/A",
            "Data Source": source,
            "Source URL": page_url,
        })
    return records


def looks_like_listing_link(href, anchor_text, keyword):
    path = urlparse(href).path.lower()
    text = f"{path} {anchor_text.lower()}"
    key = keyword.lower().strip()
    listing_words = [
        "business", "company", "listing", "directory", "profile", "store", "shop",
        "supplier", "manufacturer", "hotel", "school", "clinic", "pharmacy", "hospital",
        "restaurant", "services", "enterprise", "ltd", "limited", "uganda"
    ]
    return key in text or any(word in text for word in listing_words)


def extract_visible_records(soup, source, region_name, keyword, page_url):
    records = []

    # First preference: structured data.
    for obj in parse_jsonld(soup):
        records.extend(extract_business_from_jsonld(obj, source, region_name, keyword, page_url))

    # Generic fallback: headings/anchors that look like business listings.
    for heading in soup.find_all(["h2", "h3", "h4"]):
        name = clean_text(heading.get_text(" ", strip=True))
        if name in {"N/A", "Home", "Contact", "About Us", "Login", "Search", "Categories"}:
            continue
        parent = heading.parent
        block = clean_text(parent.get_text(" ", strip=True)) if parent else name
        if len(name) < 3 or len(name) > 180:
            continue
        if not any(x in block.lower() for x in ["uganda", "kampala", "phone", "+256", "address", "category", "business", "company"]):
            continue

        links = parent.find_all("a", href=True) if parent else []
        website = "N/A"
        detail_url = page_url
        for link in links:
            href = urljoin(page_url, link.get("href"))
            if href.startswith("http") and urlparse(href).netloc != urlparse(page_url).netloc:
                website = href
            elif href.startswith("http"):
                detail_url = href

        phones = re.findall(r"(?:\+?256|0)[\d\s().\-/]{7,}", block)
        phone = clean_text(phones[0] if phones else "N/A")
        address_match = re.search(r"(?:Physical Address|Address|Location|City|Town)\s*[:\-]\s*([^|]+?)(?:\s+(?:Phone|Tel|Email|Website|Category|Description)\s*[:\-]|$)", block, re.I)
        address = clean_text(address_match.group(1)) if address_match else "N/A"
        category_match = re.search(r"Category\s*[:\-]\s*([^|]+?)(?:\s+Address|\s+Email|\s+Website|$)", block, re.I)
        category = clean_text(category_match.group(1)) if category_match else keyword.capitalize()

        if keyword.lower() not in block.lower() and keyword.lower() not in category.lower():
            # Keep records if the page itself is a category/search page. For
            # generic pages this prevents unrelated site navigation from being
            # treated as a business.
            if not looks_like_listing_link(detail_url, name, keyword):
                continue

        records.append({
            "Company Name": name,
            "Region": region_name,
            "Category": category,
            "Business Deals In": category,
            "Phone Contact": phone,
            "Website": website,
            "Physical Address": address,
            "Rating": "N/A",
            "Place ID": make_id(source, name, "", website),
            "Lat": "N/A",
            "Lng": "N/A",
            "Data Source": source,
            "Source URL": detail_url,
        })

    return records


def find_next_page(soup, current_url):
    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text(" ", strip=True)).lower()
        rel = " ".join(a.get("rel", [])).lower()
        href = urljoin(current_url, a["href"])
        if "next" in text or "next" in rel:
            return href
    return None


def same_domain(url, base_url):
    return urlparse(url).netloc == urlparse(base_url).netloc


REGION_ALIASES = {
    "kampala": ["kampala", "nakawa", "kawempe", "rubaga", "lubaga", "makindye", "central division", "kololo", "ntinda", "nakasero"],
    "wakiso": ["wakiso", "kira", "nansana", "kajjansi", "gayaza", "buloba", "kira municipality", "entebbe"],
    "mukono": ["mukono", "seeta", "namugongo", "lugazi"],
    "masaka": ["masaka"],
    "jinja": ["jinja", "bugembe", "walukuba"],
    "western uganda": ["mbarara", "fort portal", "fort-portal", "kabale", "kasese", "hoima", "bushenyi", "ibanda", "ntungamo", "western uganda", "western region"],
}


def region_match(record, region_name):
    aliases = REGION_ALIASES.get(region_name.lower(), [region_name.lower()])
    text = " ".join([
        clean_text(record.get("Physical Address")),
        clean_text(record.get("Company Name")),
        clean_text(record.get("Website")),
        clean_text(record.get("Source URL")),
    ]).lower()
    return any(alias in text for alias in aliases)


def query_match(record, keyword, region_name):
    if not keyword.strip():
        return region_match(record, region_name)

    haystack = " ".join([
        clean_text(record.get("Company Name")),
        clean_text(record.get("Category")),
        clean_text(record.get("Business Deals In")),
        clean_text(record.get("Physical Address")),
        clean_text(record.get("Website")),
        clean_text(record.get("Source URL")),
    ]).lower()
    tokens = [t for t in re.findall(r"[a-z0-9]+", keyword.lower()) if len(t) > 1]
    keyword_ok = not tokens or any(t in haystack for t in tokens)
    if not keyword_ok:
        return False

    # Region is a real filter, not just a label. If the source/profile exposes
    # location information, it must agree with the selected region.
    return region_match(record, region_name)


def crawl_paginated(start_url, source, region_name, keyword, page_builder=None, max_pages=None):
    records = []
    seen_urls = set()
    page = 1
    current = start_url

    while current and current not in seen_urls:
        if max_pages is not None and page > max_pages:
            break
        seen_urls.add(current)
        html = fetch_html(current)
        if not html:
            break
        soup = BeautifulSoup(html, "html.parser")
        page_records = extract_visible_records(soup, source, region_name, keyword, current)
        records.extend(page_records)

        next_url = find_next_page(soup, current)
        if next_url and same_domain(next_url, start_url):
            current = next_url
        elif page_builder:
            page += 1
            current = page_builder(page)
        else:
            current = None
            continue
        page += 1

        if not page_records and page > 2:
            # Do not keep hammering a source after its public pagination is exhausted.
            break

    return records


def crawl_yellowpages(region_name, keyword):
    def builder(page):
        return f"https://www.yellowpages-uganda.com/listings/page/{page}/"
    records = crawl_paginated(
        builder(1), "Yellow Pages Uganda", region_name, keyword,
        page_builder=builder, max_pages=None
    )
    return [r for r in records if query_match(r, keyword, region_name)]


def crawl_hotfrog(region_name, keyword):
    city = "kampala" if region_name == "Kampala" else slugify(region_name.replace(" Uganda", ""))
    q = slugify(keyword)
    base = f"https://www.hotfrog.ug/search/{city}/{q}"

    def builder(page):
        return base if page == 1 else f"{base}/{page}"

    return crawl_paginated(
        base, "Hotfrog Uganda", region_name, keyword,
        page_builder=builder, max_pages=None
    )


def crawl_finderafrica(region_name, keyword):
    base = "https://finderafrica.com/location/business-directory-uganda/"

    def builder(page):
        return base if page == 1 else f"{base}page/{page}/"

    records = crawl_paginated(
        base, "FinderAfrica Directory", region_name, keyword,
        page_builder=builder, max_pages=None
    )
    return [r for r in records if query_match(r, keyword, region_name)]


def crawl_kcca(region_name, keyword):
    url = "https://www.kcca.go.ug/businesses"
    if not allowed_by_robots(url):
        return []
    try:
        time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
        response = session.get(url, params={"business_name": keyword, "business_nature": keyword}, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        records = extract_visible_records(soup, "KCCA Business Register", region_name, keyword, response.url)
        return [r for r in records if query_match(r, keyword, region_name)]
    except Exception:
        return []


def sitemap_urls(base_url):
    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    candidates = [root + "/sitemap.xml", root + "/sitemap_index.xml"]
    found = []
    for sm in candidates:
        html, _ = fetch_url(sm, accept_xml=True)
        if not html:
            continue
        soup = BeautifulSoup(html, "xml")
        locs = [clean_text(x.get_text()) for x in soup.find_all("loc")]
        found.extend(locs)
        if MAX_SITEMAP_URLS is not None and len(found) >= MAX_SITEMAP_URLS:
            break
    return found if MAX_SITEMAP_URLS is None else found[:MAX_SITEMAP_URLS]


def crawl_generic(source, region_name, keyword):
    start = source["url"]
    source_name = source["name"]
    records = []

    # First try source-provided public search URLs. A source can expose a
    # search endpoint without needing an API key.
    seed_pages = []
    for pattern in source.get("search_patterns", []):
        try:
            seed_pages.append(pattern.format(query=quote_plus(keyword), region=quote_plus(region_name)))
        except Exception:
            pass

    for seed in list(dict.fromkeys(seed_pages)):
        html = fetch_html(seed)
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        records.extend(extract_visible_records(soup, source_name, region_name, keyword, seed))
        for a in soup.find_all("a", href=True):
            href = urljoin(seed, a.get("href"))
            if same_domain(href, start) and looks_like_listing_link(href, clean_text(a.get_text(" ", strip=True)), keyword):
                seed_pages.append(href)

    # Then try a public sitemap and only fetch URLs that are plausible listing
    # pages or contain the requested category/keyword.
    urls = sitemap_urls(start)
    key_tokens = [x for x in re.findall(r"[a-z0-9]+", keyword.lower()) if len(x) > 1]
    candidates = []
    for u in urls:
        low = u.lower()
        if any(t in low for t in key_tokens) or looks_like_listing_link(u, "", keyword):
            candidates.append(u)
    candidates = list(dict.fromkeys(candidates))

    if candidates:
        for u in candidates:
            html = fetch_html(u)
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            records.extend(extract_visible_records(soup, source_name, region_name, keyword, u))
            if len(records) and len(records) % 50 == 0:
                time.sleep(0.5)
        return [r for r in records if query_match(r, keyword, region_name)]

    # Fallback BFS. It follows only same-domain links that look like directory,
    # category, profile, company or listing pages; it does not bypass logins,
    # CAPTCHAs, robots rules, or access controls.
    queue = deque([start])
    seen = set()
    pages = 0

    while queue and (MAX_GENERIC_DISCOVERY_PAGES is None or pages < MAX_GENERIC_DISCOVERY_PAGES):
        current = queue.popleft()
        if current in seen or not same_domain(current, start):
            continue
        seen.add(current)
        html = fetch_html(current)
        pages += 1
        if not html:
            continue
        soup = BeautifulSoup(html, "html.parser")
        records.extend(extract_visible_records(soup, source_name, region_name, keyword, current))

        for a in soup.find_all("a", href=True):
            href = urljoin(current, a.get("href"))
            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"} or not same_domain(href, start):
                continue
            if href in seen:
                continue
            text = clean_text(a.get_text(" ", strip=True))
            if looks_like_listing_link(href, text, keyword):
                queue.append(href)

    return [r for r in records if query_match(r, keyword, region_name)]


def crawl_uma(region_name, keyword):
    # UMA has a public member list. Generic parsing is used so member names are
    # captured without inventing contact details that are not published there.
    return crawl_generic(
        {"name": "Uganda Manufacturers Association (UMA)", "url": "https://uma.or.ug/", "mode": "generic"},
        region_name, keyword
    )


def collect_from_source(source, region_name, keyword):
    try:
        mode = source.get("mode")
        if mode == "yellowpages":
            return crawl_yellowpages(region_name, keyword)
        if mode == "yellow_ug":
            return crawl_generic(source, region_name, keyword)
        if mode == "hotfrog":
            return crawl_hotfrog(region_name, keyword)
        if mode == "finderafrica":
            return crawl_finderafrica(region_name, keyword)
        if mode == "kcca":
            return crawl_kcca(region_name, keyword)
        if mode == "uma":
            return crawl_uma(region_name, keyword)
        if mode == "table":
            return crawl_generic(source, region_name, keyword)
        return crawl_generic(source, region_name, keyword)
    except Exception:
        return []


def normalize_and_dedupe(records):
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    expected = [
        "Company Name", "Region", "Category", "Business Deals In",
        "Phone Contact", "Website", "Physical Address", "Rating",
        "Place ID", "Lat", "Lng", "Data Source", "Source URL"
    ]
    for col in expected:
        if col not in df.columns:
            df[col] = "N/A"

    for col in expected:
        df[col] = df[col].map(clean_text)

    # Remove obvious navigation/noise rows.
    bad_names = {"home", "contact", "about us", "login", "register", "search", "categories", "read more"}
    df = df[~df["Company Name"].str.lower().isin(bad_names)]

    # First exact source record ID, then cross-source business identity.
    df["_identity"] = (
        df["Company Name"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        + "|" + df["Physical Address"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    )
    df = df.drop_duplicates(subset=["Place ID"], keep="first")

    # Cross-directory dedupe: same company + same/near-same address becomes one row.
    df = df.drop_duplicates(subset=["_identity"], keep="first")
    df = df.drop(columns=["_identity"], errors="ignore")
    return df.reset_index(drop=True)


# ====================== SESSION STATE ======================
# The active search fingerprint is deliberately tied to BOTH region and keyword.
# Changing either one starts a clean search and prevents stale results from
# being reused or renamed.
if "stored_places" not in st.session_state:
    st.session_state.stored_places = []
if "last_search_fingerprint" not in st.session_state:
    st.session_state.last_search_fingerprint = ""
if "source_status" not in st.session_state:
    st.session_state.source_status = {}
if "source_errors" not in st.session_state:
    st.session_state.source_errors = {}

from concurrent.futures import ThreadPoolExecutor, as_completed

# ====================== OPTIMIZED COLLECTION PIPELINE ======================

def process_single_source(source, region, search_query):
    """Worker function to scrape a single source safely within a thread pool."""
    source_name = source["name"]
    try:
        records = collect_from_source(source, region, search_query)
        records = [r for r in records if query_match(r, search_query, region)]
        return source_name, records, None
    except Exception as exc:
        return source_name, [], str(exc)[:200]

if not search_query.strip():
    st.warning("Enter a business keyword to start the directory search.")
else:
    if not st.session_state.stored_places:
        with st.spinner(f"⚡ Concurrently scanning Uganda directories & registries for '{search_query}' in {region}..."):
            all_records = []
            source_status = {}
            source_errors = {}

            # Use ThreadPoolExecutor to scrape multiple directories simultaneously
            max_workers = min(8, len(DIRECTORY_SOURCES)) # Adjust worker count to balance speed and server load
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_source = {
                    executor.submit(process_single_source, source, region, search_query): source 
                    for source in DIRECTORY_SOURCES
                }
                
                for future in as_completed(future_to_source):
                    source_name, records, error = future.result()
                    source_status[source_name] = len(records)
                    if error:
                        source_errors[source_name] = error
                    all_records.extend(records)

            st.session_state.source_status = source_status
            st.session_state.source_errors = source_errors

            df_temp = normalize_and_dedupe(all_records)
            if not df_temp.empty:
                df_temp["Search Fingerprint"] = current_search_fingerprint
                st.session_state.stored_places = df_temp.to_dict("records")
