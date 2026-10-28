"""Build static CV views and a downloadable source bundle from one content dataset."""
# Keep this source ASCII-only: Unicode symbols use escapes for safe copying.
from pathlib import Path
import html, json, zipfile, subprocess, os
from urllib.parse import urljoin, urlsplit, urlencode, quote

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
DATA = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
# GitHub supplies its actual Pages address, including a repository subpath or
# custom domain. Local builds use the preview address in content.json.
configured_url = os.environ.get('SITE_URL', '').strip()
if os.environ.get('GITHUB_ACTIONS') == 'true' and not configured_url:
    raise SystemExit('SITE_URL is required in GitHub Actions. Run the included Pages workflow.')
site_url = configured_url or DATA['contact']['siteUrl']
parsed_url = urlsplit(site_url)
if (parsed_url.scheme not in ('http', 'https') or not parsed_url.hostname
        or parsed_url.query or parsed_url.fragment or parsed_url.username
        or parsed_url.password or any(c.isspace() for c in site_url)):
    raise SystemExit('SITE_URL must be an absolute HTTP(S) site root without credentials, a query, or a fragment.')
site_url = site_url.rstrip('/') + '/'
DATA['contact']['siteUrl'] = site_url
esc = lambda value: html.escape(str(value), quote=True)

# These additions live in the build script so the existing GitHub deployment
# can pick them up from one replacement file in the repository root.
FREELANCE_EMAIL = 'chriswecox@outlook.com'
DATA['contact']['freelanceEmail'] = FREELANCE_EMAIL
inquiry_url = 'mailto:' + FREELANCE_EMAIL + '?' + urlencode({
    'subject': 'Freelance website project inquiry',
    'body': 'Hi Chris,\r\n\r\nBusiness or organization:\r\nCurrent website (if any):\r\nWhat I would like to build or improve:\r\nDesired timing:\r\nApproximate budget:\r\n\r\nThanks!',
}, quote_via=quote)

FREELANCE_CSS = '''
/* Independent freelance services: scoped to the new section and contact routes. */
.freelance-availability{display:flex;align-items:flex-start;gap:10px;margin-top:20px;padding:13px 15px;background:var(--accent-soft);border-radius:6px;font-size:12px;line-height:1.7;color:var(--text)}
.freelance-availability>.status-dot{flex:none;margin:7px 0 0;background:var(--accent)}
.freelance-availability a{display:inline-block;margin-left:4px;color:var(--accent);font-weight:600;text-decoration:underline;text-underline-offset:3px}
.freelance-section{padding-block:0 85px}
.freelance-panel{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:30px 42px;padding:38px;border:1px solid var(--line);border-radius:12px;background:var(--surface)}
.freelance-intro h2{font-size:clamp(34px,4vw,48px);margin:15px 0 18px}
.freelance-intro h2 em{color:var(--accent)}
.freelance-summary{font-size:14px;line-height:1.8;max-width:40ch}
.freelance-intro .button{margin-top:24px;gap:14px;text-align:center}
.freelance-independence{font-size:12px;line-height:1.7;margin-top:16px;max-width:42ch}
.freelance-prices{width:100%;border-collapse:collapse;table-layout:fixed}
.freelance-prices caption{text-align:left;font-weight:600;font-size:14px;color:var(--text);padding-bottom:14px}
.freelance-prices caption span{font-family:var(--mono);font-size:10px;color:var(--muted);font-weight:400;margin-left:7px}
.freelance-prices th,.freelance-prices td{vertical-align:top;text-align:left;border-bottom:1px solid var(--line);padding:14px 0}
.freelance-prices thead th{font-family:var(--mono);font-size:10px;font-weight:400;color:var(--muted);padding:0 0 11px}
.freelance-prices th:last-child,.freelance-prices td{width:120px;text-align:right;padding-left:16px}
.freelance-prices tbody th{font-weight:500;font-size:14px;line-height:1.5;color:var(--text)}
.freelance-prices th small{display:block;font-weight:400;font-size:12px;line-height:1.6;color:var(--muted);margin-top:4px}
.freelance-prices td{font-size:23px;line-height:1.25;letter-spacing:-.04em;color:var(--accent);font-variant-numeric:tabular-nums}
.freelance-prices .freelance-quote{font-size:12px;line-height:1.6;letter-spacing:0;color:var(--muted)}
.freelance-prices tbody tr:last-child>*{border-bottom:0;padding-bottom:0}
.freelance-terms{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:18px 30px;border-top:1px solid var(--line);padding-top:22px}
.freelance-terms p{font-size:12px;line-height:1.8}
.freelance-terms strong{color:var(--text);font-weight:600}
.freelance-contact-actions{display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin-top:27px}
.freelance-contact-actions .contact-card-cta{margin:0}
.contact-section .freelance-inquiry-button{background:#5b44d5;color:#fff;border-color:#5b44d5;gap:14px}
.contact-bottom.contact-routes{display:grid;grid-template-columns:1fr 1fr;align-items:start;gap:24px 36px}
.contact-route{min-width:0}
.contact-routes .contact-route-label{font-family:var(--mono);font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:#424454;margin-bottom:8px}
.contact-routes .email-link{font-size:clamp(17px,2vw,23px);overflow-wrap:anywhere}
.contact-routes .contact-route-note{font-size:12px;line-height:1.7;margin-top:7px;max-width:44ch}
.contact-route-links{display:flex;align-items:center;flex-wrap:wrap;gap:6px 13px}
.contact-route-links .copy-email{margin:0}
.card-contact-list .card-email-value{min-width:0;overflow-wrap:anywhere}
@media(min-width:701px) and (max-width:1050px){.header-actions .contact-link{display:none}.desktop-nav{gap:16px}}
@media(max-width:860px){.freelance-panel{padding:28px;gap:28px}.freelance-prices th:last-child,.freelance-prices td{width:110px;padding-left:12px}.freelance-intro h2{font-size:36px}}
@media(max-width:700px){.freelance-section{padding-bottom:65px}.freelance-panel{grid-template-columns:1fr;padding:24px 20px;gap:28px}.freelance-intro h2{font-size:39px}.freelance-summary{max-width:none}.freelance-terms{grid-template-columns:1fr;gap:12px}.contact-bottom.contact-routes{grid-template-columns:1fr;gap:24px}.freelance-contact-actions .button{font-size:12px;min-height:46px}.contact-routes .email-link{font-size:21px}}
@media(max-width:370px){.freelance-panel{padding:23px 16px}.freelance-prices tbody th{font-size:13px}.freelance-prices td{font-size:21px}.freelance-prices th:last-child,.freelance-prices td{width:100px}.freelance-prices .freelance-quote{font-size:11px}.contact-routes .email-link{font-size:18px}.freelance-intro .button{width:100%;gap:10px;padding-inline:12px;font-size:12px}}
'''

