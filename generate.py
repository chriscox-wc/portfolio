"""Build static CV views and a downloadable source bundle from one content dataset."""
from pathlib import Path
import html, json, zipfile, subprocess, os
from urllib.parse import urljoin, urlsplit

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

def entry_markup(entry, index, print_view=False):
    hidden = '' if print_view or entry['category'] == 'Experience' else ' hidden'
    tags = ''.join(f'<span>{esc(tag)}</span>' for tag in entry['tags'])
    status = f'<span class="entry-status">{esc(entry["status"])}</span>' if entry.get('status') else ''
    return f'''<article class="cv-entry" data-index="{index}"{hidden}>
      <div class="entry-meta"><p>{esc(entry['date'])}</p><span>{esc(entry['category'])}</span></div>
      <div><h3>{esc(entry['title'])}</h3><p class="entry-org">{esc(entry['org'])}</p><p class="entry-text">{esc(entry['text'])}</p>{status}<div class="tags">{tags}</div></div>
    </article>'''

entries = '\n'.join(entry_markup(entry, i) for i, entry in enumerate(DATA['entries']))
courses = '\n'.join(f'<details class="course-item" data-area="{esc(c["area"])}"><summary>{esc(c["title"])}</summary><p>{esc(c["focus"])}<span>{esc(c["area"])}</span></p></details>' for c in DATA['courses'])
template = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
card_url = urljoin(DATA['contact']['siteUrl'], 'card/')
portrait_url = urljoin(DATA['contact']['siteUrl'], 'assets/chris-cox-portrait.webp')
card = (ROOT / 'templates/business-card.html').read_text(encoding='utf-8').replace('{{CARD_URL}}',esc(card_url))
template = template.replace('<!-- BUSINESS_CARD -->',card).replace('{{SITE_URL}}',esc(site_url)).replace('{{PORTRAIT_URL}}',esc(portrait_url))
assert template.count('<!-- CV_ENTRIES -->') == 1
assert template.count('<!-- COURSES -->') == 1
(DIST / 'index.html').write_text(template.replace('<!-- CV_ENTRIES -->',entries).replace('<!-- COURSES -->',courses),encoding='utf-8')
(DIST / 'data.js').write_text('window.PORTFOLIO_DATA = '+json.dumps(DATA,ensure_ascii=False, separators=(',',':'))+';\n',encoding='utf-8')
card_page = (ROOT / 'templates/card-page.html').read_text(encoding='utf-8').replace('<!-- BUSINESS_CARD -->',card).replace('{{CARD_URL}}',esc(card_url)).replace('{{PORTRAIT_URL}}',esc(portrait_url))
(DIST / 'card').mkdir(exist_ok=True)
(DIST / 'card/index.html').write_text(card_page,encoding='utf-8')
subprocess.run(['node',str(ROOT/'build-card.cjs')],cwd=ROOT,check=True,env={**os.environ,'SITE_URL':site_url})

sections=[]
for category in ['Experience','Education','Scholarship','Teaching','Leadership','Awards']:
    heading = {'Leadership':'Academic and institutional service','Experience':'Professional experience','Scholarship':'Scholarly and professional activity','Teaching':'Teaching and advising','Awards':'Awards and honors'}.get(category,category)
    items='\n'.join(entry_markup(e,i,True) for i,e in enumerate(DATA['entries']) if e['category']==category)
    sections.append(f'<section><h2>{esc(heading)}</h2>{items}</section>')

