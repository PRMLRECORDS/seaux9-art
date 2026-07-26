/* SEAUX9.ART — content renderer
   Content lives in content/site.json (canonical). content/site.data.js embeds it
   for file:// viewing. When served over http(s) we re-fetch the JSON so edits
   show up without rebuilding. */

(function () {
  'use strict';

  const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const set = (id, fn) => { const el = document.getElementById(id); if (el) fn(el); };

  function render(data) {
    // ── releases: BUY buttons first, stream second ──
    const buyUrl = (sku) => {
      const all = [...(data.store?.music || []), ...(data.store?.merch || [])];
      return all.find((p) => p.id === sku)?.url || '#store';
    };
    set('releases', (el) => {
      el.innerHTML = data.releases.map((r) => {
        const buys = Object.entries(r.buy || {}).map(([fmt, sku]) =>
          `<a class="rel-buy" href="${esc(buyUrl(sku))}" target="_blank" rel="noopener">Buy ${esc(fmt.toUpperCase())}</a>`).join('');
        const streams = Object.entries(r.links || {}).map(([name, url]) =>
          `<a class="rel-stream" href="${esc(url)}" target="_blank" rel="noopener">${esc(name[0].toUpperCase() + name.slice(1))} ↗</a>`).join('');
        return `
        <article class="release c-${esc(r.color)} reveal">
          <span class="rel-type">${esc(r.type)}</span>
          ${r.img ? `<img class="rel-cover" src="${esc(r.img)}" alt="${esc(r.title)} cover art" loading="lazy">` : ''}
          <h3 class="rel-title">${esc(r.title)}</h3>
          <span class="rel-year">${esc(r.year)}</span>
          <p class="rel-story">${esc(r.story)}</p>
          ${r.note ? `<p class="rel-note">✦ ${esc(r.note)}</p>` : ''}
          <div class="rel-links">${buys}${streams}</div>
        </article>`;
      }).join('');
    });

    // ── upcoming projects ──
    set('upcoming', (el) => {
      el.innerHTML = (data.upcoming || []).map((u) => `
        <div class="up-card reveal">
          <span class="up-status">${esc(u.status)}</span>
          <h4 class="up-title">${esc(u.title)}</h4>
          <p class="up-note">${esc(u.note)}</p>
        </div>`).join('');
    });

    // ── store ──
    const productCard = (p) => `
      <article class="product reveal">
        ${p.img ? `<img class="product-img" src="${esc(p.img)}" alt="${esc(p.name)}" loading="lazy">` : ''}
        <h4 class="product-name">${esc(p.name)}</h4>
        <span class="product-format">${esc(p.format)}</span>
        ${p.note ? `<p class="product-note">${esc(p.note)}</p>` : '<p class="product-note"></p>'}
        <div class="product-row">
          <span class="product-price">${esc(p.price)}</span>
          ${p.url
            ? `<a class="product-buy" href="${esc(p.url)}" target="_blank" rel="noopener">BUY →</a>`
            : `<span class="product-buy soon">SOON</span>`}
        </div>
      </article>`;
    set('store-pitch', (el) => { el.textContent = data.store.pitch; });
    set('store-music', (el) => { el.innerHTML = data.store.music.map(productCard).join(''); });
    set('store-merch', (el) => { el.innerHTML = data.store.merch.map(productCard).join(''); });

    // ── tiers ──
    set('tiers-grid', (el) => {
      el.innerHTML = data.tiers.map((t) => `
        <article class="tier c-${esc(t.color)}${t.featured ? ' featured' : ''} reveal">
          <h3 class="tier-name">${esc(t.name)}</h3>
          <div class="tier-price">${esc(t.price)}</div>
          <div class="tier-cadence">${esc(t.cadence)}</div>
          <ul class="tier-perks">${t.perks.map((p) => `<li>${esc(p)}</li>`).join('')}</ul>
          <a class="btn ${t.featured ? 'btn-solid' : 'btn-line'}" href="${esc(t.url)}" target="_blank" rel="noopener">${esc(t.cta)}</a>
        </article>`).join('');
    });

    // ── events (soonest first) + NEXT UP hero banner ──
    const events = [...data.events].sort((a, b) => a.date.localeCompare(b.date));
    const today = new Date().toISOString().slice(0, 10);
    const next = events.find((e) => e.date >= today) || events[0];
    if (next) set('next-show', (el) => {
      el.innerHTML = `NEXT UP → <a href="#events">${esc(next.title)} · ${esc(next.displayDate)} · ${esc(next.city)}</a>`;
    });
    set('events-list', (el) => {
      el.innerHTML = events.map((e) => {
        const [big, small] = splitDate(e.displayDate);
        return `
        <article class="event reveal">
          <div class="ev-date">${esc(big)}<small>${esc(small)}</small></div>
          <div class="ev-main">
            <h3>${esc(e.title)}${e.livestream ? ' <span class="ev-live">LIVESTREAM</span>' : ''}</h3>
            <p class="ev-venue">${esc(e.venue)} · ${esc(e.city)} · ${esc(e.time)}</p>
            <p class="ev-info">${esc(e.info)}</p>
          </div>
          ${e.link
            ? `<a class="ev-cta" href="${esc(e.link)}" ${e.link.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}>${esc(e.cta)} →</a>`
            : `<span class="ev-cta ev-soon">${esc(e.cta)}</span>`}
        </article>`;
      }).join('');
    });

    // ── bio + milestones ──
    set('bio', (el) => { el.textContent = data.artist.bio; });
    set('bio-extra', (el) => { el.textContent = data.artist.bioExtra || ''; });
    set('milestones', (el) => {
      el.innerHTML = (data.milestones || []).map((m) => `
        <div class="milestone reveal">
          <span class="milestone-year">${esc(m.year)}</span>
          <span class="milestone-what">${esc(m.what)}</span>
        </div>`).join('');
    });

    // ── press ──
    set('press-grid', (el) => {
      el.innerHTML = (data.press || []).map((p) => `
        <a class="press-card reveal" href="${esc(p.url)}" target="_blank" rel="noopener">
          <span class="press-outlet">${esc(p.outlet)}</span>
          <h3 class="press-title">${esc(p.title)}</h3>
          <p class="press-quote">${esc(p.quote)}</p>
        </a>`).join('');
    });

    // ── gallery ──
    set('gallery-track', (el) => {
      el.innerHTML = (data.gallery || []).map((g) => `
        <figure class="gallery-item">
          <img src="${esc(g.src)}" alt="${esc(g.alt)}" loading="lazy">
          <figcaption class="gallery-caption">${esc(g.caption)}</figcaption>
        </figure>`).join('');
    });

    // ── giving ──
    set('giving-card', (el) => {
      el.innerHTML = `
      <h3 class="giv-title">${esc(data.giving.title)}</h3>
      <p class="giv-body">${esc(data.giving.body)}</p>
      <a class="giv-cta" href="${esc(data.giving.link)}" target="_blank" rel="noopener">Support the build ✦</a>
      <p class="giv-partner">${esc(data.giving.partner)}</p>`;
    });

    // ── arsenal (gear affiliates + sponsor CTA) ──
    if (data.arsenal) {
      set('arsenal-pitch', (el) => { el.textContent = data.arsenal.pitch; });
      set('gear-grid', (el) => {
        el.innerHTML = data.arsenal.gear.map((g) => {
          const inner = `<b class="gear-name">${esc(g.name)}</b><span class="gear-role">${esc(g.role)}</span>`;
          return g.url
            ? `<a class="gear reveal has-link" href="${esc(g.url)}" target="_blank" rel="noopener sponsored">${inner}<span class="gear-shop">SHOP →</span></a>`
            : `<span class="gear reveal">${inner}</span>`;
        }).join('');
      });
      set('sponsor-cta', (el) => {
        el.innerHTML = `<p>${esc(data.arsenal.sponsorCta.line)}</p>
          <a class="btn btn-sun" href="${esc(data.arsenal.sponsorCta.url)}">${esc(data.arsenal.sponsorCta.cta)} ✦</a>`;
      });
    }

    // ── worlds ──
    set('worlds-grid', (el) => {
      el.innerHTML = data.worlds.map((x) => `
        <a class="world reveal" href="${esc(x.link)}" ${x.link.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}>
          <h3>${esc(x.name)}</h3><p>${esc(x.desc)}</p>
        </a>`).join('');
    });

    // ── journal posts (newest first) ──
    set('posts', (el) => {
      el.innerHTML = [...data.posts]
        .sort((a, b) => b.date.localeCompare(a.date))
        .map((p) => `
        <article class="post reveal">
          <span class="post-date">${esc(fmtDate(p.date))}</span>
          <h3>${esc(p.title)}</h3>
          <p>${esc(p.body)}</p>
          <div class="post-tags">${(p.tags || []).map((t) => `<span>#${esc(t)}</span>`).join('')}</div>
        </article>`).join('');
    });

    // ── socials + mailing + donate ──
    set('socials', (el) => {
      el.innerHTML = data.socials.map((s) => `
        <a class="social reveal" href="${esc(s.url)}" target="_blank" rel="noopener">
          ${esc(s.name)}<small>${esc(s.handle)}</small>
        </a>`).join('');
    });
    if (data.mailing) {
      set('mailing-cta', (el) => { el.href = data.mailing.url; });
      set('mailing-pitch', (el) => { el.textContent = data.mailing.pitch; });
    }
    if (data.donate) {
      set('donate-cta', (el) => { el.href = data.donate.url; });
      set('nav-donate', (el) => { el.href = data.donate.url; });
    }

    // ── ticker ──
    set('ticker-track', (el) => {
      const items = ['9SQUAD', 'OWN THE MUSIC', 'AFRO FREEDOM HOUSEHOP', 'AYITI ✦ ATLANTA',
        'PRML RECORDS', 'TANBOU DIGITAL', '9SOCIETY', 'STAY BLESSED'];
      const run = items.map((t) => `<span>${esc(t)}</span><span>✦</span>`).join('');
      el.innerHTML = run + run; // doubled for seamless loop
    });

    set('yr', (el) => { el.textContent = String(new Date().getFullYear()); });
    observeReveals();
  }

  function splitDate(display) {
    const parts = display.split('·').map((s) => s.trim());
    return [parts[0] || display, parts[1] || ''];
  }

  function fmtDate(iso) {
    const d = new Date(iso + 'T12:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).toUpperCase();
  }

  function observeReveals() {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((el) => el.classList.add('in')); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en, i) => {
        if (en.isIntersecting) {
          en.target.style.transitionDelay = `${(i % 6) * 70}ms`;
          en.target.classList.add('in');
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach((el) => io.observe(el));
  }

  // Prefer fresh JSON over the embedded copy when we're on a real server.
  const embedded = window.SEAUX9_DATA;
  if (location.protocol.startsWith('http')) {
    fetch('content/site.json', { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(render)
      .catch(() => embedded && render(embedded));
  } else if (embedded) {
    render(embedded);
  }
})();
