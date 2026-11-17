#!/usr/bin/env python3
"""Generates the static HTML pages from shared partials. Run: python3 _build/build.py"""
import os, pathlib, json, datetime
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Live site address: used for canonical tags, Open Graph URLs, JSON-LD and sitemap.xml
SITE = 'https://houseroot.in'
EMAIL = 'sales@houseroot.in'
PHONE_E164 = '+919230592846'
OG_IMAGE = 'assets/img/hero-model.jpg'

# Location landing pages: (file, short name for menus)
LOCATIONS = [('new-town.html', 'New Town'), ('rajarhat.html', 'Rajarhat'), ('southern-bypass.html', 'Southern Bypass')]

ICON = {
 'pin': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
 'home': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>',
 'doc': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 7h3M13 7h3M8 11h3M13 11h3M8 15h3M13 15h3M10 21v-3h4v3"/></svg>',
 'arrow': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'search': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
 'cal': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
 'rupee': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h12M6 9h12M9 4c0 7 6 7 6 11H6"/></svg>',
 'wa': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-12.3 7.5L3 21l2-5.5A8.5 8.5 0 1 1 21 11.5z"/></svg>',
 'mail': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
 'phone': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6.2 6.2l1.3-1.3a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
 'heart': '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linejoin="round"><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/></svg>',
 'list': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7h18M3 12h12M3 17h8"/></svg>',
 'grid': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4zM4 10h16M10 4v16"/></svg>',
 'refresh': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9"/><path d="M21 3v6h-6"/></svg>',
 'layers': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
 'video': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="m10 9 5 3-5 3z"/></svg>',
 'check': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg>',
 'users': '<svg aria-hidden="true" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3"/><path d="M3 20c0-4 3-6 6-6s6 2 6 6M16 11h5M18.5 8.5v5"/></svg>',
}
def ic(name, s=20, c='#1A1A1A'): return ICON[name].format(s=s, c=c)

def jsonld(data):
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/') + '\n</script>\n'

def head(title, desc, dark=False, path=None, full_title=None, keywords=None, schema=''):
    """path: the page's URL path for canonical/og:url ('' = homepage). None = no canonical
    (project.html and post.html change per ?id / ?slug, so a fixed canonical would be wrong)."""
    t = full_title or f'{title} · HouseRoot'
    url = None if path is None else f'{SITE}/{path}'
    seo = ''
    if keywords: seo += f'<meta name="keywords" content="{", ".join(keywords)}">\n'
    if url: seo += f'<link rel="canonical" href="{url}">\n'
    og = f'''<meta property="og:type" content="website">
<meta property="og:site_name" content="HouseRoot">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
{f'<meta property="og:url" content="{url}">' + chr(10) if url else ''}<meta property="og:image" content="{SITE}/{OG_IMAGE}">
<meta property="og:image:alt" content="Architectural model of a modern home on blueprints, by HouseRoot Kolkata">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/{OG_IMAGE}">'''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{desc}">
{seo}<meta name="theme-color" content="{'#1A1A1A' if dark else '#F58220'}">
{og}
{schema}<link rel="icon" href="assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v=20261117a">
</head>
<body>
<div class="page"><div class="card-shell{' card-shell--dark' if dark else ''}">
'''

def header(dark=False):
    logo = 'logo-h-white.png' if dark else 'logo-h.png'
    return f'''<header class="header"><div class="inner nav">
  <a href="index.html" class="nav__logo" aria-label="HouseRoot home"><img src="assets/img/{logo}" alt="HouseRoot" width="900" height="134"></a>
  <nav class="nav__links" aria-label="Primary"><a href="projects.html">Buy</a><a href="projects.html#rent">Rent</a><a href="contact.html">Sell</a><a href="contact.html#agents">Find agent</a></nav>
  <div class="nav__right"><a href="developers.html">List property</a><a href="blog.html">Blog</a><a href="about.html">About us</a><a href="admin/" class="btn btn--sm btn--outline nav__login">Login</a><a href="contact.html" class="btn btn--sm">Join</a>
    <button class="nav__burger" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button></div>
</div></header>
<div class="drawer" aria-hidden="true"><div class="drawer__scrim"></div><div class="drawer__panel">
  <button class="drawer__close" aria-label="Close menu">×</button>
  <a href="index.html">Home</a><a href="projects.html">Buy</a><a href="projects.html#rent">Rent</a><a href="contact.html">Sell</a><a href="contact.html#agents">Find agent</a><a href="developers.html">List property</a><a href="blog.html">Blog</a><a href="about.html">About us</a>
  {''.join(f'<a href="{f}">{n}</a>' for f, n in LOCATIONS)}
  <div class="drawer__cta"><a href="admin/" class="btn btn--block btn--outline">Login</a><a href="contact.html" class="btn btn--block">Request a call back</a><a href="https://wa.me/919230592846" class="btn btn--block btn--dark">{ic('wa',18,'#7CD992')} WhatsApp us</a></div>
</div></div>
'''

FOOTER = f'''<footer class="footer"><div class="inner section stack" style="gap:48px">
  <div class="footer__grid">
    <div class="footer__brand stack" style="gap:18px"><img src="assets/img/logo-white.png" alt="HouseRoot" style="height:60px;width:auto;align-self:flex-start"><p>Connecting you to the home you love. A real estate channel partner brand by Flint De Orient Marketing &amp; Technology Pvt. Ltd., Kolkata.</p><span style="font-size:13px;color:#8A8A8A">RERA Reg. No. [WB/XXXXX]</span></div>
    <div class="footer__col"><h4>Explore</h4><a href="projects.html">New launches</a><a href="projects.html">Ready to move</a><a href="projects.html">Plots &amp; land</a><a href="projects.html">Commercial</a><a href="blog.html">Blog</a></div>
    <div class="footer__col"><h4>Company</h4><a href="about.html">About HouseRoot</a><a href="developers.html">For developers</a><a href="contact.html">Careers</a><a href="https://flintdeorient.in" target="_blank" rel="noopener">Flint De Orient</a></div>
    <div class="footer__col"><h4>Locations</h4>{''.join(f'<a href="{f}">{n}</a>' for f, n in LOCATIONS)}</div>
    <div class="footer__col"><h4>Visit</h4><span>[Office address line 1]<br>[Line 2], Kolkata – [PIN]</span><a href="mailto:sales@houseroot.in">sales@houseroot.in</a></div>
  </div>
  <div class="footer__bottom"><span>© <span data-year>2026</span> HouseRoot · Flint De Orient Marketing &amp; Technology Pvt. Ltd.</span><div class="row" style="gap:24px"><a href="#">Privacy</a><a href="#">Terms</a><a href="#">RERA disclaimer</a><a href="admin/" style="opacity:.55">Admin</a></div></div>
</div></footer>
</div></div>
<a href="https://wa.me/919230592846" class="wa-fab" aria-label="Chat on WhatsApp" target="_blank" rel="noopener">{ic('wa',26,'#fff')}</a>
<script src="assets/js/main.js?v=20261117a" defer></script>
<script src="assets/js/site-data.js?v=20261117a" defer></script>
</body>
</html>
'''

def pcard(name, loc, dev, chips, price, tag='New launch', tagcls=''):
    chips_html = ''.join(f'<span class="chip">{c}</span>' for c in chips)
    return f'''<article class="pcard">
  <div class="photo">Add project photo<span class="tag {tagcls}">{tag}</span><button type="button" class="save" aria-label="Save project" aria-pressed="false">{ICON['heart']}</button></div>
  <div class="pcard__body">
    <div class="stack" style="gap:4px"><h3 class="h-4">{name}</h3><span class="pcard__meta">{loc} · by {dev}</span></div>
    <div class="pcard__chips">{chips_html}</div>
    <div class="pcard__foot"><div class="stack"><span style="font-size:12px;color:#8A8A8A;font-weight:600">Starting</span><span class="price">{price}</span></div><a href="project.html" class="btn btn--sm btn--dark">View project</a></div>
  </div>
</article>'''

SUCCESS = '''<div class="form-success"><span style="width:64px;height:64px;border-radius:50%;background:#E8F7EC;display:inline-flex;align-items:center;justify-content:center">''' + ic('check',30,'#1E7A3C') + '''</span><strong class="h-4">Got it — we'll call you within the hour.</strong><span style="font-size:14px;color:#5A5A5A">Weekdays 10 am – 7 pm. Or WhatsApp us anytime.</span></div>'''

# =============================== INDEX ===============================
AGENT_SCHEMA = jsonld({
    '@context': 'https://schema.org',
    '@type': 'RealEstateAgent',
    '@id': f'{SITE}/#agent',
    'name': 'HouseRoot',
    'url': f'{SITE}/',
    'logo': f'{SITE}/assets/img/logo.png',
    'image': f'{SITE}/{OG_IMAGE}',
    'description': 'RERA-registered real estate channel partner in Kolkata for new launches and luxury projects in New Town, Rajarhat and Southern Bypass. Zero brokerage on new homes.',
    'email': EMAIL,
    'telephone': PHONE_E164,
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Kolkata', 'addressRegion': 'West Bengal', 'addressCountry': 'IN'},
    'areaServed': [{'@type': 'City', 'name': 'Kolkata'}] + [{'@type': 'Place', 'name': f'{n}, Kolkata'} for _, n in LOCATIONS],
    'contactPoint': {'@type': 'ContactPoint', 'telephone': PHONE_E164, 'email': EMAIL, 'contactType': 'sales', 'areaServed': 'IN', 'availableLanguage': ['English', 'Bengali', 'Hindi']},
    'parentOrganization': {'@type': 'Organization', 'name': 'Flint De Orient Marketing & Technology Pvt. Ltd.', 'url': 'https://flintdeorient.in'},
})