FREELANCE_SECTION = f'''
  <section id="work-with-me" class="freelance-section wrap" aria-labelledby="freelance-title">
    <div class="freelance-panel">
      <div class="freelance-intro">
        <p class="eyebrow">INDEPENDENT WEB SERVICES</p>
        <h2 id="freelance-title">Work with <em>me.</em></h2>
        <p class="freelance-summary">I build websites for small businesses, redesign existing sites, and develop interactive features that help visitors understand your services and take the next step.</p>
        <a class="button primary" href="{esc(inquiry_url)}" data-freelance-inquiry>Tell me about your project <span aria-hidden="true">\u2197</span></a>
        <p class="freelance-independence">Select projects, with a clear scope. My freelance work is independent of my role at Westminster College.</p>
      </div>
      <div>
        <table class="freelance-prices" aria-describedby="freelance-scope freelance-costs">
          <caption>Introductory starting prices <span>USD</span></caption>
          <thead><tr><th scope="col">Service</th><th scope="col">Starting price</th></tr></thead>
          <tbody>
            <tr><th scope="row">One-page business website<small>A focused, mobile-friendly introduction to your business.</small></th><td>$400</td></tr>
            <tr><th scope="row">Existing website redesign<small>Refresh the layout, navigation, and experience.</small></th><td>$650</td></tr>
            <tr><th scope="row">Custom interactive business site<small>Features such as calculators, selectors, or guided inquiries.</small></th><td>$900+</td></tr>
            <tr><th scope="row">Small website changes<small>Focused updates to an existing site.</small></th><td class="freelance-quote">Quoted separately</td></tr>
          </tbody>
        </table>
      </div>
      <div class="freelance-terms">
        <p id="freelance-scope"><strong>A clear quote before we begin.</strong> These introductory prices are starting points; your final quote depends on the agreed scope. Complex booking systems, e-commerce, integrations, and larger multi-page projects are quoted separately.</p>
        <p id="freelance-costs"><strong>Project costs, clearly separated.</strong> Domain registration, hosting subscriptions, and ongoing maintenance are outside the project price unless specifically agreed.</p>
      </div>
    </div>
  </section>
'''

