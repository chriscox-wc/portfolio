const test=require('node:test');
const assert=require('node:assert/strict');
const core=require('../dist/card-core.js');
const {contact}=require('../content.json');
const qrcode=require('../dist/vendor/qrcode.js');

test('card links adapt to custom domains and GitHub repository subpaths',()=>{
  for(const [base,root] of [
    ['https://example.com/index.html','https://example.com/'],
    ['https://example.com/','https://example.com/'],
    ['https://example.github.io/portfolio/','https://example.github.io/portfolio/'],
    ['https://example.github.io/portfolio/index.html','https://example.github.io/portfolio/']
  ]) assert.deepEqual(core.urls(base),{portfolio:root,card:root+'card/'});
});
test('vCard contains the verified contact data with CRLF and safe folding',()=>{
  const result=core.vcard(contact,'https://example.com/');
  assert.ok(result.startsWith('BEGIN:VCARD\r\nVERSION:3.0\r\n'));
  assert.ok(result.endsWith('END:VCARD\r\n'));
  assert.match(result,/FN:Chris Cox\r\n/);
  assert.match(result,/N:Cox;Christopher;;;/);
  assert.match(result,/TEL;TYPE=WORK,VOICE:\+15735925525/);
  assert.match(result,/EMAIL;TYPE=INTERNET,WORK:Chris.Cox@wcmo.edu/);
  assert.match(result,/URL:https:\/\/example.com\//);
  for(const line of result.split('\r\n')) assert.ok(Buffer.byteLength(line,'utf8')<=75);
  const long=core.foldLine('NOTE:'+('é😀'.repeat(75)));
  assert.equal(long.replace(/\r\n /g,''),'NOTE:'+('é😀'.repeat(75)));
  for(const line of long.split('\r\n')) assert.ok(Buffer.byteLength(line,'utf8')<=75);
  assert.equal(core.escapeText('a;b,c\\d\ne'),'a\\;b\\,c\\\\d\\ne');
});
test('QR encoder builds bounded square matrices for the live and future card URLs',()=>{
  for(const base of [contact.siteUrl,'https://example.github.io/chris-cox/']){
    const qr=qrcode(0,'M');qr.addData(core.urls(base).card);qr.make();
    const n=qr.getModuleCount();assert.equal((n-17)%4,0);assert.ok(n>=21&&n<=177);
    const svg=qr.createSvgTag({cellSize:6,margin:24,scalable:true});
    assert.match(svg,/^<svg /);assert.match(svg,/viewBox=/);
  }
});
