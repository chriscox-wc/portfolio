(() => {
  'use strict';
  const card=document.querySelector('[data-contact-card]');
  if(!card) return;
  const find=selector=>card.querySelector(selector);
  const link=window.ContactCard.urls(document.baseURI);
  const contact=window.PORTFOLIO_DATA.contact;
  const dialog=document.getElementById('business-card-dialog');
  const status=find('[data-card-status]');
  const announce=message=>{status.textContent=message;};
  let contactBlobUrl=null,qrBlobUrl=null;

  document.querySelectorAll('[data-business-card]').forEach(anchor=>{
    anchor.href=link.card;
    if(!dialog||typeof dialog.showModal!=='function') return;
    anchor.addEventListener('click',event=>{
      if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey||event.button>0) return;
      event.preventDefault();
      const menu=document.querySelector('.mobile-menu');if(menu) menu.open=false;
      announce('');dialog.showModal();
    });
  });
  find('[data-portfolio-url]').href=link.portfolio;
  find('[data-card-permalink]').href=link.card;
  find('[data-card-url]').value=link.card;

  // The generated static .vcf is a no-JavaScript fallback. This version follows
  // the current domain and repository path when the portfolio is moved.
  try{
    contactBlobUrl=URL.createObjectURL(new Blob([window.ContactCard.vcard(contact,document.baseURI)],{type:'text/vcard;charset=utf-8'}));
    find('[data-save-contact]').href=contactBlobUrl;
  }catch{}
  find('[data-save-contact]').addEventListener('click',()=>announce('Open the downloaded contact file to add Chris to your contacts.'));

  function manualCopy(){
    find('[data-copy-fallback]').hidden=false;
    const input=find('[data-card-url]');
    input.focus();input.select();input.setSelectionRange(0,input.value.length);
    announce('Select and copy the card link below.');
  }
  find('[data-copy-card]').addEventListener('click',async()=>{
    try{
      if(!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(link.card);
      announce('Card link copied. Paste it into a text, email, or message.');
    }catch{manualCopy();}
  });
  const share=find('[data-share-card]');
  if(typeof navigator.share!=='function') share.title='Sharing depends on your browser; you can copy the card link.';
  share.addEventListener('click',async()=>{
    if(typeof navigator.share!=='function'){manualCopy();return;}
    try{
      await navigator.share({title:'Chris Cox — Digital Business Card',text:'Chris Cox · Web Developer & Educator · Westminster College',url:link.card});
      announce('Share dialog closed.');
    }catch(error){
      if(error.name==='AbortError'){announce('');return;}
      manualCopy();
    }
  });

  let qrReady=false;
  function buildQR(){
    if(qrReady) return true;
    try{
      const qr=window.qrcode(0,'M');qr.addData(link.card);qr.make();
      const svg=qr.createSvgTag({cellSize:6,margin:24,scalable:true});
      // Only numeric QR drawing data is emitted by the bundled encoder.
      find('[data-qr-code]').innerHTML=svg;
      find('[data-qr-code] svg').setAttribute('aria-hidden','true');
      qrBlobUrl=URL.createObjectURL(new Blob([svg],{type:'image/svg+xml'}));
      find('[data-download-qr]').href=qrBlobUrl;
      qrReady=true;return true;
    }catch{announce('The QR code could not load. Use Copy link to share this card.');return false;}
  }
  find('[data-toggle-qr]').addEventListener('click',()=>{
    const panel=document.getElementById('business-card-qr');
    const reveal=panel.hidden;
    if(reveal&&!buildQR()) return;
    panel.hidden=!reveal;
    find('[data-toggle-qr]').setAttribute('aria-expanded',String(reveal));
    find('[data-toggle-qr]').textContent=reveal?'Hide QR code −':'Show QR code ⊞';
    if(reveal) requestAnimationFrame(()=>panel.scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}));
  });
  // Cleanup on real navigation, but keep URLs valid when restored from bfcache.
  window.addEventListener('pagehide',event=>{
    if(event.persisted) return;
    if(contactBlobUrl) URL.revokeObjectURL(contactBlobUrl);
    if(qrBlobUrl) URL.revokeObjectURL(qrBlobUrl);
  });
})();
