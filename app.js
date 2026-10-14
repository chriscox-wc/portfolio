(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const $$ = selector => Array.from(document.querySelectorAll(selector));
  const {matches, sortFrames, shuffle} = window.PortfolioLogic;
  const data = window.PORTFOLIO_DATA;
  let toastTimer;
  function toast(message) {
    clearTimeout(toastTimer);
    $('#toast').textContent = message;
    $('#toast').hidden = false;
    toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 4000);
  }

  // Theme is the only value persisted locally. All demonstrations run in-browser.
  const themeButton = $('#theme-toggle');
  function updateThemeLabel() {
    const dark = document.documentElement.dataset.theme === 'dark';
    themeButton.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
    themeButton.title = `Switch to ${dark ? 'light' : 'dark'} theme`;
  }
  themeButton.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('cc-theme', next); } catch {}
    updateThemeLabel();
  });
  updateThemeLabel();
  $$('.mobile-menu a').forEach(a => a.addEventListener('click', () => { $('.mobile-menu').open = false; }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') $('.mobile-menu').open = false;
  });

  // Live CSS workbench.
  const preview = $('#design-preview');
  let accent = '#5b44d5';
  let radius = 16;
  let layout = 'wide';
  function renderDesign() {
    preview.style.setProperty('--demo-accent', accent);
    preview.style.setProperty('--demo-radius', `${radius}px`);
    preview.classList.toggle('compact', layout === 'compact');
    $('#radius-value').value = `${radius}px`;
    $('#radius-value').textContent = `${radius}px`;
    $('#live-css').textContent = `--accent: ${accent}; border-radius: ${radius}px;`;
    $$('[data-accent]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.accent === accent)));
    $$('[data-layout]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.layout === layout)));
  }
  $$('[data-accent]').forEach(b => b.addEventListener('click', () => {accent = b.dataset.accent; renderDesign();}));
  $$('[data-layout]').forEach(b => b.addEventListener('click', () => {layout = b.dataset.layout; renderDesign();}));
  $('#radius').addEventListener('input', event => {radius = Number(event.target.value); renderDesign();});
  $('#mini-action').addEventListener('click', () => {
    const activated = preview.classList.toggle('activated');
    $('#mini-message').textContent = activated ? 'Clicked. A little feedback goes a long way.' : 'Small details. Better experiences.';
    $('#mini-action').textContent = activated ? 'Nicely done ✓' : 'Try this button ↗';
  });
  $('#design-reset').addEventListener('click', () => {
    accent = '#5b44d5'; radius = 16; layout = 'wide';
    $('#radius').value = '16';
    preview.classList.remove('activated');
    $('#mini-message').textContent = 'Small details. Better experiences.';
    $('#mini-action').textContent = 'Try this button ↗';
    renderDesign();
  });
  renderDesign();

  // Deterministic algorithm frames keep play and single-step behavior in sync.
  let values = [62,28,84,16,47,93,36,72,54,22,81,41];
  let frames = sortFrames(values);
  let cursor = 0;
  let playing = false;
  let timer;
  const bars = $('#bars');
  const barNodes = values.map(() => {
    const bar = document.createElement('div');
    bar.className = 'bar';
    const label = document.createElement('span');
    bar.append(label); bars.append(bar);
    return {bar, label};
  });
  function renderFrame(announce = true) {
    const frame = frames[cursor];
    frame.values.forEach((value, index) => {
      const {bar,label} = barNodes[index];
      bar.style.height = `${value}%`;
      bar.classList.toggle('sorted', index < frame.sorted);
      bar.classList.toggle('active', frame.active.includes(index));
      label.textContent = String(value);
    });
    bars.setAttribute('aria-label', `${frame.done ? 'Sorted' : 'Current'} values: ${frame.values.join(', ')}. ${frame.note}`);
    $('#comparison-count').textContent = frame.comparisons;
    $('#swap-count').textContent = frame.swaps;
    $('#step-count').textContent = `STEP ${cursor} / ${frames.length - 1}`;
    // Avoid repeated screen-reader announcements during automatic playback.
    $('#sort-note').setAttribute('aria-live', announce ? 'polite' : 'off');
    $('#sort-note').textContent = frame.note;
    $('#sort-step').disabled = Boolean(frame.done);
    $('#sort-play').textContent = playing ? 'Pause Ⅱ' : frame.done ? 'Replay ↺' : 'Play ▶';
  }
  function pause(announce = true) {
    playing = false; clearTimeout(timer); renderFrame(announce);
  }
  function scheduleNext() {
    clearTimeout(timer);
    if (!playing) return;
    const delay = 950 - Number($('#sort-speed').value) * 150;
    timer = setTimeout(() => {
      cursor = Math.min(cursor + 1, frames.length - 1);
      if (cursor === frames.length - 1) pause(true);
      else {renderFrame(false); scheduleNext();}
    }, delay);
  }
  $('#sort-play').addEventListener('click', () => {
    if (playing) {pause(); return;}
    if (cursor === frames.length - 1) cursor = 0;
    playing = true; renderFrame(false); scheduleNext();
  });
  $('#sort-step').addEventListener('click', () => {
    playing = false; clearTimeout(timer);
    cursor = Math.min(cursor + 1, frames.length - 1); renderFrame();
  });
  $('#sort-reset').addEventListener('click', () => {pause(false); cursor = 0; renderFrame();});
  $('#shuffle').addEventListener('click', () => {
    pause(false); values = shuffle(values); frames = sortFrames(values); cursor = 0; renderFrame();
  });
  $('#sort-speed').addEventListener('input', scheduleNext);
  document.addEventListener('visibilitychange', () => {if(document.hidden && playing) pause(false);});
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting && playing) pause(false);
    }).observe($('#playground'));
  }
  renderFrame();

  // Course explorer retains semantic <details> controls for keyboard access.
  $$('[data-course]').forEach(button => button.addEventListener('click', () => {
    const selected = button.dataset.course;
    let count = 0;
    $$('.course-item').forEach(item => {
      const show = selected === 'All' || item.dataset.area === selected;
      item.hidden = !show;
      if (show) count++;
    });
    $$('[data-course]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    $('#course-count').textContent = `${count} COURSES`;
  }));
  $('#course-count').setAttribute('aria-live', 'polite');

  // Search never writes visitor input as HTML.
  let category = 'Experience';
  let query = '';
  let limit = 8;
  const entries = $$('.cv-entry');
  function renderCV() {
    let count = 0;
    entries.forEach((node, index) => {
      const include = matches(data.entries[index], category, query);
      if (include) count++;
      node.hidden = !include || count > limit;
    });
    $$('[data-category]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    const showing = Math.min(count, limit);
    $('#cv-results-count').textContent = `${showing} OF ${count} ${category === 'All' ? 'MATCHING' : category.toUpperCase()} ${count === 1 ? 'ENTRY' : 'ENTRIES'}`;
    $('#cv-empty').hidden = count !== 0;
    $('#cv-more').hidden = count <= limit;
    $('#cv-more').textContent = `Show ${Math.min(8, count - limit)} more entries ↓`;
  }
  $$('[data-category]').forEach(button => button.addEventListener('click', () => {
    category = button.dataset.category; limit = 8; renderCV();
  }));
  $('#cv-search').addEventListener('input', event => {
    query = event.target.value; category = 'All'; limit = 8; renderCV();
  });
  $('#cv-more').addEventListener('click', () => {
    const previousVisible = new Set(entries.filter(n => !n.hidden));
    limit += 8; renderCV();
    const firstNew = entries.find(n => !n.hidden && !previousVisible.has(n));
    if (firstNew) {firstNew.tabIndex = -1; firstNew.focus({preventScroll:true});}
  });
  function resetCV() {
    query = ''; category = 'All'; limit = 8; $('#cv-search').value = ''; renderCV();
  }
  $('#cv-clear').addEventListener('click', resetCV);
  $('#empty-reset').addEventListener('click', resetCV);
  $$('[data-cv-query], [data-cv-category]').forEach(link => link.addEventListener('click', () => {
    category = link.dataset.cvCategory || 'All';
    query = link.dataset.cvQuery || '';
    limit = 8;
    $('#cv-search').value = query;
    renderCV();
    if (link.hasAttribute('data-close-dialog')) link.closest('dialog').close();
    requestAnimationFrame(() => $('#cv-search').focus({preventScroll:true}));
  }));
  renderCV();

  // Native dialogs provide Escape handling and focus restoration.
  $$('[data-open]').forEach(button => button.addEventListener('click', () => {
    const dialog = document.getElementById(button.dataset.open);
    dialog.showModal();
  }));
  $$('dialog').forEach(dialog => {
    dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const r = dialog.getBoundingClientRect();
      if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close();
    });
  });
  $('#copy-email').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(data.email);
      toast('Email address copied.');
    } catch {
      toast(`Email: ${data.email} — select the address to copy it.`);
    }
  });
})();
