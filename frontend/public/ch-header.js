/**
 * ch-header.js — CampaignHelp patch layer header injector
 *
 * Injected into the upstream tool's HTML at build time (Phase 2.2–2.5).
 * Inserts the CH header bar and appends the CH footer fragment.
 *
 * Constraints:
 *   - Vanilla JS only — no imports, no async/await, no optional chaining
 *   - Relative paths for ch-logo.png and ch-footer.html so they resolve
 *     under the prefix path (e.g., /pdf/ch-logo.png, /image/ch-footer.html)
 *   - Uses .then() instead of async/await for broad browser compatibility
 */

(function () {
  'use strict';

  function buildHeader() {
    var header = document.createElement('header');
    header.className = 'ch-bar';

    var inner = document.createElement('div');
    inner.className = 'ch-bar-inner';

    // Brand link — "← All tools" leads back to the hub
    var brand = document.createElement('a');
    brand.className = 'ch-brand';
    brand.href = 'https://tools.campaign.help/';

    var logo = document.createElement('img');
    logo.src = 'ch-logo.png'; // relative — resolves to /{prefix}/ch-logo.png
    logo.alt = 'CampaignHelp';

    var divider = document.createElement('span');
    divider.className = 'ch-divider';
    divider.textContent = '/';

    var subdomain = document.createElement('span');
    subdomain.className = 'ch-subdomain';
    subdomain.textContent = 'Tools';

    brand.appendChild(logo);
    brand.appendChild(divider);
    brand.appendChild(subdomain);

    // CTA button
    var cta = document.createElement('a');
    cta.className = 'ch-cta';
    cta.href = 'https://campaign.help/contact';

    var ctaText = document.createTextNode('Talk to CampaignHelp ');
    var ctaIcon = document.createElement('span');
    ctaIcon.className = 'ch-cta-icon';
    ctaIcon.textContent = '→'; // →

    cta.appendChild(ctaText);
    cta.appendChild(ctaIcon);

    inner.appendChild(brand);
    inner.appendChild(cta);
    header.appendChild(inner);

    return header;
  }

  function injectHeader() {
    var header = buildHeader();
    var body = document.body;
    if (body.firstChild) {
      body.insertBefore(header, body.firstChild);
    } else {
      body.appendChild(header);
    }
  }

  function injectFooter() {
    fetch('ch-footer.html') // relative — resolves to /{prefix}/ch-footer.html
      .then(function (response) {
        if (!response.ok) {
          throw new Error('ch-footer.html fetch failed: ' + response.status);
        }
        return response.text();
      })
      .then(function (html) {
        var wrapper = document.createElement('div');
        wrapper.innerHTML = html;
        while (wrapper.firstChild) {
          document.body.appendChild(wrapper.firstChild);
        }
      })
      .catch(function (err) {
        console.warn('[ch-header.js] Footer not loaded:', err.message);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      injectHeader();
      injectFooter();
    });
  } else {
    // DOMContentLoaded already fired (script loaded with defer or at bottom of body)
    injectHeader();
    injectFooter();
  }
}());