index = head('Home', 'RERA-registered channel partner for new homes and luxury projects in New Town, Rajarhat and Southern Bypass, Kolkata. Zero brokerage on new launches.',
             path='', full_title='New Homes in Kolkata, Zero Brokerage | HouseRoot', schema=AGENT_SCHEMA) + header() + f'''
<section class="hero" id="top">
  <div class="hero__art" aria-hidden="true"><picture><source srcset="assets/img/hero-model.webp" type="image/webp"><img class="hero__img" src="assets/img/hero-model.jpg" alt="Architectural model of a modern multi-storey home on blueprints, representing new launch projects in Kolkata" width="2200" height="1228" fetchpriority="high"></picture></div>
  <div class="inner hero__grid">
    <div class="hero__copy">
      <span class="eyebrow">New homes · Kolkata</span>
      <h1 class="hero__title words">Connecting you <span class="muted">to the</span> home you love</h1>
      <p class="hero__lede">From blueprint to keys. RERA-verified new launches, ready-to-move flats and villas across Kolkata, every one walked by our team. Zero brokerage on new homes.</p>
      <div class="stats">
        <div><span class="stat" data-count="40" data-suffix="+">0</span><span class="stat-l">Projects listed</span></div>
        <div><span class="stat" data-count="300" data-suffix="+">0</span><span class="stat-l">Families moved in</span></div>
        <div><span class="stat" data-count="4.8">0</span><span class="stat-l">Google rating</span></div>
      </div>
    </div>
  </div>
  <a href="project.html" class="callout callout--roof"><span class="callout__dot"></span><span class="callout__line"></span><span class="callout__card"><strong>[Project name]</strong><span>New Town · 3 BHK · ₹[XX] L onwards</span></span></a>
  <a href="contact.html" class="callout callout--visit"><span class="callout__dot"></span><span class="callout__line"></span><span class="callout__card"><strong>Free site visits</strong><span>Pick-up &amp; drop across Kolkata</span></span></a>
</section>

<div class="inner finder-wrap">
  <form class="finder" action="projects.html" method="get" aria-label="Search homes">
    <input type="hidden" name="mode" value="buy">
    <div class="finder__tabs" role="tablist" aria-label="Looking to">
      <button type="button" role="tab" class="is-on" aria-selected="true" data-value="buy"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11 12 3l9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/></svg>Buy</button>
      <button type="button" role="tab" aria-selected="false" data-value="rent"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M15 12v2"/></svg>Rent</button>
      <button type="button" role="tab" aria-selected="false" data-value="plots"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7 9 4l6 3 6-3v13l-6 3-6-3-6 3z"/><path d="M9 4v13M15 7v13"/></svg>Plots</button>
      <button type="button" role="tab" aria-selected="false" data-value="commercial"><svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 7h3M13 7h3M8 11h3M13 11h3M8 15h3M13 15h3M10 21v-3h4v3"/></svg>Commercial</button>
    </div>
    <div class="finder__row">
      <label class="finder__f"><span class="finder__lbl">Location</span><span class="finder__in"><input name="q" type="text" placeholder="Locality, project or PIN" autocomplete="off"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg></span></label>
      <label class="finder__f"><span class="finder__lbl">Property type</span><span class="finder__in"><select name="type"><option>All types</option><option>2 BHK</option><option>3 BHK</option><option>4 BHK+</option><option>Villa</option></select></span></label>
      <label class="finder__f"><span class="finder__lbl">Budget</span><span class="finder__in"><select name="budget"><option>Any price</option><option>Under ₹50 L</option><option>₹50 L – ₹1 Cr</option><option>₹1 – 2 Cr</option><option>₹2 Cr +</option></select></span></label>
      <label class="finder__f"><span class="finder__lbl">Possession</span><span class="finder__in"><select name="possession"><option>Any time</option><option>Ready to move</option><option>Within 1 year</option><option>1–3 years</option></select></span></label>
      <button type="submit" class="btn finder__btn"><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg> Search</button>
    </div>
  </form>
</div>

<section class="section section--white section--top-round" id="about"><div class="inner">
  <div class="why-panel" data-reveal="scale">
    <div class="why-panel__blob why-panel__blob--a" aria-hidden="true"></div>
    <div class="why-panel__blob why-panel__blob--b" aria-hidden="true"></div>
    <div class="chevron-bg chevron-bg--white" style="right:-180px;top:-200px;width:640px;height:640px" aria-hidden="true"></div>
    <div class="stack" style="gap:12px;align-items:center;text-align:center;position:relative">
      <span class="eyebrow">Why HouseRoot</span>
      <h2 class="h-2">Verified. Local. Zero brokerage.</h2>
      <div class="rule"></div>
      <p class="lede" style="max-width:560px">We're not a listing site. We're the advisor who has walked every project in Kolkata and is paid by the developer, not by you.</p>
    </div>
    <ul class="why" data-stagger>
      <li class="why__item">
        <span class="why__ic"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="m9 12 2 2 4-4"/></svg></span>
        <h3 class="h-4">RERA-verified projects</h3>
        <p>Every project is walked by our team. Approvals, pricing and possession history are checked before it is listed.</p>
      </li>
      <li class="why__item">
        <span class="why__ic"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 4h10M7 8h10M9 4c0 7 6 7 6 12a4 4 0 0 1-4 4H7"/></svg></span>
        <h3 class="h-4">Zero brokerage on new homes</h3>
        <p>The developer pays our fee, so you pay nothing extra and get the same price as walking in directly. Often better.</p>
      </li>
      <li class="why__item">
        <span class="why__ic"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/><path d="m16 5 1.5 1.5L20 4"/></svg></span>
        <h3 class="h-4">One advisor, start to keys</h3>
        <p>The person who takes your first call stays with you through site visits, negotiation, loan and possession.</p>
      </li>
      <li class="why__item">
        <span class="why__ic"><svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s7-6.3 7-12a7 7 0 1 0-14 0c0 5.7 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg></span>
        <h3 class="h-4">Kolkata, block by block</h3>
        <p>New Town, Salt Lake, EM Bypass, Joka and Howrah, compared on metro access, schools, flooding and growth.</p>
      </li>
    </ul>
  </div>
</div></section>

<section class="section section--card" id="projects"><div class="inner stack" style="gap:40px">
  <div class="stack" style="gap:14px;align-items:center;text-align:center" data-reveal><div class="rule"></div><h2 class="h-2">Find your dream home</h2><p class="lede">Curated new launches across Kolkata — shortlist, visit, negotiate, move in.</p></div>
  <form class="bar" action="projects.html" method="get" aria-label="Filter projects" data-reveal="scale">
    <div class="bar__f">{ic('pin',22)}<label>Location<select name="loc"><option>Anywhere in Kolkata</option><option>New Town &amp; Rajarhat</option><option>Salt Lake</option><option>EM Bypass</option><option>Joka &amp; Behala</option><option>Howrah</option></select></label></div>
    <div class="bar__f">{ic('cal',22)}<label>Possession<select name="when"><option>Any time</option><option>Ready to move</option><option>Within 1 year</option><option>1–3 years</option></select></label></div>
    <div class="bar__f">{ic('rupee',22)}<label>Budget<select name="budget"><option>Any price</option><option>Under ₹50 L</option><option>₹50 L – ₹1 Cr</option><option>₹1 – 2 Cr</option><option>₹2 Cr +</option></select></label></div>
    <button type="submit" class="btn btn--lg">{ic('search',18)} Search</button>
  </form>
  <div class="grid-3" data-stagger data-featured-grid>
    {pcard('[Project name]','[Locality], Kolkata','[Developer]',['2 &amp; 3 BHK','[XXX]–[XXXX] sq ft','RERA ✓'],'₹[XX] L+')}
    {pcard('[Project name]','[Locality], Kolkata','[Developer]',['3 &amp; 4 BHK','OC received','RERA ✓'],'₹[X.X] Cr+','Ready to move','tag--dark')}
    {pcard('[Project name]','[Locality]','[Developer]',['Gated','[X]–[Y] katha','Mutation ✓'],'₹[XX] L+','Plots','tag--white')}
  </div>
</div></section>

<section class="section section--white" id="how"><div class="inner stack" style="gap:44px">
  <div class="stack" style="gap:14px;align-items:center;text-align:center" data-reveal><div class="rule"></div><h2 class="h-2">How HouseRoot works</h2><p class="lede" style="max-width:560px">From your first call to the keys in your hand, one advisor stays with you. Here is what the next few weeks look like.</p></div>
  <ol class="how" data-stagger>
    <li class="how__step">
      <div class="how__art"><svg viewBox="0 0 220 150" role="img" aria-label="Advisor on a call with a checklist of what matters to you" fill="none" stroke="#1A1A1A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="26" y="18" width="62" height="114" rx="10" fill="#fff"/><rect x="34" y="28" width="46" height="88" rx="6" fill="#FFF1E6" stroke="none"/><line x1="50" y1="124" x2="64" y2="124"/>
        <rect x="42" y="40" width="30" height="12" rx="6" fill="#F58220" stroke="none"/><rect x="42" y="58" width="22" height="10" rx="5" fill="#fff"/><rect x="50" y="74" width="22" height="10" rx="5" fill="#fff"/>
        <rect x="104" y="30" width="92" height="96" rx="10" fill="#fff"/><line x1="104" y1="48" x2="196" y2="48"/><circle cx="118" cy="39" r="3" fill="#F58220" stroke="none"/>
        <rect x="114" y="58" width="12" height="12" rx="3" fill="#FFE6D2"/><path d="m117 64 3 3 5-6"/><line x1="134" y1="64" x2="184" y2="64"/>
        <rect x="114" y="78" width="12" height="12" rx="3" fill="#FFE6D2"/><path d="m117 84 3 3 5-6"/><line x1="134" y1="84" x2="176" y2="84"/>
        <rect x="114" y="98" width="12" height="12" rx="3" fill="#fff"/><line x1="134" y1="104" x2="168" y2="104"/>
        <circle cx="196" cy="118" r="14" fill="#F58220" stroke="none"/><path d="M190 119c2 3 4 4 6 4 3 0 5-2 7-5" stroke="#fff"/><path d="M191 113l3 1M201 113l-3 1" stroke="#fff"/>
      </svg></div>
      <h3 class="h-4"><span class="how__n">Step 1</span>Tell us your brief</h3>
      <p>A 15-minute call. Budget, localities, timeline, what matters: schools, metro, Vastu, rental yield.</p>
    </li>
    <li class="how__step">
      <div class="how__art"><svg viewBox="0 0 220 150" role="img" aria-label="A shortlist of verified projects with one marked as the pick" fill="none" stroke="#1A1A1A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <rect x="20" y="34" width="54" height="84" rx="8" fill="#fff"/><path d="M30 60l17-13 17 13v26H30z" fill="#FFF1E6"/><rect x="42" y="74" width="10" height="12" fill="#fff"/><line x1="30" y1="98" x2="64" y2="98"/><line x1="30" y1="106" x2="54" y2="106"/>
        <rect x="83" y="22" width="54" height="104" rx="8" fill="#fff" stroke-width="2"/><path d="M93 54l17-13 17 13v26H93z" fill="#FFE6D2"/><rect x="105" y="68" width="10" height="12" fill="#fff"/><line x1="93" y1="94" x2="127" y2="94"/><line x1="93" y1="102" x2="117" y2="102"/>
        <circle cx="134" cy="26" r="12" fill="#F58220" stroke="none"/><path d="m128 26 4 4 8-8" stroke="#fff" stroke-width="2.2"/>
        <rect x="146" y="34" width="54" height="84" rx="8" fill="#fff"/><path d="M156 60l17-13 17 13v26h-34z" fill="#FFF1E6"/><rect x="168" y="74" width="10" height="12" fill="#fff"/><line x1="156" y1="98" x2="190" y2="98"/><line x1="156" y1="106" x2="180" y2="106"/>
        <rect x="150" y="118" width="46" height="14" rx="7" fill="#FFE6D2" stroke="none"/><text x="173" y="128" font-family="Manrope, sans-serif" font-size="8" font-weight="700" fill="#D14F00" text-anchor="middle" stroke="none">RERA ✓</text>
        <rect x="24" y="118" width="46" height="14" rx="7" fill="#FFE6D2" stroke="none"/><text x="47" y="128" font-family="Manrope, sans-serif" font-size="8" font-weight="700" fill="#D14F00" text-anchor="middle" stroke="none">RERA ✓</text>
      </svg></div>
      <h3 class="h-4"><span class="how__n">Step 2</span>Get a shortlist of 3 to 5</h3>
      <p>Only projects our team has walked, compared on price per sq ft, carpet area, hidden charges and delay risk.</p>
    </li>
    <li class="how__step">
      <div class="how__art"><svg viewBox="0 0 220 150" role="img" aria-label="A car on the way to a project site with a map pin" fill="none" stroke="#1A1A1A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 124c40-10 80-6 116-22 28-12 44-30 74-34" stroke-dasharray="4 6"/>
        <path d="M144 50l26-20 26 20v38h-52z" fill="#FFF1E6"/><rect x="164" y="66" width="12" height="22" fill="#fff"/><rect x="150" y="60" width="8" height="8" fill="#fff"/><rect x="182" y="60" width="8" height="8" fill="#fff"/>
        <path d="M170 10c-8 0-13 6-13 12 0 9 13 20 13 20s13-11 13-20c0-6-5-12-13-12z" fill="#F58220" stroke="none"/><circle cx="170" cy="22" r="4" fill="#fff" stroke="none"/>
        <path d="M34 104h-8c-4 0-6-2-6-6v-8c0-3 2-5 5-6l10-2 10-12c2-2 4-3 7-3h22c3 0 5 1 7 3l10 12 12 2c3 1 5 3 5 6v8c0 4-2 6-6 6h-6" fill="#FFE6D2"/>
        <path d="M44 84l8-10c1-1 2-2 4-2h8v12zM70 72h10c2 0 3 1 4 2l8 10H70z" fill="#fff"/>
        <circle cx="42" cy="106" r="8" fill="#fff"/><circle cx="42" cy="106" r="3" fill="#1A1A1A" stroke="none"/><circle cx="96" cy="106" r="8" fill="#fff"/><circle cx="96" cy="106" r="3" fill="#1A1A1A" stroke="none"/><line x1="50" y1="104" x2="88" y2="104"/>
        <rect x="112" y="96" width="30" height="12" rx="6" fill="#F58220" stroke="none"/><text x="127" y="105" font-family="Manrope, sans-serif" font-size="7.5" font-weight="700" fill="#fff" text-anchor="middle" stroke="none">FREE</text>
      </svg></div>
      <h3 class="h-4"><span class="how__n">Step 3</span>Visit, then negotiate</h3>
      <p>Free pick-up and drop across Kolkata, weekends included. We use our developer relationships to get the best offer.</p>
    </li>
    <li class="how__step">
      <div class="how__art"><svg viewBox="0 0 220 150" role="img" aria-label="A hand holding house keys beside a zero brokerage tag" fill="none" stroke="#1A1A1A" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M60 132c-14 0-26-8-30-20l-6-18c-2-6 4-10 8-6l12 12V46c0-4 3-6 6-6s6 2 6 6v34h4V36c0-4 3-6 6-6s6 2 6 6v44h4V42c0-4 3-6 6-6s6 2 6 6v38h4V56c0-4 3-6 6-6s6 2 6 6v50c0 14-12 26-30 26z" fill="#FFF1E6"/>
        <circle cx="128" cy="40" r="16" fill="#fff"/><circle cx="128" cy="40" r="6" fill="#FFE6D2"/><path d="M140 48l40 38M166 72l-6 6M174 80l-6 6M180 86l-5 5"/>
        <path d="M150 104l26-20 26 20v26h-52z" fill="#fff"/><rect x="170" y="116" width="12" height="14" fill="#FFE6D2"/>
        <rect x="106" y="112" width="74" height="24" rx="12" fill="#F58220" stroke="none" transform="rotate(-8 143 124)"/><text x="143" y="128" font-family="Manrope, sans-serif" font-size="9" font-weight="700" fill="#fff" text-anchor="middle" stroke="none" transform="rotate(-8 143 124)">₹0 brokerage</text>
      </svg></div>
      <h3 class="h-4"><span class="how__n">Step 4</span>Book and move in</h3>
      <p>Zero brokerage on new homes. We stay for the loan, agreement review, registration and a possession snag-list.</p>
    </li>
  </ol>
  <div class="row" style="justify-content:center;gap:12px;flex-wrap:wrap" data-reveal><a href="contact.html" class="btn">Start with a 15-minute brief</a><a href="about.html" class="btn btn--outline">More about how we work</a></div>
</div></section>

<section class="section section--card" id="locations"><div class="inner stack" style="gap:40px">
  <div class="stack" style="gap:14px;align-items:center;text-align:center" data-reveal><div class="rule"></div><h2 class="h-2">Explore homes by location</h2><p class="lede" style="max-width:620px">Our advisors track upcoming luxury projects in New Town, Rajarhat and Southern Bypass closely — prices, RERA status, possession dates and what each tower is really like on a site visit.</p></div>
  <div class="grid-3" data-stagger>
    <div class="value"><span class="value__n">East Kolkata</span><h3 class="h-4"><a href="new-town.html">New Town</a></h3><p>A planned township with wide roads, Eco Park and IT campuses next door. High-rise 2 and 3 BHK launches for end-users and investors.</p><a href="new-town.html" class="link">Projects in New Town {ic('arrow',16)}</a></div>
    <div class="value"><span class="value__n">Near the airport</span><h3 class="h-4"><a href="rajarhat.html">Rajarhat</a></h3><p>Close to the airport and VIP Road, with gated communities and more space for the budget than central New Town.</p><a href="rajarhat.html" class="link">Projects in Rajarhat {ic('arrow',16)}</a></div>
    <div class="value"><span class="value__n">South Kolkata</span><h3 class="h-4"><a href="southern-bypass.html">Southern Bypass</a></h3><p>New residential towers along the bypass corridor, linking established South Kolkata neighbourhoods with faster road access.</p><a href="southern-bypass.html" class="link">Projects near Southern Bypass {ic('arrow',16)}</a></div>
  </div>
</div></section>

<section class="section section--ember" id="developers"><div class="chevron-bg chevron-bg--white" style="right:-160px;top:-140px;width:620px;height:620px"></div><div class="inner split" style="position:relative">
  <div class="stack" style="gap:20px" data-reveal="left">
    <span class="eyebrow">For developers</span>
    <h2 class="h-2">List your project with a partner who brings buyers, not just leads.</h2>
    <p class="lede" style="max-width:520px">HouseRoot is the real estate arm of Flint De Orient — every enquiry runs through our own CRM, WhatsApp automation and performance marketing, with a live pipeline you can see.</p>
    <div class="row" style="gap:12px;flex-wrap:wrap"><a href="developers.html" class="btn btn--white">Partner with us</a><a href="developers.html#partner" class="btn btn--ghost">Download partner deck</a></div>
  </div>
  <ul style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px" data-stagger>
    <li style="background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:8px"><strong style="font:600 16px var(--font-display)">Qualified</strong><span style="font-size:14px;line-height:1.5;opacity:.9">Budget, intent and timeline verified before any site visit.</span></li>
    <li style="background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:8px"><strong style="font:600 16px var(--font-display)">Live</strong><span style="font-size:14px;line-height:1.5;opacity:.9">Shared dashboard of leads, visits and bookings in real time.</span></li>
    <li style="background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:8px"><strong style="font:600 16px var(--font-display)">Automated</strong><span style="font-size:14px;line-height:1.5;opacity:.9">WhatsApp re-engagement of cold leads with offers and updates.</span></li>
    <li style="background:#1A1A1A;border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:8px"><strong style="font:600 16px var(--font-display);color:#F7A200">End to end</strong><span style="font-size:14px;line-height:1.5;color:#B9B2AA">Pre-launch EOI drives, broker meets and digital campaigns.</span></li>
  </ul>
</div></section>

<section class="section section--white" id="contact"><div class="inner split">
  <div class="stack" style="gap:20px" data-reveal="left">
    <div class="rule"></div>
    <h2 class="h-2">Tell us what you're looking for. We'll call within the hour.</h2>
    <p class="lede" style="max-width:460px">Or message us on WhatsApp — most of our conversations start there.</p>
    <a href="https://wa.me/919230592846" class="contact-line"><span class="contact-line__ic">{ic('wa',20,'#fff')}</span>WhatsApp: +91 92305 92846</a>
    <a href="mailto:sales@houseroot.in" class="contact-line"><span class="contact-line__ic contact-line__ic--soft">{ic('mail',20,'#D14F00')}</span>sales@houseroot.in</a>
  </div>
  <form class="form-card" style="background:var(--card);box-shadow:none" data-lead data-reveal="right">
    <div class="form-grid"><div class="field"><label class="label" for="c-name">Your name</label><input class="input" id="c-name" name="name" type="text" placeholder="Priya Sen" required style="background:#fff"></div><div class="field"><label class="label" for="c-phone">Phone</label><input class="input" id="c-phone" name="phone" type="tel" placeholder="+91" required style="background:#fff"></div></div>
    <div class="form-grid"><div class="field"><label class="label" for="c-bud">Budget</label><select class="select" id="c-bud" name="budget" style="background-color:#fff"><option>Under ₹50 L</option><option>₹50 L – ₹1 Cr</option><option>₹1 – 2 Cr</option><option>₹2 Cr +</option></select></div><div class="field"><label class="label" for="c-when">Planning to buy</label><select class="select" id="c-when" name="when" style="background-color:#fff"><option>Within 3 months</option><option>3–6 months</option><option>6–12 months</option><option>Just exploring</option></select></div></div>
    <div class="field"><label class="label" for="c-msg">Anything we should know? <span style="font-weight:500;color:#9A9A9A">(optional)</span></label><textarea class="textarea" id="c-msg" name="msg" rows="3" placeholder="Near a metro, east-facing, school within 2 km…" style="background:#fff"></textarea></div>
    <button type="submit" class="btn btn--block">Request a call back</button>
    <p class="form-note">No spam. Your number isn't shared with developers until you say so.</p>
    {SUCCESS}
  </form>
</div></section>
''' + FOOTER