CONTACT_SECTION = f'''<section id="contact" class="contact-section" aria-labelledby="contact-title"><div class="wrap">
    <p class="eyebrow">LET\u2019S MAKE SOMETHING USEFUL</p>
    <div class="contact-top"><h2 id="contact-title">Good things start<br>with a <em>conversation.</em></h2><a class="contact-arrow" href="{esc(inquiry_url)}" aria-label="Email Chris about a freelance website project" title="Freelance website inquiry">\u2197</a></div>
    <div class="freelance-contact-actions"><a class="button freelance-inquiry-button" href="{esc(inquiry_url)}" data-freelance-inquiry>Discuss a website project <span aria-hidden="true">\u2197</span></a><a class="button contact-card-cta" href="card/" data-business-card>My business card <span aria-hidden="true">\u2197</span></a></div>
    <div class="contact-bottom contact-routes">
      <div class="contact-route"><p class="contact-route-label">Freelance website projects</p><a class="email-link" href="mailto:{FREELANCE_EMAIL}">{FREELANCE_EMAIL}</a><p class="contact-route-note">Independent website design and development.<br>Project inquiries and quotes.</p></div>
      <div class="contact-route"><p class="contact-route-label">Westminster &amp; academic inquiries</p><div class="contact-route-links"><a class="email-link" href="mailto:Chris.Cox@wcmo.edu">Chris.Cox@wcmo.edu</a><button class="copy-email" id="copy-email" aria-label="Copy Westminster College email address">Copy \u2197</button></div><p class="contact-route-note">College work, teaching, and academic collaboration.</p></div>
    </div>
  </div></section>'''

def replace_once(text, old, new, label):
    """Apply a known template change and fail clearly if the source changes."""
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f'Could not locate the expected {label}; review the source template before rebuilding.')
    return text.replace(old, new, 1)

def fix_adams_photo(template):
    # The stored WebP pixels are sideways. Rotate the displayed image clockwise
    # and swap its layout dimensions so it still covers the same right-hand area.
    old = '<img src="assets/adams-k9.webp" width="900" height="1200"'
    new = '<img class="adams-photo-upright" src="assets/adams-k9.webp" width="900" height="675"'
    template = replace_once(template, old, new, 'Adams K9 photo')
    photo_css = '''
.adams-art{--adams-ratio:1.2;aspect-ratio:var(--adams-ratio)}
.adams-art .adams-photo-upright{left:66%;top:50%;right:auto;width:calc(100% / var(--adams-ratio));height:calc(68% * var(--adams-ratio));max-width:none;object-position:50% 50%;transform:translate(-50%,-50%) rotate(90deg)}
.adams-art:hover .adams-photo-upright{transform:translate(-50%,-50%) rotate(90deg) scale(1.035)}
@media(max-width:860px){.adams-art{--adams-ratio:.85}}
@media(max-width:700px){.adams-art{--adams-ratio:1.1}}
'''
    return replace_once(template, '</head>', '<style id="adams-photo-styles">' + photo_css + '</style>\n</head>', 'Adams K9 photo styles')

def add_freelance_homepage(template):
    template = fix_adams_photo(template)
    work_link = '<a href="#work">Selected work</a>'
    if '<a href="#work-with-me">Work with me</a>' not in template:
        if template.count(work_link) != 2:
            raise ValueError('Expected desktop and mobile Selected work navigation links.')
        template = template.replace(work_link, work_link + '<a href="#work-with-me">Work with me</a>')
    tags = '<div class="tags"><span>Web design</span><span>Interactive tools</span><span>Wix delivery</span></div>'
    availability = '<p class="freelance-availability"><span class="status-dot" aria-hidden="true"></span><span>Available for select website design and development projects. <a href="#work-with-me">Work with me <span aria-hidden="true">\u2192</span></a></span></p>'
    template = replace_once(template, tags, tags + availability, 'Adams K9 availability placement')
    template = replace_once(template, '  <section id="playground"', FREELANCE_SECTION + '  <section id="playground"', 'services section placement')
    start = template.index('<section id="contact"')
    end = template.index('</section>', start) + len('</section>')
    template = template[:start] + CONTACT_SECTION + template[end:]
    return replace_once(template, '</head>', '<style id="freelance-styles">' + FREELANCE_CSS + '</style>\n</head>', 'freelance styles')