cv = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Christopher Cox — Curriculum Vitae. Computing and Digital Technology, Westminster College."><title>Christopher Cox — Curriculum Vitae</title><link rel="icon" href="assets/favicon.svg"><style>
*{box-sizing:border-box}body{font-family:Arial,Helvetica,sans-serif;color:#222;background:#f3f2ed;line-height:1.55;margin:0;font-size:13px}a{color:#44319c;text-underline-offset:3px}a:focus-visible,button:focus-visible{outline:3px solid #5b44d5;outline-offset:4px}.paper{max-width:930px;margin:35px auto;padding:60px 65px;background:white;box-shadow:0 5px 30px #0001}.print-toolbar{max-width:930px;margin:30px auto 0;display:flex;justify-content:space-between;gap:20px;padding:0 15px;font-size:13px}.print-toolbar button{font:inherit;background:#5b44d5;border:0;border-radius:5px;padding:10px 18px;color:white;cursor:pointer}h1{font-size:37px;line-height:1.1;letter-spacing:-1.5px;margin:0 0 12px}header>p{margin:3px 0}.contact{font-size:11px;color:#555}.update{font-size:10px;color:#666;margin-top:13px!important}h2{font-size:20px;letter-spacing:-.5px;border-bottom:2px solid #333;padding-bottom:7px;margin:35px 0 5px}h3{font-size:14px;line-height:1.4;margin:0}.intro h2{margin-top:30px}.intro p{font-size:12px}.cv-entry{display:grid;grid-template-columns:125px 1fr;gap:20px;padding:15px 0;border-bottom:1px solid #ddd;break-inside:avoid}.entry-meta p{font-size:10px;margin:0;color:#555}.entry-meta span,.tags{display:none}.entry-org{font-size:11px;color:#55458d;margin:4px 0 7px}.entry-text{font-size:11px;margin:0}.entry-status{display:inline-block;font-size:9px;margin-top:7px;padding:2px 6px;background:#efebfa;color:#44319c}.footer-note{font-size:10px;color:#666;margin-top:35px;border-top:1px solid #ccc;padding-top:15px}
@media(max-width:650px){.paper{margin:20px 12px;padding:30px 24px}.cv-entry{grid-template-columns:1fr;gap:6px}.print-toolbar{align-items:center}.print-toolbar button{padding:9px 11px;font-size:11px}h1{font-size:32px}}
@page{size:letter;margin:.6in}
@media print{body{background:#fff;font-size:11px}.print-toolbar{display:none}.paper{max-width:none;padding:0;margin:0;box-shadow:none}h1{font-size:29px}h2{break-after:avoid;font-size:16px;margin-top:24px}.cv-entry{grid-template-columns:115px 1fr;padding:10px 0;gap:16px}h3{font-size:12px}.entry-text{font-size:10px}.entry-org{font-size:10px;color:#333}.entry-status{background:none;border:1px solid #aaa;color:#222;font-size:8px}a{color:inherit;text-decoration:none}.footer-note{font-size:8px}}
</style></head><body><div class="print-toolbar"><a href="index.html#cv">← Back to the interactive portfolio</a><button id="print">Print / save as PDF</button></div><main class="paper"><header><h1>Christopher Cox</h1><p><strong>Assistant Professor and Department Chair</strong></p><p>Computing and Digital Technology · Westminster College</p><p class="contact">501 Westminster Avenue, Fulton, Missouri 65251 · 573-592-5525<br><a href="mailto:Chris.Cox@wcmo.edu">Chris.Cox@wcmo.edu</a></p><p class="update">Curriculum vitae · Updated October 13, 2026</p></header><section class="intro"><h2>Academic interests</h2><p>INTERESTS</p></section>SECTIONS<p class="footer-note">Based on the September 2026 CV, with October updates for the accepted DC Comics fandom proposal and Spring 2027 doctoral admission. Proposal statuses reflect the source CV unless a later update is stated. Course titles reflect the catalog or commonly used title during the term taught.</p></main><script>document.getElementById('print').addEventListener('click',function(){window.print()});</script></body></html>'''
(DIST / 'cv.html').write_text(cv.replace('INTERESTS',esc(DATA['interests'])).replace('SECTIONS','\n'.join(sections)),encoding='utf-8')

# Include the actual source, excluding the archive itself and hosting credentials.
bundle = DIST / 'assets/portfolio-source.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    source_files = [ROOT/name for name in ['content.json','generate.py','build-card.cjs','validate.py','README.md','START_HERE.md','.gitignore','DEPLOY_WORKFLOW.txt']]
    for path in source_files + sorted((ROOT/'.github').rglob('*')) + sorted((ROOT/'tests').glob('*')) + sorted((ROOT/'templates').glob('*')) + sorted(DIST.rglob('*')):
        if path.is_file() and path != bundle: z.write(path,path.relative_to(ROOT))
print(json.dumps({'cv_entries':len(DATA['entries']),'courses':len(DATA['courses']),'generated':['dist/index.html','dist/data.js','dist/cv.html','dist/card/index.html','dist/assets/chris-cox.vcf','dist/assets/chris-cox-card-qr.svg','dist/assets/portfolio-source.zip']}))