# =============================== PROJECTS ===============================
projects = head('Projects', 'RERA-registered new launches, ready-to-move flats, plots and villas across Kolkata — verified by HouseRoot.', path='projects.html') + header() + f'''
<section class="inner stack" style="padding-top:24px;padding-bottom:40px;gap:28px">
  <div class="row" style="justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap">
    <div class="stack" style="gap:12px" data-reveal>
      <span style="font-size:13px;color:#7A7A7A"><a href="index.html" style="color:#7A7A7A">Home</a> &nbsp;/&nbsp; <span style="color:#1A1A1A;font-weight:600">Projects</span></span>
      <h1 class="h-2" style="font-size:24px">New homes <span class="muted">in</span> Kolkata</h1>
      <p style="color:#6E6E6E" data-projects-sub>[XX] RERA-registered projects · verified by our team · zero brokerage on new launches</p>
    </div>
    <div class="seg" role="group" aria-label="Looking to" id="rent" data-reveal="right"><button type="button" class="is-on">Buy</button><button type="button">Rent</button><button type="button">Plots</button><button type="button">Commercial</button></div>
  </div>
  <form class="bar bar--4" aria-label="Filter projects" data-reveal="scale">
    <div class="bar__f">{ic('pin',20)}<label>Location<select><option>Anywhere in Kolkata</option><option>New Town &amp; Rajarhat</option><option>Salt Lake</option><option>EM Bypass</option><option>Joka &amp; Behala</option><option>Howrah</option></select></label></div>
    <div class="bar__f">{ic('home',20)}<label>Type<select><option>Any</option><option>2 BHK</option><option>3 BHK</option><option>4 BHK+</option><option>Villa</option></select></label></div>
    <div class="bar__f">{ic('rupee',20)}<label>Budget<select><option>Any price</option><option>Under ₹50 L</option><option>₹50 L – ₹1 Cr</option><option>₹1 – 2 Cr</option><option>₹2 Cr +</option></select></label></div>
    <div class="bar__f">{ic('cal',20)}<label>Possession<select><option>Any time</option><option>Ready to move</option><option>Within 1 year</option><option>1–3 years</option></select></label></div>
    <button type="submit" class="btn">{ic('search',18)} Search</button>
  </form>
</section>

<section class="section--white section--top-round"><div class="inner listing-layout" style="padding-top:48px;padding-bottom:72px">
  <aside class="rail">
    <div class="row" style="justify-content:space-between"><strong style="font:600 16px var(--font-display)">Filters</strong><button type="button" class="btn btn--sm btn--outline rail__toggle">Show filters</button><a href="projects.html" style="font-size:13px;font-weight:600" class="rail__body">Clear all</a></div>
    <div class="rail__body">
    <div class="rail__group" data-filter-status><h3>Status</h3><label class="check"><input type="checkbox" checked> New launch</label><label class="check"><input type="checkbox" checked> Under construction</label><label class="check"><input type="checkbox"> Ready to move</label></div>
    <div class="rail__group"><h3>Developer</h3><label class="check"><input type="checkbox"> [Developer A]</label><label class="check"><input type="checkbox"> [Developer B]</label><label class="check"><input type="checkbox"> [Developer C]</label><a href="#" style="font-size:13px;font-weight:600">Show all</a></div>
    <div class="rail__group"><h3>Near</h3><label class="check"><input type="checkbox"> Metro station (1 km)</label><label class="check"><input type="checkbox"> Schools</label><label class="check"><input type="checkbox"> IT hubs</label><label class="check"><input type="checkbox"> Hospitals</label></div>
    <div class="rail__group"><h3>Extras</h3><label class="check"><input type="checkbox"> Vastu compliant</label><label class="check"><input type="checkbox"> Bank-approved</label><label class="check"><input type="checkbox"> Offer running</label></div>
    <div class="rail__promo" style="background:#1A1A1A;color:#fff;border-radius:18px;padding:22px;display:flex;flex-direction:column;gap:10px;margin-top:16px"><strong style="font:600 16px var(--font-display)">Can't decide?</strong><span style="font-size:13px;line-height:1.5;color:#B9B2AA">Tell us your brief, get a 5-project shortlist by tomorrow.</span><a href="contact.html" class="btn btn--sm">Get a shortlist</a></div>
    </div>
  </aside>
  <div class="stack" style="gap:24px">
    <div class="row" style="justify-content:space-between;gap:16px;flex-wrap:wrap"><span style="font-size:15px;color:#6E6E6E"><strong style="color:#1A1A1A" data-projects-count>[XX] projects</strong> in Kolkata</span><label class="row" style="gap:10px;font-size:14px;color:#6E6E6E">Sort by<select class="select" data-projects-sort style="width:auto;height:40px;padding:0 40px 0 14px;font-weight:600"><option>Recommended</option><option>Price: low to high</option><option>Price: high to low</option><option>Possession: soonest</option></select></label></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px" data-stagger data-projects-grid>
      {pcard('[Project name]','New Town, Kolkata','[Developer]',['2 &amp; 3 BHK','[XXX]–[XXXX] sq ft','Possession [Year]','RERA ✓'],'₹[XX] L')}
      {pcard('[Project name]','EM Bypass, Kolkata','[Developer]',['3 &amp; 4 BHK','OC received','Bank-approved','RERA ✓'],'₹[X.X] Cr','Ready to move','tag--dark')}
      {pcard('[Project name]','Salt Lake, Kolkata','[Developer]',['2 BHK','[XXX] sq ft','Metro 600 m','RERA ✓'],'₹[XX] L','Under construction','tag--white')}
      {pcard('[Project name]','Joka, Kolkata','[Developer]',['2 &amp; 3 BHK','Clubhouse','Possession [Year]','RERA ✓'],'₹[XX] L','Offer running')}
      {pcard('[Project name]','Rajarhat, Kolkata','[Developer]',['4 BHK villas','[XXXX] sq ft','Gated','RERA ✓'],'₹[X.X] Cr','Villas','tag--white')}
      {pcard('[Project name]','Howrah','[Developer]',['2 &amp; 3 BHK','OC received','Riverside','RERA ✓'],'₹[XX] L','Ready to move','tag--dark')}
    </div>
    <nav class="pg" aria-label="Pages" style="padding-top:12px"><a href="#" class="is-on">1</a><a href="#">2</a><a href="#">3</a><a href="#" aria-label="Next page">›</a></nav>
  </div>
</div></section>
''' + FOOTER