def add_freelance_card(card):
    old = '<small>EMAIL</small>Chris.Cox@wcmo.edu'
    card = replace_once(card, old, '<small>WESTMINSTER &amp; ACADEMIC</small>Chris.Cox@wcmo.edu', 'college email label')
    anchor = '    <div class="card-contact-list">'
    row = f'\n      <a href="{esc(inquiry_url)}" data-freelance-inquiry><span class="card-contact-icon" aria-hidden="true">@</span><span class="card-email-value"><small>FREELANCE INQUIRIES</small>{FREELANCE_EMAIL}</span><span aria-hidden="true">\u2197</span></a>'
    return replace_once(card, anchor, anchor + row, 'freelance business card email')

# Keep saved contacts consistent with the two clearly labeled email routes.
core_path = DIST / 'card-core.js'
core = core_path.read_text(encoding='utf-8')
email_line = '      `EMAIL;TYPE=INTERNET,WORK:${e(contact.email)}`,'
core = replace_once(core, email_line, email_line + '\n      ...(contact.freelanceEmail ? [`EMAIL;TYPE=INTERNET:${e(contact.freelanceEmail)}`] : []),', 'vCard freelance email')
old_note = "      `NOTE:${e('Web developer and educator.\\nDigital business card: '+link.card)}`,"
new_note = "      `NOTE:${e('Web developer and educator.\\n'+(contact.freelanceEmail?'Freelance website inquiries: '+contact.freelanceEmail+'. College and academic inquiries: '+contact.email+'.\\n':'')+'Digital business card: '+link.card)}`,"
core = replace_once(core, old_note, new_note, 'vCard inquiry labels')
core_path.write_text(core, encoding='utf-8')

def add_daily_gathering(template):
    """Load additive project partials without altering the existing work cards."""
    feature = (ROOT / 'templates/daily-gathering-feature.html').read_text(encoding='utf-8')
    case_study = (ROOT / 'templates/daily-gathering-case-study.html').read_text(encoding='utf-8')
    anchor = '    <div class="work-grid">'
    template = replace_once(template, anchor, feature + '\n' + anchor, 'featured independent project placement')
    anchor = '<dialog id="adams-dialog"'
    template = replace_once(template, anchor, case_study + '\n' + anchor, 'independent project case study')
    anchor = '<button data-category="Education" aria-pressed="false">Education</button>'
    project_filter = '<button data-category="Digital projects" aria-pressed="false" aria-label="Selected Digital Projects and Technical Innovation">Digital projects</button>'
    template = replace_once(template, anchor, project_filter + anchor, 'digital projects CV filter')
    old_note = 'with October updates for the accepted DC Comics fandom proposal and Spring 2027 doctoral admission.'
    new_note = 'with October updates for the accepted DC Comics fandom proposal, Spring 2027 doctoral admission, and The Daily Gathering independent digital project.'
    template = replace_once(template, old_note, new_note, 'CV update note')
    template = replace_once(template, '</body>', '<script src="daily-gathering.js" defer></script>\n</body>', 'case study scroll reset')
    return replace_once(template, '</head>', '<link rel="stylesheet" href="daily-gathering.css">\n</head>', 'independent project styles')

def entry_markup(entry, index, print_view=False):
    hidden = '' if print_view or entry['category'] == 'Experience' else ' hidden'
    tags = ''.join(f'<span>{esc(tag)}</span>' for tag in entry['tags'])
    status = f'<span class="entry-status">{esc(entry["status"])}</span>' if entry.get('status') else ''
    project_link = ''
    if entry.get('url'):
        project_url = urlsplit(entry['url'])
        if project_url.scheme not in ('https', 'http') or not project_url.hostname:
            raise ValueError('CV project links must be absolute HTTP(S) URLs.')
        project_link = f'<p class="entry-project-link"><a href="{esc(entry["url"])}" target="_blank" rel="noopener noreferrer">{esc(entry["url"])}<span class="dg-sr-only"> (opens in a new tab)</span></a></p>' if not print_view else f'<p class="entry-project-link"><a href="{esc(entry["url"])}">{esc(entry["url"])}</a></p>'
    return f'''<article class="cv-entry" data-index="{index}"{hidden}>
      <div class="entry-meta"><p>{esc(entry['date'])}</p><span>{esc(entry['category'])}</span></div>
      <div><h3>{esc(entry['title'])}</h3><p class="entry-org">{esc(entry['org'])}</p><p class="entry-text">{esc(entry['text'])}</p>{project_link}{status}<div class="tags">{tags}</div></div>
    </article>'''

