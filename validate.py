"""Static integrity checks for links, controls, generated data, and status wording."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, re, zipfile

root=Path(__file__).resolve().parent
dist=root/'dist'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.refs=[];self.labels=[];self.attrs=[];self.feed(text)
    def handle_starttag(self,tag,attributes):
        a=dict(attributes);self.attrs.append((tag,a))
        if 'id' in a:self.ids.append(a['id'])
        for key in ['href','src']:
            if key in a:self.refs.append(a[key])
        if tag=='label' and 'for' in a:self.labels.append(a['for'])

for name in ['index.html','cv.html','card/index.html']:
    page_path=dist/name
    text=page_path.read_text(encoding='utf-8');p=Page(text)
    assert len(p.ids)==len(set(p.ids)),f'Duplicate ids: {name}'
    base_dir=page_path.parent
    for tag,attrs in p.attrs:
        if tag=='base':base_dir=(page_path.parent/attrs['href']).resolve()
    for ref in p.refs:
        u=urlparse(ref)
        if u.scheme or ref.startswith('//'):continue
        if ref=='../' and name=='card/index.html':continue
        target=(base_dir/unquote(u.path)).resolve() if u.path else page_path
        if target.is_dir():target=target/'index.html'
        assert target.exists(),f'Missing asset: {ref}'
        if u.fragment:
            target_ids=p.ids if target==page_path else Page(target.read_text(encoding='utf-8')).ids
            assert u.fragment in target_ids,f'Missing anchor: {ref}'
    for label in p.labels: assert label in p.ids,f'Unassociated label: {label}'
    for tag,a in p.attrs:
        if 'data-open' in a:assert a['data-open'] in p.ids
        if tag=='img':assert a.get('alt') and a.get('width') and a.get('height')
        if a.get('target')=='_blank':assert 'noopener' in a.get('rel','')
    assert '<!-- CV_ENTRIES -->' not in text
    assert '<!-- BUSINESS_CARD -->' not in text
    assert not re.search(r'\{\{[A-Z_]+\}\}',text),f'Unresolved placeholder: {name}'
    if name!='card/index.html':
        assert 'Accepted proposal' in text
        assert 'Admitted · not yet enrolled' in text
    assert '4904' not in text

index=(dist/'index.html').read_text(encoding='utf-8');ids=set(Page(index).ids)
app=(dist/'app.js').read_text(encoding='utf-8')
for selector in re.findall(r"\$\('#([^']+)'\)",app):assert selector in ids,f'Missing JS target: {selector}'
data=json.loads((root/'content.json').read_text(encoding='utf-8'))
assert index.count('class="cv-entry"')==len(data['entries'])
assert index.count('class="course-item"')==len(data['courses'])
with zipfile.ZipFile(dist/'assets/portfolio-source.zip') as z:
    assert not any('.openai/' in n or '.git/' in n for n in z.namelist())
    assert z.read('dist/index.html')==(dist/'index.html').read_bytes()
    assert z.read('dist/app.js')==(dist/'app.js').read_bytes()
    assert z.read('dist/card/index.html')==(dist/'card/index.html').read_bytes()
    assert 'dist/assets/chris-cox-portrait.webp' in z.namelist()
    assert 'dist/vendor/qrcode-LICENSE.txt' in z.namelist()
    assert z.read('.github/workflows/deploy-pages.yml')==(root/'.github/workflows/deploy-pages.yml').read_bytes()
assert index.index('id="playground"')<index.index('id="design-preview"')
assert index.count('id="business-card-dialog"')==1
assert index.count('data-contact-card')==1
assert index.index('class="hero-portrait"')<index.index('class="evidence-strip"')
print(f'PASS: 3 HTML views, {len(data["entries"])} CV entries, {len(data["courses"])} courses, local links and JS targets, photo placement, business card, source bundle and status labels.')