# =============================== PROJECT DETAIL ===============================
project = head('Project detail', 'Units, prices, amenities, location and the honest HouseRoot verdict on this Kolkata project.') + header() + f'''
<section class="inner stack" style="padding-top:16px;padding-bottom:40px;gap:24px">
  <span style="font-size:13px;color:#7A7A7A"><a href="index.html" style="color:#7A7A7A">Home</a> &nbsp;/&nbsp; <a href="projects.html" style="color:#7A7A7A">Projects</a> &nbsp;/&nbsp; <span style="color:#1A1A1A;font-weight:600" data-p="crumb">[Project name]</span></span>
  <div class="row" style="justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap">
    <div class="stack" style="gap:10px" data-reveal>
      <div class="row" style="gap:8px"><span class="tag" style="position:static" data-p="tag">New launch</span><span class="tag tag--white" style="position:static" data-p="rera">RERA [WB/XXXXX]</span></div>
      <h1 class="h-2" style="font-size:24px" data-p="name">[Project name]</h1>
      <span class="row" style="gap:8px;color:#6E6E6E">{ic('pin',18,'#F58220')}<span data-p="address">[Street / Block], New Town, Kolkata</span> · by <strong style="color:#1A1A1A" data-p="developer">[Developer]</strong></span>
    </div>
    <div class="stack" style="align-items:flex-end;gap:4px" data-reveal="right"><span style="font-size:13px;color:#8A8A8A;font-weight:600">Starting from</span><span style="font:700 24px var(--font-display);letter-spacing:-.02em;color:#F26B0E;line-height:1" data-p="price">₹[XX] L</span><span style="font-size:13px;color:#8A8A8A" data-p="psf">₹[X,XXX] / sq ft · all-inclusive quote on request</span></div>
  </div>
  <div class="gallery" data-stagger data-p="gallery">
    <div class="photo">Add elevation photo<button type="button" class="btn btn--sm btn--white" style="position:absolute;left:16px;bottom:16px">▶ Walkthrough video</button></div>
    <div class="photo">Add lobby / club photo</div>
    <div class="photo">Add sample flat photo<span class="pill" style="position:absolute;right:16px;bottom:16px;background:#1A1A1A;color:#fff;height:32px;padding:0 14px">+[XX] photos</span></div>
  </div>
</section>

<section class="section--white section--top-round"><div class="inner detail-layout" style="padding-top:48px;padding-bottom:80px">
  <div class="stack" style="gap:44px">
    <div class="facts" data-stagger data-p="facts"><div class="fact"><span>Configurations</span><strong>2, 3 BHK</strong></div><div class="fact"><span>Carpet area</span><strong>[XXX]–[XXXX] sq ft</strong></div><div class="fact"><span>Possession</span><strong>[Month Year]</strong></div><div class="fact"><span>Towers · floors</span><strong>[X] · G+[XX]</strong></div></div>
    <nav class="tabs" aria-label="Sections"><a href="#overview" class="is-on">Overview</a><a href="#units">Units &amp; prices</a><a href="#amenities">Amenities</a><a href="#location">Location</a><a href="#verdict">Our verdict</a></nav>
    <div id="overview" class="stack" style="gap:14px;max-width:680px" data-reveal data-p="about">
      <h2 class="h-3 h-3--section">About the project</h2>
      <p style="line-height:1.7;color:#4A4A4A">[Two or three sentences in HouseRoot's voice: who this project suits, what stands out on a site visit, and the one thing a buyer should know before booking.]</p>
      <p style="line-height:1.7;color:#4A4A4A">[Developer track record: previous projects delivered in Kolkata, typical delay history, construction quality notes.]</p>
    </div>
    <div id="units" class="stack" style="gap:16px" data-reveal>
      <h2 class="h-3 h-3--section">Units &amp; prices</h2>
      <div class="table-wrap"><table class="units"><thead><tr><th>Type</th><th>Carpet</th><th>Built-up</th><th>Facing</th><th>Price</th><th></th></tr></thead><tbody data-p="units">
        <tr><td style="font-weight:600">2 BHK</td><td>[XXX] sq ft</td><td>[XXXX] sq ft</td><td>East / North</td><td style="font-weight:700;color:#F26B0E">₹[XX] L</td><td><a href="contact.html" style="font-weight:700;font-size:13px">Floor plan →</a></td></tr>
        <tr><td style="font-weight:600">3 BHK</td><td>[XXXX] sq ft</td><td>[XXXX] sq ft</td><td>East / South</td><td style="font-weight:700;color:#F26B0E">₹[XX] L</td><td><a href="contact.html" style="font-weight:700;font-size:13px">Floor plan →</a></td></tr>
        <tr><td style="font-weight:600">3 BHK + study</td><td>[XXXX] sq ft</td><td>[XXXX] sq ft</td><td>Corner</td><td style="font-weight:700;color:#F26B0E">₹[X.X] Cr</td><td><a href="contact.html" style="font-weight:700;font-size:13px">Floor plan →</a></td></tr>
      </tbody></table></div>
      <p style="font-size:13px;color:#8A8A8A">Base price. GST, registration, parking and club charges quoted separately on request — we show you the all-in number before you decide.</p>
    </div>
    <div id="amenities" class="stack" style="gap:16px" data-reveal>
      <h2 class="h-3 h-3--section">Amenities</h2>
      <div class="amen" data-stagger data-p="amen">
        <div>{ic('home',22,'#F58220')}Clubhouse</div><div>{ic('check',22,'#F58220')}Swimming pool</div><div>{ic('check',22,'#F58220')}Gym</div><div>{ic('check',22,'#F58220')}24×7 security</div>
        <div>{ic('check',22,'#F58220')}Landscaped garden</div><div>{ic('check',22,'#F58220')}Covered parking</div><div>{ic('check',22,'#F58220')}Power backup</div><div>{ic('users',22,'#F58220')}Kids' play area</div>
      </div>
    </div>
    <div id="location" class="split split--start" style="gap:24px" data-reveal>
      <div class="stack" style="gap:16px"><h2 class="h-3 h-3--section">Location</h2><div style="background:var(--card);border-radius:20px;padding:6px 20px" data-p="near"><div class="near"><span>[Nearest metro] station</span><strong>[X.X] km</strong></div><div class="near"><span>[School name]</span><strong>[X.X] km</strong></div><div class="near"><span>[Hospital name]</span><strong>[X.X] km</strong></div><div class="near"><span>[IT hub / Sector V]</span><strong>[XX] min</strong></div><div class="near"><span>Airport</span><strong>[XX] min</strong></div></div></div>
      <div class="photo" style="height:300px" data-p="map">Embed map (Google Maps iframe)</div>
    </div>
    <div id="verdict" class="verdict" data-reveal="scale">
      <span class="eyebrow" style="color:#F7A200">HouseRoot verdict</span>
      <h2 class="h-2" data-p="goodfor">Good for: [end-users wanting metro access under ₹[XX] L]</h2>
      <div class="verdict__cols" style="display:grid;grid-template-columns:1fr 1fr;gap:24px">
        <div class="stack" style="gap:8px"><strong style="color:#7CD992;font-size:14px">What we liked</strong><ul data-p="liked"><li>[Point]</li><li>[Point]</li><li>[Point]</li></ul></div>
        <div class="stack" style="gap:8px"><strong style="color:#F7A200;font-size:14px">Watch out for</strong><ul data-p="watch"><li>[Point]</li><li>[Point]</li></ul></div>
      </div>
      <span style="font-size:13px;color:#8A8A8A" data-p="walked">Walked by [Advisor name], [Month Year]. We're paid by the developer; our verdict is still ours.</span>
    </div>
  </div>
  <aside class="sticky-card" data-reveal="right">
    <div class="advisor"><span class="advisor__pic" data-p="advpic">[AD]</span><div class="stack"><strong style="font:600 16px var(--font-display)" data-p="advisor">[Advisor name]</strong><span style="font-size:13px;color:#7A7A7A">Your HouseRoot advisor · replies in minutes</span></div></div>
    <form class="stack" style="gap:12px" data-lead>
      <label class="sr-only" for="d-name">Name</label><input class="input" id="d-name" type="text" placeholder="Your name" required>
      <label class="sr-only" for="d-phone">Phone</label><input class="input" id="d-phone" type="tel" placeholder="+91 phone" required>
      <label class="sr-only" for="d-type">Interested in</label><select class="select" id="d-type" data-p="unitselect"><option>Interested in: 2 BHK</option><option>Interested in: 3 BHK</option><option>Interested in: 3 BHK + study</option></select>
      <button type="submit" class="btn btn--block">Book a free site visit</button>
      <a href="https://wa.me/919230592846" class="btn btn--block btn--outline">{ic('wa',18,'#25A05A')} Chat on WhatsApp</a>
      {SUCCESS}
    </form>
    <div class="stack" style="gap:8px;padding-top:12px;border-top:1px solid #EFEFEF;font-size:13px;color:#5A5A5A;line-height:1.5"><span>✓ Free pick-up &amp; drop for site visits</span><span>✓ Zero brokerage — developer pays us</span><span>✓ Home-loan help from [X] partner banks</span></div>
    <a href="contact.html" style="font-size:13px;font-weight:600;text-align:center">Download brochure (PDF)</a>
  </aside>
</div></section>

<section class="section section--card"><div class="inner stack" style="gap:28px">
  <div class="row" style="justify-content:space-between;align-items:flex-end" data-reveal><h2 class="h-2">Similar projects nearby</h2><a href="projects.html" class="link">See all {ic('arrow',16)}</a></div>
  <div class="grid-3" data-stagger data-similar-grid>
    {pcard('[Project name]','New Town','[Developer]',['2 &amp; 3 BHK','RERA ✓'],'₹[XX] L+')}
    {pcard('[Project name]','Rajarhat','[Developer]',['3 BHK','RERA ✓'],'₹[XX] L+','Under construction','tag--white')}
    {pcard('[Project name]','Salt Lake','[Developer]',['2 BHK','RERA ✓'],'₹[XX] L+','Ready to move','tag--dark')}
  </div>
</div></section>
''' + FOOTER

