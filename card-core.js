(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  else root.ContactCard=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function urls(base){
    const portfolio=new URL('./',base).href;
    return {portfolio,card:new URL('card/',portfolio).href};
  }
  function escapeText(value){return String(value).replace(/\\/g,'\\\\').replace(/\r\n|\r|\n/g,'\\n').replace(/;/g,'\\;').replace(/,/g,'\\,');}
  function foldLine(line){
    const encoder=new TextEncoder();let lines=[],part='',bytes=0;
    for(const char of line){
      const size=encoder.encode(char).length;
      if(bytes+size>75){lines.push(part);part=' ';bytes=1;}
      part+=char;bytes+=size;
    }
    lines.push(part);return lines.join('\r\n');
  }
  function vcard(contact,base){
    const link=urls(base), e=escapeText;
    const lines=[
      'BEGIN:VCARD','VERSION:3.0',
      `N:${e(contact.familyName)};${e(contact.givenName)};;;`,
      `FN:${e(contact.name)}`,
      `ORG:${e(contact.organization)};${e(contact.department)}`,
      `TITLE:${e(contact.role)}`,
      `EMAIL;TYPE=INTERNET,WORK:${e(contact.email)}`,
      `TEL;TYPE=WORK,VOICE:${e(contact.phone)}`,
      `ADR;TYPE=WORK:;;${e(contact.street)};${e(contact.city)};${e(contact.region)};${e(contact.postalCode)};${e(contact.country)}`,
      `URL:${link.portfolio}`,
      `NOTE:${e('Web developer and educator.\nDigital business card: '+link.card)}`,
      'END:VCARD'
    ];
    return lines.map(foldLine).join('\r\n')+'\r\n';
  }
  return {urls,escapeText,foldLine,vcard};
});
