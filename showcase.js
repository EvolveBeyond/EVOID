(function() {
  var started = false;

  function init() {
    var code = document.getElementById('showcase-code');
    var result = document.getElementById('showcase-result');
    var section = document.getElementById('showcase-section');
    if (!code || !result || !section) { setTimeout(init, 100); return; }

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting && !started) {
          started = true;
          typeCode(code, result);
          observer.disconnect();
        }
      });
    }, { threshold: 0.3 });

    observer.observe(section);
  }

  function typeCode(code, result) {
    var lines = [
      { t: '<span class="kw">from</span> <span class="cls">evoid</span> <span class="kw">import</span> <span class="typ">Intent</span>, <span class="typ">Level</span>, <span class="fn">add_intent</span>', d: 40 },
      { t: '', d: 200 },
      { t: '<span class="cm"># Define two intents</span>', d: 30 },
      { t: '<span class="typ">GET_USER</span> <span class="op">=</span> <span class="typ">Intent</span>(<span class="st">"get_user"</span>, <span class="typ">Level</span>.<span class="cls">STANDARD</span>)', d: 35 },
      { t: '<span class="typ">SEND_EMAIL</span> <span class="op">=</span> <span class="typ">Intent</span>(<span class="st">"send_email"</span>, <span class="typ">Level</span>.<span class="cls">CRITICAL</span>)', d: 35 },
      { t: '', d: 200 },
      { t: '<span class="cm"># Write handlers — that\'s it</span>', d: 30 },
      { t: '<span class="kw">async def</span> <span class="fn">handle_user</span>(<span class="typ">intent</span>: <span class="typ">Intent</span>) <span class="op">-&gt;</span> <span class="typ">dict</span>:', d: 40 },
      { t: '    <span class="kw">return</span> {<span class="st">"id"</span>: <span class="st">42</span>, <span class="st">"name"</span>: <span class="st">"Ali"</span>}', d: 30 },
      { t: '', d: 150 },
      { t: '<span class="kw">async def</span> <span class="fn">handle_email</span>(<span class="typ">intent</span>: <span class="typ">Intent</span>) <span class="op">-&gt;</span> <span class="typ">dict</span>:', d: 40 },
      { t: '    <span class="kw">return</span> {<span class="st">"status"</span>: <span class="st">"sent"</span>}', d: 30 },
      { t: '', d: 150 },
      { t: '<span class="fn">add_intent</span>(<span class="typ">GET_USER</span>, <span class="fn">handle_user</span>)', d: 35 },
      { t: '<span class="fn">add_intent</span>(<span class="typ">SEND_EMAIL</span>, <span class="fn">handle_email</span>)', d: 35 },
    ];

    var i = 0, out = '';
    function go() {
      if (i >= lines.length) {
        setTimeout(function() {
          result.innerHTML = '<span class="ok">✓</span> <span class="json">GET:/users/42 → {"id": 42, "name": "Ali"}</span>';
          setTimeout(function() {
            result.innerHTML += '  <span class="ok">✓</span> <span class="json">POST:/email → {"status": "sent"}</span>';
          }, 600);
        }, 400);
        return;
      }
      out += lines[i].t + '\n';
      code.innerHTML = out + '<span class="cursor"></span>';
      i++;
      setTimeout(go, lines[i-1].d);
    }
    go();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