# =============================== ABOUT ===============================
about = head('About', 'HouseRoot is the friend who has walked every site — a RERA-registered channel partner from Kolkata, by Flint De Orient.', path='about.html') + header() + f'''
<section class="inner split" style="padding-top:40px;padding-bottom:64px">
  <div class="stack" style="gap:24px" data-reveal="left">
    <div class="rule"></div>
    <h1 class="h-1 words">We're the friend <span class="muted">who has</span> walked every site.</h1>
    <p class="lede" style="font-size:16px;max-width:520px">HouseRoot is a RERA-registered real estate channel partner from Kolkata. Developers pay us to bring them serious buyers; buyers get an advisor who has seen every project in the city — at the same price, with no brokerage.</p>
    <div class="row" style="gap:12px;flex-wrap:wrap"><a href="projects.html" class="btn">Browse projects</a><a href="#team" class="btn btn--outline">Meet the team</a></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;height:520px" data-stagger>
    <div class="photo" style="grid-row:1 / span 2">Add photo — team on a site visit</div>
    <div class="photo">Add photo — office</div>
    <div style="border-radius:24px;background:linear-gradient(135deg,#F7A200,#F26B0E);color:#fff;padding:24px;display:flex;flex-direction:column;justify-content:flex-end;gap:4px"><strong style="font:700 24px var(--font-display);letter-spacing:-.02em;line-height:1">Est. [Year]</strong><span style="font-size:14px;opacity:.9">Kolkata · by Flint De Orient</span></div>
  </div>
</section>
<section class="section section--white section--top-round"><div class="inner">
  <div class="kpis" data-stagger><div class="kpi"><strong><span data-count="40" data-suffix="+">0</span></strong><span>Projects we partner on</span></div><div class="kpi"><strong><span data-count="300">0</span></strong><span>Families moved in</span></div><div class="kpi"><strong><span data-count="18">0</span></strong><span>Developer partners</span></div><div class="kpi"><strong>₹0</strong><span>Brokerage charged to buyers</span></div></div>
</div></section>
<section class="section--white"><div class="inner split" style="padding-bottom:80px">
  <div class="photo" style="height:440px" data-reveal="left">Add photo — founder / advisor with a client</div>
  <div class="stack" style="gap:18px" data-reveal="right">
    <span class="eyebrow">Our story</span>
    <h2 class="h-2">Built because buying a flat in Kolkata shouldn't take ten brokers and a hundred calls.</h2>
    <p style="line-height:1.7;color:#4A4A4A">[Two paragraphs in the founder's voice: what went wrong on your own home search, why a channel partner model fixes it, and what HouseRoot promises — one advisor, honest comparisons, the all-in number before you book.]</p>
    <p style="line-height:1.7;color:#4A4A4A">HouseRoot is the real estate arm of <a href="https://flintdeorient.in" target="_blank" rel="noopener">Flint De Orient Marketing &amp; Technology</a>, so every enquiry runs on our own CRM and WhatsApp automation — no lead is ever lost in a spreadsheet.</p>
  </div>
</div></section>
<section class="section section--card"><div class="inner stack" style="gap:36px">
  <div class="stack" style="gap:12px;max-width:640px" data-reveal><div class="rule"></div><h2 class="h-2">How we work</h2></div>
  <div class="grid-3" data-stagger>
    <div class="value"><span class="value__n">01</span><h3 class="h-4">Fewer projects, verified</h3><p>We list only projects our team has walked — RERA, approvals, possession history and pricing checked before they appear here.</p></div>
    <div class="value"><span class="value__n">02</span><h3 class="h-4">The all-in number, upfront</h3><p>GST, registration, parking, club charges — you see the real total before you fall in love with a floor plan.</p></div>
    <div class="value"><span class="value__n">03</span><h3 class="h-4">One advisor, start to keys</h3><p>The person who takes your first call drives you to the site, negotiates, and checks the flat at possession. No hand-offs.</p></div>
  </div>
</div></section>
<section class="section section--white"><div class="inner split split--start">
  <div class="stack" style="gap:16px;position:sticky;top:110px" data-reveal="left"><div class="rule"></div><h2 class="h-2">From first call to possession</h2><p class="lede">Most buyers go from brief to booking in 3–6 weeks. We stay until you've moved in.</p></div>
  <div class="stack" style="gap:16px" data-stagger>
    <div class="step"><span class="step__n">1</span><div class="stack" style="gap:4px"><strong style="font:600 16px var(--font-display)">A 15-minute brief</strong><span style="font-size:14px;line-height:1.55;color:#5A5A5A">Budget, locality, timeline, what matters — schools, metro, Vastu, rental yield.</span></div></div>
    <div class="step"><span class="step__n">2</span><div class="stack" style="gap:4px"><strong style="font:600 16px var(--font-display)">A shortlist of 3–5</strong><span style="font-size:14px;line-height:1.55;color:#5A5A5A">With a plain comparison: price per sq ft, carpet vs built-up, hidden charges, delay risk.</span></div></div>
    <div class="step"><span class="step__n">3</span><div class="stack" style="gap:4px"><strong style="font:600 16px var(--font-display)">Site visits, then negotiation</strong><span style="font-size:14px;line-height:1.55;color:#5A5A5A">Free pick-up and drop. We use our developer relationships to get you the best available offer.</span></div></div>
    <div class="step"><span class="step__n">4</span><div class="stack" style="gap:4px"><strong style="font:600 16px var(--font-display)">Loan, paperwork, possession</strong><span style="font-size:14px;line-height:1.55;color:#5A5A5A">Bank tie-ups, agreement review, registration and a possession snag-list.</span></div></div>
  </div>
</div></section>
<section class="section section--card" id="team"><div class="inner stack" style="gap:36px">
  <div class="row" style="justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap" data-reveal><div class="stack" style="gap:12px"><div class="rule"></div><h2 class="h-2">The advisors</h2></div><a href="contact.html" class="link">We're hiring {ic('arrow',16)}</a></div>
  <div class="grid-4" data-stagger>
    <div class="member"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:14px;color:#7A7A7A">Founder · [X] yrs in Kolkata real estate</span></div></div>
    <div class="member"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:14px;color:#7A7A7A">Senior advisor · New Town &amp; Rajarhat</span></div></div>
    <div class="member"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:14px;color:#7A7A7A">Advisor · South Kolkata</span></div></div>
    <div class="member"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:14px;color:#7A7A7A">Home-loan &amp; documentation</span></div></div>
  </div>
</div></section>
<section class="section section--ember"><div class="inner row" style="justify-content:space-between;gap:32px;flex-wrap:wrap" data-reveal>
  <div class="stack" style="gap:8px;max-width:620px"><h2 class="h-2">Ready to start? Tell us your brief.</h2><span style="opacity:.92">We'll call within the hour, on a weekday.</span></div>
  <a href="contact.html" class="btn btn--white">Talk to an advisor</a>
</div></section>
''' + FOOTER

