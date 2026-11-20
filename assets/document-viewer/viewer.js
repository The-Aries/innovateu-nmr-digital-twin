(function () {
  'use strict';
  var script = document.currentScript;
  var stylesheet = document.createElement('link');
  stylesheet.rel = 'stylesheet';
  stylesheet.href = new URL('./viewer.css', script.src).href;
  stylesheet.onload = function () {
    try {
      initViewer();
      initializeInteractions();
    } catch (error) {
      console.error('Shared document viewer initialization failed:', error);
    }
  };
  stylesheet.onerror = function () {
    stylesheet.remove();
    if (typeof window.__rendererViewerLoadFailed === 'function') {
      window.__rendererViewerLoadFailed();
    }
  };
  document.head.appendChild(stylesheet);

  function initViewer() {
    var main = document.querySelector('main.document');
    if (!main || document.getElementById('table-of-contents')) { return; }
    var data = {};
    var dataNode = document.getElementById('renderer-document-data');
    if (dataNode) {
      try { data = JSON.parse(dataNode.textContent); } catch (_) {}
    }
    var shell = document.createElement('div');
    shell.className = 'web-shell';
    var sidebar = document.createElement('aside');
    sidebar.className = 'sidebar';
    sidebar.id = 'table-of-contents';
    var header = document.createElement('div');
    header.className = 'sidebar-header';
    var navigation = document.createElement('div');
    navigation.className = 'document-navigation';
    navigation.innerHTML =
      '<div class="document-navigation-header"><label class="document-navigation-title" for="document-switcher">Documents</label>' +
      '<div class="document-navigation-actions"><span id="document-count" class="document-count">0</span>' +
      '<button type="button" id="document-refresh" class="document-refresh" ' +
      'title="Refresh files in this folder" aria-label="Refresh files in this folder">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M20 11a8 8 0 1 0-2.5 5.8"/><path d="M20 4v7h-7"/></svg></button></div></div>' +
      '<div class="document-select-wrap"><svg class="document-icon" viewBox="0 0 24 24" ' +
      'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>' +
      '<path d="M14 2v6h6M8 13h8M8 17h6"/></svg>' +
      '<select id="document-switcher" class="document-switcher" aria-label="Switch HTML document in this folder"></select>' +
      '<svg class="document-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg></div>' +
      '<p id="document-navigation-status" class="document-navigation-status" role="status" aria-live="polite"></p>';
    var switcher = navigation.querySelector('#document-switcher');
    var counter = navigation.querySelector('#document-count');
    var filename = decodeURIComponent(window.location.pathname.split('/').pop() || '');
    var names = Array.isArray(data.files) ? data.files.slice() : [];
    if (filename && !names.includes(filename)) { names.push(filename); }
    names.sort(function (a, b) { return a.localeCompare(b); });
    names.forEach(function (name) {
      if (typeof name !== 'string' || !/\.html$/i.test(name) || name.startsWith('.')) { return; }
      var option = document.createElement('option');
      option.value = encodeURIComponent(name);
      option.textContent = name.replace(/\.html$/i, '');
      option.selected = name === filename;
      switcher.appendChild(option);
    });
    switcher.dataset.current = encodeURIComponent(filename);
    switcher.title = filename;
    counter.textContent = String(switcher.options.length);
    counter.setAttribute('aria-label', switcher.options.length + ' files');
    header.appendChild(navigation);
    if (data.generatedLabel) {
      var generation = document.createElement('div');
      generation.className = 'generation-info';
      generation.appendChild(document.createTextNode('Generated: '));
      var time = document.createElement('time');
      time.dateTime = data.generatedAt || '';
      time.textContent = data.generatedLabel;
      generation.appendChild(time);
      header.appendChild(generation);
    }
    var contentsLabel = document.createElement('div');
    contentsLabel.className = 'sidebar-title';
    contentsLabel.textContent = 'Contents';
    header.appendChild(contentsLabel);
    sidebar.appendChild(header);
    var scroll = document.createElement('div');
    scroll.className = 'sidebar-scroll';
    var toc = document.createElement('nav');
    toc.className = 'toc';
    toc.setAttribute('aria-label', 'Table of contents');
    main.querySelectorAll('h1[id], h2[id], h3[id]').forEach(function (heading) {
      var link = document.createElement('a');
      link.className = 'level-' + heading.tagName.slice(1);
      link.href = '#' + encodeURIComponent(heading.id);
      link.textContent = heading.textContent.trim();
      toc.appendChild(link);
    });
    if (!toc.children.length) { toc.textContent = 'No headings'; }
    scroll.appendChild(toc);
    sidebar.appendChild(scroll);
    var contentWrap = document.createElement('div');
    contentWrap.className = 'document-wrap';
    var toggle = document.createElement('button');
    toggle.id = 'nav-toggle';
    toggle.className = 'nav-toggle';
    toggle.type = 'button';
    toggle.setAttribute('aria-controls', 'table-of-contents');
    toggle.textContent = 'Hide contents';
    main.parentNode.insertBefore(shell, main);
    contentWrap.appendChild(main);
    shell.appendChild(sidebar);
    shell.appendChild(contentWrap);
    document.body.insertBefore(toggle, shell);
  }

  function initializeInteractions() {


  var documentSwitcher = document.getElementById('document-switcher');
  var documentRefresh = document.getElementById('document-refresh');
  var documentStatus = document.getElementById('document-navigation-status');
  var documentCount = document.getElementById('document-count');
  if (documentSwitcher) {
    documentSwitcher.addEventListener('change', function () {
      var selected = documentSwitcher.value;
      if (selected && selected !== documentSwitcher.dataset.current) {
        window.location.assign(new URL(selected, window.location.href).href);
      }
    });
  }

  // Browser file:// pages cannot enumerate folders. The renderer writes an
  // adjacent index whenever it produces HTML; load that index on demand.
  if (documentSwitcher && documentRefresh) {
    documentRefresh.hidden = false;
    documentRefresh.addEventListener('click', function () {
      documentRefresh.disabled = true;
      documentStatus.textContent = 'Refreshing HTML files...';
      window.__rendererHtmlFiles = null;
      var script = document.createElement('script');
      var indexUrl = new URL('./.renderer-html-index.js', window.location.href);
      indexUrl.searchParams.set('refresh', String(Date.now()));
      script.src = indexUrl.href;
      script.onload = function () {
        script.remove();
        documentRefresh.disabled = false;
        var names = window.__rendererHtmlFiles;
        if (!Array.isArray(names)) {
          documentStatus.textContent = 'HTML index is invalid. Re-render a file in this folder.';
          return;
        }
        var currentFilename = decodeURIComponent(window.location.pathname.split('/').pop());
        names = names.filter(function (name) {
          return typeof name === 'string' && /\.html$/i.test(name) && !name.startsWith('.');
        });
        if (!names.includes(currentFilename)) { names.push(currentFilename); }
        names.sort(function (a, b) { return a.localeCompare(b); });
        documentSwitcher.replaceChildren();
        names.forEach(function (name) {
          var option = document.createElement('option');
          option.value = encodeURIComponent(name);
          option.textContent = name.replace(/\.html$/i, '');
          option.selected = name === currentFilename;
          documentSwitcher.appendChild(option);
        });
        documentSwitcher.dataset.current = encodeURIComponent(currentFilename);
        documentSwitcher.title = currentFilename;
        if (documentCount) {
          documentCount.textContent = String(names.length);
          documentCount.setAttribute('aria-label', names.length + ' files');
        }
        documentStatus.textContent = names.length + ' HTML files available.';
      };
      script.onerror = function () {
        script.remove();
        documentRefresh.disabled = false;
        documentStatus.textContent = 'HTML index unavailable. Re-render a file in this folder.';
      };
      document.head.appendChild(script);
    });
  }

  function fallbackCopy(text) {
    var area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
    document.body.removeChild(area);
    if (!ok) { throw new Error('Copy command failed'); }
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    fallbackCopy(text);
  }

  document.querySelectorAll('.document pre > code').forEach(function (code) {
    var pre = code.parentElement;
    if (!pre || pre.closest('.code-shell')) { return; }

    var shell = document.createElement('div');
    shell.className = 'code-shell';
    pre.parentNode.insertBefore(shell, pre);

    var toolbar = document.createElement('div');
    toolbar.className = 'code-toolbar';
    var language = document.createElement('span');
    language.textContent = pre.dataset.language || 'text';
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy block');

    button.addEventListener('click', async function () {
      var original = button.textContent;
      try {
        await copyText(code.textContent);
        button.textContent = 'Copied';
      } catch (_) {
        button.textContent = 'Copy failed';
      }
      window.setTimeout(function () { button.textContent = original; }, 1400);
    });

    toolbar.appendChild(language);
    toolbar.appendChild(button);
    shell.appendChild(toolbar);
    shell.appendChild(pre);
  });

  document.querySelectorAll('.document table').forEach(function (table) {
    if (table.classList.contains('flowchart') || table.closest('.table-scroll')) { return; }
    var wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  var toggle = document.getElementById('nav-toggle');
  if (toggle) {
    var updateToggle = function () {
      var expanded = !document.body.classList.contains('nav-collapsed');
      toggle.setAttribute('aria-expanded', String(expanded));
      toggle.textContent = expanded ? 'Hide contents' : 'Show contents';
    };
    toggle.addEventListener('click', function () {
      document.body.classList.toggle('nav-collapsed');
      updateToggle();
    });
    window.addEventListener('resize', updateToggle);
    updateToggle();
  }

  var links = Array.from(document.querySelectorAll('.toc a[href^="#"]'));
  var linkById = new Map();
  links.forEach(function (link) {
    try { linkById.set(decodeURIComponent(link.hash.slice(1)), link); } catch (_) {}
  });

  var headings = Array.from(document.querySelectorAll('.document h1[id], .document h2[id], .document h3[id]'));
  if ('IntersectionObserver' in window && headings.length) {
    var visible = new Map();
    var updateActive = function () {
      var best = null;
      headings.forEach(function (heading) {
        if (!visible.get(heading)) { return; }
        if (!best || heading.getBoundingClientRect().top < best.getBoundingClientRect().top) { best = heading; }
      });
      if (!best) {
        for (var i = headings.length - 1; i >= 0; i--) {
          if (headings[i].getBoundingClientRect().top <= 120) { best = headings[i]; break; }
        }
      }
      links.forEach(function (link) { link.classList.remove('active'); });
      if (best && linkById.has(best.id)) { linkById.get(best.id).classList.add('active'); }
    };
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { visible.set(entry.target, entry.isIntersecting); });
      updateActive();
    }, { rootMargin: '-10% 0px -75% 0px', threshold: [0, 1] });
    headings.forEach(function (heading) { observer.observe(heading); });
  }
  }
})();