entries = '\n'.join(entry_markup(entry, i) for i, entry in enumerate(DATA['entries']))
courses = '\n'.join(f'<details class="course-item" data-area="{esc(c["area"])}"><summary>{esc(c["title"])}</summary><p>{esc(c["focus"])}<span>{esc(c["area"])}</span></p></details>' for c in DATA['courses'])
template = add_freelance_homepage((ROOT / 'templates/index.html').read_text(encoding='utf-8'))
template = add_daily_gathering(template)
card_url = urljoin(DATA['contact']['siteUrl'], 'card/')
portrait_url = urljoin(DATA['contact']['siteUrl'], 'assets/chris-cox-portrait.webp')
card = add_freelance_card((ROOT / 'templates/business-card.html').read_text(encoding='utf-8')).replace('{{CARD_URL}}',esc(card_url))
template = template.replace('<!-- BUSINESS_CARD -->',card).replace('{{SITE_URL}}',esc(site_url)).replace('{{PORTRAIT_URL}}',esc(portrait_url))
assert template.count('<!-- CV_ENTRIES -->') == 1
assert template.count('<!-- COURSES -->') == 1
(DIST / 'index.html').write_text(template.replace('<!-- CV_ENTRIES -->',entries).replace('<!-- COURSES -->',courses),encoding='utf-8')
(DIST / 'data.js').write_text('window.PORTFOLIO_DATA = '+json.dumps(DATA,ensure_ascii=False, separators=(',',':'))+';\n',encoding='utf-8')
card_page = (ROOT / 'templates/card-page.html').read_text(encoding='utf-8').replace('<!-- BUSINESS_CARD -->',card).replace('{{CARD_URL}}',esc(card_url)).replace('{{PORTRAIT_URL}}',esc(portrait_url))
card_page = card_page.replace('</head>', '<style>.card-contact-list .card-email-value{min-width:0;overflow-wrap:anywhere}</style></head>')
(DIST / 'card').mkdir(exist_ok=True)
(DIST / 'card/index.html').write_text(card_page,encoding='utf-8')
subprocess.run(['node',str(ROOT/'build-card.cjs')],cwd=ROOT,check=True,env={**os.environ,'SITE_URL':site_url})
# The generic build helper reads content.json; use the full generated profile for
# the downloadable fallback so it matches the browser-generated contact exactly.
vcard_result = subprocess.run(
    ['node', '-e', "const fs=require('node:fs');const core=require('./dist/card-core.js');const profile=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(core.vcard(profile,profile.siteUrl));"],
    input=json.dumps(DATA['contact']).encode('utf-8'), stdout=subprocess.PIPE,
    cwd=ROOT, check=True,
)
(DIST / 'assets/chris-cox.vcf').write_bytes(vcard_result.stdout)

sections=[]
for category in ['Experience','Digital projects','Education','Scholarship','Teaching','Leadership','Awards']:
    heading = {'Digital projects':'Selected Digital Projects and Technical Innovation','Leadership':'Academic and institutional service','Experience':'Professional experience','Scholarship':'Scholarly and professional activity','Teaching':'Teaching and advising','Awards':'Awards and honors'}.get(category,category)
    items='\n'.join(entry_markup(e,i,True) for i,e in enumerate(DATA['entries']) if e['category']==category)
    sections.append(f'<section><h2>{esc(heading)}</h2>{items}</section>')