# =============================== DEVELOPERS ===============================
developers = head('For developers', 'List your Kolkata project with HouseRoot: qualified buyers, a live pipeline dashboard and WhatsApp automation — pay per registered booking.', dark=True, path='developers.html') + header(dark=True) + f'''
<section class="inner" style="padding-top:40px;padding-bottom:72px;position:relative">
  <div class="chevron-bg" style="right:-200px;top:-120px"></div>
  <div class="split" style="position:relative">
    <div class="stack" style="gap:24px" data-reveal="left">
      <span class="eyebrow">For developers &amp; owners</span>
      <h1 class="h-1 words" style="color:#fff">Inventory moves faster <span class="muted">with a partner who</span> brings buyers, not leads.</h1>
      <p class="lede" style="font-size:16px;max-width:520px;color:#B9B2AA">HouseRoot is the real estate arm of Flint De Orient — a technology company. Every enquiry runs through our own CRM, WhatsApp automation and performance marketing, and you see the pipeline live.</p>
      <div class="row" style="gap:12px;flex-wrap:wrap"><a href="#partner" class="btn">List your project</a><a href="#partner" class="btn btn--ghost">Download partner deck</a></div>
    </div>
    <div class="dash" data-reveal="right">
      <div class="row" style="justify-content:space-between"><strong style="font:600 16px var(--font-display)">Live pipeline · [Project name]</strong><span class="pill" style="background:#E8F7EC;color:#1E7A3C"><span class="live-dot"></span>Live</span></div>
      <div class="dash__kpis"><div class="dash__kpi"><span>Leads</span><strong><span data-count="312">0</span></strong></div><div class="dash__kpi"><span>Qualified</span><strong><span data-count="86">0</span></strong></div><div class="dash__kpi"><span>Visits</span><strong><span data-count="41">0</span></strong></div><div class="dash__kpi dash__kpi--hot"><span>Bookings</span><strong><span data-count="9">0</span></strong></div></div>
      <div>
        <div class="dash__row dash__head" style="border:0"><span>Buyer</span><span>Budget</span><span>Stage</span><span>Advisor</span></div>
        <div class="dash__row"><span style="font-weight:600">[Buyer name]</span><span>₹[XX] L</span><span class="pill" style="background:#FFE6D2;color:#B84A00">Site visit</span><span style="color:#6E6E6E">[Name]</span></div>
        <div class="dash__row"><span style="font-weight:600">[Buyer name]</span><span>₹[XX] L</span><span class="pill" style="background:#E8F7EC;color:#1E7A3C">Booked</span><span style="color:#6E6E6E">[Name]</span></div>
        <div class="dash__row"><span style="font-weight:600">[Buyer name]</span><span>₹[X.X] Cr</span><span class="pill" style="background:#EEF2FF;color:#3B4CC0">Negotiating</span><span style="color:#6E6E6E">[Name]</span></div>
        <div class="dash__row"><span style="font-weight:600">[Buyer name]</span><span>₹[XX] L</span><span class="pill" style="background:#F4F4F4;color:#5A5A5A">Nudged · WhatsApp</span><span style="color:#6E6E6E">Auto</span></div>
      </div>
      <span style="font-size:12px;color:#8A8A8A">Illustrative dashboard — you get a login to the real one on day one.</span>
    </div>
  </div>
</section>
<section class="inner" style="padding-bottom:72px"><div class="kpis kpis--dark" data-stagger>
  <div class="kpi"><strong>[XX]%</strong><span>of site visits from HouseRoot leads convert to a booking</span></div>
  <div class="kpi"><strong>[X] days</strong><span>average lead-to-visit time, with free pick-up &amp; drop</span></div>
  <div class="kpi"><strong>[XX]+</strong><span>projects partnered across Kolkata &amp; fringes</span></div>
</div></section>
<section class="section section--card section--top-round" style="color:#1A1A1A"><div class="inner stack" style="gap:36px">
  <div class="stack" style="gap:12px;max-width:640px" data-reveal><div class="rule"></div><h2 class="h-2">What a HouseRoot partnership includes</h2></div>
  <div class="grid-3" data-stagger>
    <div class="svc"><span class="svc__ic">{ic('list',24,'#D14F00')}</span><h3 class="h-4">Qualified leads only</h3><p>Budget, intent and timeline verified by an advisor before a visit is booked. Your sales team meets buyers, not browsers.</p></div>
    <div class="svc"><span class="svc__ic">{ic('grid',24,'#D14F00')}</span><h3 class="h-4">Live pipeline dashboard</h3><p>Every lead, visit and booking in real time — shared transparently, exportable, no monthly PDF reports.</p></div>
    <div class="svc"><span class="svc__ic">{ic('refresh',24,'#D14F00')}</span><h3 class="h-4">WhatsApp re-engagement</h3><p>Cold leads nudged automatically with offers, construction updates and walkthrough videos until they're ready.</p></div>
    <div class="svc"><span class="svc__ic">{ic('layers',24,'#D14F00')}</span><h3 class="h-4">Launch campaigns</h3><p>Pre-launch EOI drives, broker meets and Meta/Google campaigns — run by Flint De Orient's performance team.</p></div>
    <div class="svc"><span class="svc__ic">{ic('video',24,'#D14F00')}</span><h3 class="h-4">Content &amp; walkthroughs</h3><p>Site videos, drone shots and sample-flat tours, cut for Instagram, YouTube and WhatsApp — included.</p></div>
    <div class="svc"><span class="svc__ic">{ic('check',24,'#D14F00')}</span><h3 class="h-4">Clean paperwork</h3><p>RERA-compliant disclosures, agreement support and a possession snag-list — fewer disputes, happier owners.</p></div>
  </div>
</div></section>
<section class="section section--white" style="color:#1A1A1A"><div class="inner stack" style="gap:36px">
  <div class="stack" style="gap:12px;max-width:640px" data-reveal><div class="rule"></div><h2 class="h-2">From onboarding to sold out</h2></div>
  <div class="flow" data-stagger>
    <div><span class="n">01</span><strong>Project walkthrough</strong><span>Our advisors visit, verify approvals and build the HouseRoot verdict.</span></div>
    <div><span class="n">02</span><strong>Listing &amp; content</strong><span>Live on HouseRoot in 48 hours with photos, pricing and walkthrough video.</span></div>
    <div><span class="n">03</span><strong>Campaigns on</strong><span>Performance ads, broker network and WhatsApp broadcasts start.</span></div>
    <div><span class="n">04</span><strong>Visits &amp; bookings</strong><span>Qualified buyers at your site; bookings logged live on your dashboard.</span></div>
    <div><span class="n">05</span><strong>Settlement</strong><span>Brokerage invoiced per registered booking — nothing upfront.</span></div>
  </div>
</div></section>
<section class="section section--card" style="color:#1A1A1A"><div class="inner split">
  <div class="photo" style="height:360px" data-reveal="left">Add photo — resale flat / owner handing keys</div>
  <div class="stack" style="gap:16px" data-reveal="right"><span class="eyebrow">Individual owners</span><h2 class="h-2">Selling or renting one flat? We take those too.</h2><p class="lede">Fair valuation from recent transactions, professional photos, verified tenants or buyers, and agreement support. Brokerage only on a closed deal.</p><a href="contact.html" class="btn btn--dark" style="align-self:flex-start">Get a free valuation</a></div>
</div></section>
<section class="section section--ember" id="partner"><div class="inner split split--start">
  <div class="stack" style="gap:18px" data-reveal="left">
    <h2 class="h-2">Let's talk about your project.</h2>
    <p class="lede" style="max-width:460px">Tell us what you're launching. Our partnerships lead will reply within one working day with a proposal and references from developers we already work with.</p>
    <div class="stack" style="gap:8px;font-size:15px;font-weight:600"><span>✓ No upfront fee — pay per registered booking</span><span>✓ Live dashboard access from day one</span><span>✓ RERA-compliant marketing, always</span></div>
  </div>
  <form class="glass-form" data-lead data-reveal="right">
    <div class="form-grid"><div class="field"><label class="label" for="p-co">Company</label><input class="input" id="p-co" type="text" placeholder="Developer / owner name" required></div><div class="field"><label class="label" for="p-name">Contact person</label><input class="input" id="p-name" type="text" placeholder="Your name" required></div></div>
    <div class="form-grid"><div class="field"><label class="label" for="p-phone">Phone</label><input class="input" id="p-phone" type="tel" placeholder="+91" required></div><div class="field"><label class="label" for="p-type">I want to</label><select class="select" id="p-type"><option>List a new project</option><option>Sell remaining inventory</option><option>Sell / rent one property</option><option>Pre-launch campaign</option></select></div></div>
    <div class="field"><label class="label" for="p-msg">Project details</label><textarea class="textarea" id="p-msg" rows="3" placeholder="Location, units, price band, launch date…"></textarea></div>
    <button type="submit" class="btn btn--block btn--dark">Request a proposal</button>
    {SUCCESS.replace("we'll call you within the hour", "our partnerships lead will reply within one working day").replace("Weekdays 10 am – 7 pm. Or WhatsApp us anytime.", "Check your inbox for a confirmation.")}
  </form>
</div></section>
''' + FOOTER

# =============================== CONTACT ===============================
contact = head('Contact', 'Tell HouseRoot what you are looking for — we call back within the hour on weekdays. WhatsApp, phone, email or visit our Kolkata office.', path='contact.html') + header() + f'''
<section class="inner split split--start" style="padding-top:40px;padding-bottom:72px">
  <div class="stack" style="gap:28px" data-reveal="left">
    <div class="rule"></div>
    <h1 class="h-1 words">Tell us <span class="muted">what you're</span> looking for.</h1>
    <p class="lede" style="font-size:16px;max-width:460px">We call back within the hour on weekdays, 10 am – 7 pm. Or skip the form — most of our conversations start on WhatsApp.</p>
    <div class="stack" style="gap:14px">
      <a href="https://wa.me/919230592846" class="btn btn--dark" style="align-self:flex-start">{ic('wa',18,'#7CD992')} WhatsApp +91 92305 92846</a>
      <a href="tel:+919230592846" class="contact-line" style="gap:10px">{ic('phone',18,'#F26B0E')}Call +91 92305 92846</a>
      <a href="mailto:sales@houseroot.in" class="contact-line" style="gap:10px">{ic('mail',18,'#F26B0E')}sales@houseroot.in</a>
    </div>
    <div class="stack" style="gap:8px;padding-top:12px;border-top:1px solid #E6E6E6;max-width:460px"><strong style="font:600 15px var(--font-display)">Visit the office</strong><span style="line-height:1.6;color:#5A5A5A">[Office address line 1]<br>[Line 2], Kolkata – [PIN]<br>Mon–Sat · 10 am – 7 pm</span><a href="https://maps.google.com" target="_blank" rel="noopener" style="font-size:14px;font-weight:700">Open in Google Maps →</a></div>
  </div>
  <form class="form-card" id="form" data-lead data-reveal="right">
    <div class="stack" style="gap:10px"><span class="label">I want to</span><div class="seg seg--sm" role="group" aria-label="I want to"><button type="button" class="is-on">Buy</button><button type="button">Rent</button><button type="button">Sell</button><button type="button">Invest</button></div></div>
    <div class="form-grid"><div class="field"><label class="label" for="c-name">Your name</label><input class="input" id="c-name" type="text" placeholder="Priya Sen" required></div><div class="field"><label class="label" for="c-phone">Phone</label><input class="input" id="c-phone" type="tel" placeholder="+91" required></div></div>
    <div class="form-grid"><div class="field"><label class="label" for="c-loc">Preferred area</label><select class="select" id="c-loc"><option>Anywhere in Kolkata</option><option>New Town &amp; Rajarhat</option><option>Salt Lake</option><option>EM Bypass</option><option>Joka &amp; Behala</option><option>Howrah</option></select></div><div class="field"><label class="label" for="c-bud">Budget</label><select class="select" id="c-bud"><option>Under ₹50 L</option><option>₹50 L – ₹1 Cr</option><option>₹1 – 2 Cr</option><option>₹2 Cr +</option></select></div></div>
    <div class="form-grid"><div class="field"><label class="label" for="c-type">Type</label><select class="select" id="c-type"><option>2 BHK</option><option>3 BHK</option><option>4 BHK+</option><option>Villa</option><option>Plot</option><option>Commercial</option></select></div><div class="field"><label class="label" for="c-when">Timeline</label><select class="select" id="c-when"><option>Within 3 months</option><option>3–6 months</option><option>6–12 months</option><option>Just exploring</option></select></div></div>
    <div class="field"><label class="label" for="c-msg">Anything else? <span style="font-weight:500;color:#9A9A9A">(optional)</span></label><textarea class="textarea" id="c-msg" rows="3" placeholder="Near a metro, east-facing, school within 2 km…"></textarea></div>
    <button type="submit" class="btn btn--block">Request a call back</button>
    <p class="form-note">No spam. Your number isn't shared with developers until you say so.</p>
    {SUCCESS}
  </form>
</section>
<section class="section section--white section--top-round"><div class="inner stack" style="gap:28px">
  <h2 class="h-2" data-reveal>Other ways to reach us</h2>
  <div class="grid-3" data-stagger>
    <a href="projects.html" class="way"><span class="way__ic">{ic('cal',22,'#fff')}</span><strong class="h-4" style="font-size:16px">Book a site visit</strong><span>Pick a project, pick a slot — free pick-up and drop across Kolkata, weekends included.</span></a>
    <a href="developers.html" class="way"><span class="way__ic">{ic('doc',22,'#fff')}</span><strong class="h-4" style="font-size:16px">Developer partnerships</strong><span>Launching a project? Talk to our partnerships lead about listing and campaigns.</span></a>
    <a href="mailto:sales@houseroot.in" class="way"><span class="way__ic">{ic('users',22,'#fff')}</span><strong class="h-4" style="font-size:16px">Careers</strong><span>We're hiring advisors who'd rather walk a site than cold-call. Send your CV.</span></a>
  </div>
</div></section>
<section class="section section--card" id="agents"><div class="inner stack" style="gap:32px">
  <div class="row" style="justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap" data-reveal>
    <div class="stack" style="gap:12px;max-width:600px"><div class="rule"></div><h2 class="h-2">Find your advisor</h2><p class="lede">Each advisor covers a few localities deeply. Pick the one for your area, or let us match you.</p></div>
    <div class="seg seg--sm" role="group" aria-label="Area" data-agent-filter><button type="button" class="is-on" data-value="all">All</button><button type="button" data-value="new town">New Town</button><button type="button" data-value="south">South</button><button type="button" data-value="salt lake">Salt Lake</button><button type="button" data-value="howrah">Howrah</button></div>
  </div>
  <div class="grid-4" data-stagger>
    <div class="agent" data-area="new town"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:13px;color:#7A7A7A">New Town &amp; Rajarhat · [X] yrs</span></div><span style="font-size:13px;color:#5A5A5A">Speaks Bengali, Hindi, English</span><a href="https://wa.me/919230592846" class="btn btn--sm btn--dark">WhatsApp</a></div>
    <div class="agent" data-area="south"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:13px;color:#7A7A7A">EM Bypass &amp; South · [X] yrs</span></div><span style="font-size:13px;color:#5A5A5A">Speaks Bengali, Hindi, English</span><a href="https://wa.me/919230592846" class="btn btn--sm btn--dark">WhatsApp</a></div>
    <div class="agent" data-area="salt lake"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:13px;color:#7A7A7A">Salt Lake &amp; Sector V · [X] yrs</span></div><span style="font-size:13px;color:#5A5A5A">Speaks Bengali, Hindi, English</span><a href="https://wa.me/919230592846" class="btn btn--sm btn--dark">WhatsApp</a></div>
    <div class="agent" data-area="howrah south"><div class="photo">Add headshot</div><div class="stack" style="gap:2px"><strong style="font:600 16px var(--font-display)">[Name]</strong><span style="font-size:13px;color:#7A7A7A">Howrah &amp; Joka · [X] yrs</span></div><span style="font-size:13px;color:#5A5A5A">Speaks Bengali, Hindi, English</span><a href="https://wa.me/919230592846" class="btn btn--sm btn--dark">WhatsApp</a></div>
  </div>
</div></section>
<section class="section section--white"><div class="inner" style="display:grid;grid-template-columns:1fr 1.4fr;gap:56px;align-items:start" id="faq-grid">
  <div class="stack" style="gap:12px" data-reveal="left"><div class="rule"></div><h2 class="h-2">Before you call</h2><p class="lede">The questions every first-time buyer asks us.</p></div>
  <div class="faq stack" style="gap:10px;background:var(--card);border-radius:28px;padding:14px" data-reveal="right">
    <details open><summary>Do I really pay nothing extra?</summary><div class="faq__body"><p>On new launches, yes — the developer pays our commission and your price is the same as walking in directly (often better, because we negotiate for you). On resale, standard brokerage applies and we tell you the number upfront.</p></div></details>
    <details><summary>Will you push the projects that pay you more?</summary><div class="faq__body"><p>Our advisors are not paid per project. Every verdict on our site lists what we didn't like, too. If none of our partner projects fit, we'll say so.</p></div></details>
    <details><summary>Can you help with the home loan?</summary><div class="faq__body"><p>Yes — we work with [X] partner banks and NBFCs, compare rates for you and handle the paperwork. Pre-approval usually takes 3–5 working days.</p></div></details>
    <details><summary>What if the project gets delayed?</summary><div class="faq__body"><p>We only list RERA-registered projects, and we show you the developer's delivery history before you book. If a delay happens, we help you with the RERA process.</p></div></details>
  </div>
</div></section>
<style>@media (max-width:1100px){{#faq-grid{{grid-template-columns:1fr!important}}}}</style>
''' + FOOTER


# =============================== BLOG ===============================
BLOG_BODY = '''<section class="inner stack" style="padding-top:40px;padding-bottom:56px;gap:36px">
  <div class="stack" style="gap:12px;max-width:640px" data-reveal>
    <span class="eyebrow">Blog</span>
    <h1 class="h-2">Notes from the field</h1>
    <p class="lede">Locality comparisons, what to check before booking, and what we learn walking Kolkata's projects every week.</p>
  </div>
  <div class="blog-grid" data-blog-list><p class="lede">Loading posts…</p></div>
</section>

'''
POST_BODY = '''<section class="inner" style="padding-top:40px;padding-bottom:72px">
  <article class="post stack" style="gap:28px" data-post><p class="lede">Loading…</p></article>
</section>

'''
blog = head('Blog', 'Locality comparisons, buying checklists and field notes from HouseRoot, Kolkata.', path='blog.html') + header() + BLOG_BODY + FOOTER
post = head('Blog post', 'A HouseRoot blog post.') + header() + POST_BODY + FOOTER

# =============================== LOCATION PAGES ===============================
def loc_page(file, name, full_title, desc, keywords, h1, eyebrow, intro, alt, sections, grid_h2, grid_intro, terms, faqs):
    others = ' · '.join(f'<a href="{f}" class="link">{n}</a>' for f, n in LOCATIONS if f != file)
    body_html = '\n'.join(f'    <h2 class="h-3" style="font-size:20px;margin-top:12px">{h}</h2>\n' + '\n'.join(f'    <p>{p}</p>' for p in ps) for h, ps in sections)
    faq_html = '\n'.join(f'    <details{" open" if i == 0 else ""}><summary>{q}</summary><div class="faq__body"><p>{a}</p></div></details>' for i, (q, a) in enumerate(faqs))
    schema = jsonld({'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': name, 'item': f'{SITE}/{file}'}]},
        {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]},
    ]})
    return head(name, desc, path=file, full_title=full_title, keywords=keywords, schema=schema) + header() + f'''
<section class="inner split" style="padding-top:40px;padding-bottom:64px">
  <div class="stack" style="gap:22px" data-reveal="left">
    <span style="font-size:13px;color:#7A7A7A"><a href="index.html" style="color:#7A7A7A">Home</a> &nbsp;/&nbsp; <span style="color:#1A1A1A;font-weight:600">{name}</span></span>
    <span class="eyebrow">{eyebrow}</span>
    <h1 class="h-1">{h1}</h1>
    <p class="lede" style="max-width:540px">{intro}</p>
    <div class="row" style="gap:12px;flex-wrap:wrap"><a href="#projects" class="btn">See projects</a><a href="contact.html" class="btn btn--outline">Talk to an advisor</a></div>
  </div>
  <div class="photo" style="height:420px" data-reveal="right"><picture style="display:block;width:100%;height:100%"><source srcset="assets/img/hero-model.webp" type="image/webp"><img src="assets/img/hero-model.jpg" alt="{alt}" width="2200" height="1228"></picture></div>
</section>
<section class="section section--white section--top-round"><div class="inner">
  <div class="prose" style="max-width:780px;margin:0 auto" data-reveal>
{body_html}
  </div>
</div></section>
<section class="section section--card" id="projects"><div class="inner stack" style="gap:36px">
  <div class="stack" style="gap:14px;align-items:center;text-align:center" data-reveal><div class="rule"></div><h2 class="h-2">{grid_h2}</h2><p class="lede" style="max-width:620px">{grid_intro}</p></div>
  <div class="grid-3" data-stagger data-loc-grid="{terms}">
    <div class="value" style="grid-column:1 / -1;align-items:center;text-align:center"><h3 class="h-4">Verified projects in {name} are being added</h3><p>Ask an advisor for today's shortlist with prices, RERA numbers and possession dates.</p><a href="contact.html" class="btn btn--sm">Get the shortlist</a></div>
  </div>
</div></section>
<section class="section section--white"><div class="inner split split--start">
  <div class="stack" style="gap:16px" data-reveal="left"><div class="rule"></div><h2 class="h-2">Questions buyers ask about {name}</h2><p class="lede">Also compare: {others}</p></div>
  <div class="faq stack" style="gap:10px;background:var(--card);border-radius:28px;padding:14px" data-reveal="right">
{faq_html}
  </div>
</div></section>
<section class="section section--ember"><div class="inner row" style="justify-content:space-between;gap:32px;flex-wrap:wrap" data-reveal>
  <div class="stack" style="gap:8px;max-width:620px"><h2 class="h-2">Looking in {name}? Tell us your brief.</h2><span style="opacity:.92">We'll call within the hour on weekdays. Zero brokerage on new launches.</span></div>
  <a href="contact.html" class="btn btn--white">Talk to an advisor</a>
</div></section>
''' + FOOTER

FAQ_BROKERAGE = ('Do I pay brokerage on new launches?', 'No. On new launches the developer pays our fee, so your price is the same as booking directly, and we negotiate on your behalf.')
FAQ_RERA = ('How do I check a project\'s RERA registration?', 'Every project we list has a West Bengal RERA (WBRERA) registration number. We share it with you, and you can verify it on the WBRERA website before you book.')