cv = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Christopher Cox \u2014 Curriculum Vitae. Computing and Digital Technology, Westminster College."><title>Christopher Cox \u2014 Curriculum Vitae</title><link rel="icon" href="assets/favicon.svg"><style>
*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#222;background:#f3f2ed;line-height:1.55;margin:0;font-size:13px}a{color:#44319c;text-underline-offset:3px}a:focus-visible,button:focus-visible{outline:3px solid #5b44d5;outline-offset:4px}.paper{max-width:930px;margin:35px auto;padding:60px 65px;background:white;box-shadow:0 5px 30px #0001}.print-toolbar{max-width:930px;margin:30px auto 0;display:flex;justify-content:space-between;gap:20px;padding:0 15px;font-size:13px}.print-toolbar button{font:inherit;background:#5b44d5;border:0;border-radius:5px;padding:10px 18px;color:white;cursor:pointer}h1{font-size:37px;line-height:1.1;letter-spacing:-1.5px;margin:0 0 12px}header>p{margin:3px 0}.contact{font-size:11px;color:#555}.update{font-size:10px;color:#666;margin-top:13px!important}h2{font-size:20px;letter-spacing:-.5px;border-bottom:2px solid #333;padding-bottom:7px;margin:35px 0 5px}h3{font-size:14px;line-height:1.4;margin:0}.intro h2{margin-top:30px}.intro p{font-size:12px}.cv-entry{display:grid;grid-template-columns:125px 1fr;gap:20px;padding:15px 0;border-bottom:1px solid #ddd;break-inside:avoid}.entry-meta p{font-size:10px;margin:0;color:#555}.entry-meta span,.tags{display:none}.entry-org{font-size:11px;color:#55458d;margin:4px 0 7px}.entry-text{font-size:11px;margin:0}.entry-project-link{font-size:11px;margin:7px 0 0;overflow-wrap:anywhere}.entry-status{display:inline-block;font-size:9px;margin-top:7px;padding:2px 6px;background:#efebfa;color:#44319c}.footer-note{font-size:10px;color:#666;margin-top:35px;border-top:1px solid #ccc;padding-top:15px}
@media(max-width:650px){.paper{margin:20px 12px;padding:30px 24px}.cv-entry{grid-template-columns:1fr;gap:6px}.print-toolbar{align-items:center}.print-toolbar button{padding:9px 11px;font-size:11px}h1{font-size:32px}}
@page{size:letter;margin:.6in}
@media print{body{background:#fff;font-size:11px}.print-toolbar{display:none}.paper{max-width:none;padding:0;margin:0;box-shadow:none}h1{font-size:29px}h2{break-after:avoid;font-size:16px;margin-top:24px}.cv-entry{grid-template-columns:115px 1fr;padding:10px 0;gap:16px}h3{font-size:12px}.entry-text{font-size:10px}.entry-org{font-size:10px;color:#333}.entry-status{background:none;border:1px solid #aaa;color:#222;font-size:8px}a{color:inherit;text-decoration:none}.footer-note{font-size:8px}}
</style></head><body><div class="print-toolbar"><a href="index.html#cv">\u2190 Back to the interactive portfolio</a><button id="print">Print / save as PDF</button></div><main class="paper"><header><h1>Christopher Cox</h1><p><strong>Assistant Professor and Department Chair</strong></p><p>Computing and Digital Technology \u00b7 Westminster College</p><p class="contact">501 Westminster Avenue, Fulton, Missouri 65251 \u00b7 573-592-5525<br><a href="mailto:Chris.Cox@wcmo.edu">Chris.Cox@wcmo.edu</a></p><p class="update">Curriculum vitae \u00b7 Updated October 28, 2026</p></header><section class="intro"><h2>Academic interests</h2><p>INTERESTS</p></section>SECTIONS<p class="footer-note">Based on the September 2026 CV, with October updates for the accepted DC Comics fandom proposal, Spring 2027 doctoral admission, and The Daily Gathering independent digital project. Proposal statuses reflect the source CV unless a later update is stated. Course titles reflect the catalog or commonly used title during the term taught.</p></main><script>document.getElementById('print').addEventListener('click',function(){window.print()});</script></body></html>'''
(DIST / 'cv.html').write_text(cv.replace('INTERESTS',esc(DATA['interests'])).replace('SECTIONS','\n'.join(sections)),encoding='utf-8')

# Include the actual source, excluding the archive itself and hosting credentials.
bundle = DIST / 'assets/portfolio-source.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    source_files = [ROOT/name for name in ['content.json','generate.py','build-card.cjs','validate.py','README.md','START_HERE.md','.gitignore','DEPLOY_WORKFLOW.txt']]
    for path in source_files + sorted((ROOT/'.github').rglob('*')) + sorted((ROOT/'tests').glob('*')) + sorted((ROOT/'templates').glob('*')) + sorted(DIST.rglob('*')):
        if path.is_file() and path != bundle: z.write(path,path.relative_to(ROOT))
print(json.dumps({'cv_entries':len(DATA['entries']),'courses':len(DATA['courses']),'generated':['dist/index.html','dist/data.js','dist/cv.html','dist/card/index.html','dist/assets/chris-cox.vcf','dist/assets/chris-cox-card-qr.svg','dist/assets/portfolio-source.zip']}))