new_town = loc_page('new-town.html', 'New Town',
    'Upcoming Luxury Projects in New Town Kolkata | HouseRoot',
    'Upcoming luxury projects in New Town Kolkata, verified by HouseRoot: 2 & 3 BHK flats in gated high-rises, RERA checked, with zero brokerage.',
    ['Upcoming luxury projects in New Town Kolkata', 'Upcoming residential projects New Town', 'Luxury apartments in New Town Kolkata', 'Premium flats in New Town', 'Upcoming 2 BHK flats in New Town', 'Upcoming 3 BHK flats in New Town', 'Luxury 2 BHK apartments New Town', 'Luxury 3 BHK apartments New Town', 'New launch residential projects New Town', 'Premium gated community New Town', 'High-rise luxury apartments New Town'],
    'Upcoming luxury projects in New Town Kolkata', 'New Town · East Kolkata',
    'New Town is where much of Kolkata\'s new housing is being built: a planned township on the city\'s eastern edge with wide roads and offices a short drive away. These are the upcoming luxury projects in New Town Kolkata our team has visited, with honest notes on price, possession and build quality.',
    'Architectural model of a modern multi-storey residence on blueprints, illustrating new luxury homes in New Town, Kolkata',
    [('Luxury apartments in New Town Kolkata', [
        'New Town was planned from scratch, and it shows. Action Areas I, II and III are laid out around Biswa Bangla Sarani and the Major Arterial Road, so most new towers have proper approach roads, drainage and space between buildings. Eco Park, Tata Medical Center, well-known schools and the IT offices of New Town and Salt Lake Sector V are within a short drive, and the airport is closer than from most of the city.',
        'That planning is why many buyers start their search here. The upcoming residential projects New Town developers are launching now lean towards larger floor plates, full clubhouses, and touches like double-height lobbies and EV charging. Premium flats in New Town still cost less per square foot than comparable homes in central and south Kolkata, which keeps the area popular with families and investors alike.']),
     ('Upcoming 2 BHK flats in New Town', [
        'A two-bedroom home is the most common first purchase we help with here. Upcoming 2 BHK flats in New Town vary a lot in size and finish from tower to tower, so we compare them on carpet area rather than super built-up area. If you want a step up, the luxury 2 BHK apartments New Town developers are building now add larger balconies, branded fittings and a club with a pool and gym.']),
     ('Upcoming 3 BHK flats in New Town', [
        'Families planning for school years, or parents moving in, usually look at three bedrooms. Upcoming 3 BHK flats in New Town are offered in mid-segment towers and at the top end, where the luxury 3 BHK apartments New Town is known for come with staff rooms, separate utility areas and higher floors with open views. Before you shortlist, we check orientation, ceiling height, lifts per tower and the real monthly maintenance.']),
     ('Premium gated community homes in New Town', [
        'Most new launches are planned as a premium gated community New Town families can live in with security, landscaped greens and amenities inside one boundary wall. High-rise luxury apartments New Town projects are increasingly built over podium parking, so the ground level stays car-free for children and walkers. A larger community spreads maintenance costs across more homes, but also means more neighbours sharing the pool and the lifts, and we help you weigh both.'])],
    'New launch residential projects in New Town',
    'We add the new launch residential projects New Town developers announce only after our team has visited the site and checked its RERA registration. Prices change quickly, so call before you visit.',
    'new town|newtown',
    [('Is New Town a good place to buy a home?', 'For most buyers who work in New Town or Salt Lake Sector V, yes. Roads, water and power were planned for the township, and new schools, hospitals and shops keep opening. Some pockets are still developing, so the exact block matters more than the area name.'),
     FAQ_BROKERAGE, FAQ_RERA])

rajarhat = loc_page('rajarhat.html', 'Rajarhat',
    'Upcoming Luxury Projects in Rajarhat Kolkata | HouseRoot',
    'Upcoming luxury projects in Rajarhat Kolkata near the airport: RERA-checked 2 & 3 BHK flats in gated high-rises. Zero brokerage with HouseRoot.',
    ['Upcoming luxury projects in Rajarhat Kolkata', 'Upcoming residential projects in Rajarhat', 'Luxury flats in Rajarhat Kolkata', 'Premium apartments in Rajarhat', 'Upcoming 2 BHK projects in Rajarhat', 'Upcoming 3 BHK projects in Rajarhat', 'Luxury 2 BHK flats in Rajarhat', 'Luxury 3 BHK flats in Rajarhat', 'New launch projects in Rajarhat', 'Premium high-rise apartments Rajarhat', 'RERA registered upcoming projects Rajarhat', 'Luxury gated community in Rajarhat'],
    'Upcoming luxury projects in Rajarhat Kolkata', 'Rajarhat · Near the airport',
    'Rajarhat sits between the airport and New Town, and over the last two decades it has grown from open land into one of Kolkata\'s busiest residential belts. These are the upcoming luxury projects in Rajarhat Kolkata our advisors are tracking, with straight answers on price, possession and travel times.',
    'Scale model of a contemporary luxury home on architect\'s drawings, representing new homes in Rajarhat, Kolkata',
    [('Luxury flats in Rajarhat Kolkata', [
        'The appeal is simple. The airport, VIP Road and the offices of New Town are all close, but land here has usually cost less than in the core township. That lets developers plan larger sites with more open area, and it means luxury flats in Rajarhat Kolkata often give you more space for the same budget. Chinar Park, Rajarhat Main Road and the stretch towards the airport are where most of the activity is.',
        'Upcoming residential projects in Rajarhat range from mid-rise blocks to tall towers, and some are part of larger townships with retail and schools inside the campus. Premium apartments in Rajarhat tend to sit in these bigger developments, where the clubhouse, sports courts and green space are shared across many towers.']),
     ('Upcoming 2 BHK projects in Rajarhat', [
        'For young couples and first-time buyers, upcoming 2 BHK projects in Rajarhat are often the sweet spot between price and location. Luxury 2 BHK flats in Rajarhat usually come with a full clubhouse, covered parking and better specifications than older resale homes nearby. Check the approach road too: here, two projects a kilometre apart can feel very different in daily travel.']),
     ('Upcoming 3 BHK projects in Rajarhat', [
        'Larger families often compare upcoming 3 BHK projects in Rajarhat with similar homes in New Town and find more carpet area for the money. Luxury 3 BHK flats in Rajarhat at the upper end add private decks, home automation and staff rooms. We put the all-in cost in writing, including GST, registration, parking, club charges and maintenance deposits, so the comparison is fair.']),
     ('Luxury gated community in Rajarhat', [
        'Most new launches here are planned as a luxury gated community in Rajarhat, with security at the gate, landscaped podiums and amenities inside the campus. Premium high-rise apartments Rajarhat developers are building also offer upper-floor views across the New Town skyline. Before you book, we walk the site to check build quality, the number of flats per lift and how the project handles heavy monsoon rain.'])],
    'New launch projects in Rajarhat',
    'We list only RERA registered upcoming projects Rajarhat buyers can verify for themselves: every registration number can be checked on the WBRERA website before booking.',
    'rajarhat',
    [('Rajarhat or New Town: which is better?', 'New Town is more planned and has more finished social infrastructure. Rajarhat often gives you more space for the money and is closer to the airport. The right choice depends on where you work and your budget, and we show you both side by side.'),
     FAQ_BROKERAGE, FAQ_RERA])

southern_bypass = loc_page('southern-bypass.html', 'Southern Bypass',
    'Upcoming Projects near Southern Bypass Kolkata | HouseRoot',
    'Upcoming projects near Southern Bypass Kolkata, verified by HouseRoot: luxury 2 & 3 BHK flats in South Kolkata, RERA checked, zero brokerage.',
    ['Upcoming projects near Southern Bypass Kolkata', 'Luxury flats near Southern Bypass', '2 BHK flats near Southern Bypass Kolkata', '3 BHK flats near Southern Bypass Kolkata', 'Upcoming luxury residential projects South Kolkata'],
    'Upcoming projects near Southern Bypass Kolkata', 'Southern Bypass · South Kolkata',
    'South Kolkata has some of the city\'s most established neighbourhoods, and the Southern Bypass corridor is where much of its new housing is now planned. These are the upcoming projects near Southern Bypass Kolkata our advisors are tracking, with honest notes on price, possession and daily travel.',
    'Architect\'s scale model of a modern home on floor plans, representing new residential towers in South Kolkata',
    [('Luxury flats near Southern Bypass', [
        'Buyers look at this corridor for one reason above all: it keeps them close to South Kolkata, with its schools, hospitals, markets and family networks, while offering new construction that older neighbourhoods rarely can. Large plots are scarce in the established parts of the south, so new towers with clubhouses and open green space tend to come up along the bypass and the roads that feed it.',
        'Luxury flats near Southern Bypass typically offer what buyers miss in older South Kolkata buildings: covered parking, full power back-up, modern lifts, round-the-clock security and a proper clubhouse. Road access and metro connectivity matter a great deal here, so we map your daily commute before you shortlist anything.']),
     ('2 BHK flats near Southern Bypass Kolkata', [
        'Two-bedroom homes are popular with young professionals and with parents buying near their children. 2 BHK flats near Southern Bypass Kolkata vary widely in carpet area and finish from project to project, so we compare them on carpet area, price per square foot of carpet and the real monthly maintenance rather than on brochure numbers.']),
     ('3 BHK flats near Southern Bypass Kolkata', [
        'For growing families, 3 BHK flats near Southern Bypass Kolkata offer room for a study or a parent\'s bedroom without moving far from the neighbourhoods they already know. In premium towers, look for cross-ventilation, a separate utility balcony and a sensible number of flats per lift; these matter more over the years than a grand lobby.']),
     ('What to check before you book', [
        'Some low-lying pockets of South Kolkata see water-logging in heavy monsoon rain, so we check drainage and the approach road on a site visit, ideally after a rainy day. We also confirm the WBRERA registration, the land title and the developer\'s delivery record on past projects.'])],
    'Upcoming luxury residential projects in South Kolkata',
    'The upcoming luxury residential projects South Kolkata buyers ask us about appear here only after our team has visited the site and checked its RERA registration. If nothing fits yet, tell us your brief and we will share the current shortlist.',
    'southern bypass',
    [('Is the Southern Bypass area good for families?', 'It suits families who want to stay close to South Kolkata\'s schools, hospitals and markets but would rather live in a newer building with modern amenities and security.'),
     FAQ_BROKERAGE, FAQ_RERA])

# =============================== SITEMAP & ROBOTS ===============================
def sitemap(files):
    today = datetime.date.today().isoformat()
    def entry(f):
        loc = f'{SITE}/' if f == 'index.html' else f'{SITE}/{f}'
        pr = '1.0' if f == 'index.html' else '0.9' if f in dict(LOCATIONS) or f == 'projects.html' else '0.6'
        return f'  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>'
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(entry(f) for f in files) + '\n</urlset>\n'

ROBOTS = f'''User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {SITE}/sitemap.xml
'''

pages = {'index.html': index, 'blog.html': blog, 'post.html': post, 'projects.html': projects, 'project.html': project, 'about.html': about, 'developers.html': developers, 'contact.html': contact,
         'new-town.html': new_town, 'rajarhat.html': rajarhat, 'southern-bypass.html': southern_bypass}
for name, html in pages.items():
    (ROOT / name).write_text(html, encoding='utf-8')
    print('wrote', name, len(html))

# project.html and post.html are left out: their content depends on ?id= / ?slug=
in_sitemap = ['index.html'] + [f for f, _ in LOCATIONS] + ['projects.html', 'about.html', 'developers.html', 'blog.html', 'contact.html']
(ROOT / 'sitemap.xml').write_text(sitemap(in_sitemap), encoding='utf-8')
(ROOT / 'robots.txt').write_text(ROBOTS, encoding='utf-8')
print('wrote sitemap.xml, robots.txt')
