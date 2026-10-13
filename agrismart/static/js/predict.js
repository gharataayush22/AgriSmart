const PRESETS = {
  konkan:   {N: 80,  P: 48, K: 40, temperature: 25, humidity: 83, ph: 6.4, rainfall: 230},
  punjab:   {N: 78,  P: 48, K: 20, temperature: 22, humidity: 65, ph: 6.2, rainfall: 85},
  vidarbha: {N: 120, P: 40, K: 20, temperature: 25, humidity: 80, ph: 7.0, rainfall: 80},
  kerala:   {N: 22,  P: 17, K: 30, temperature: 27, humidity: 95, ph: 6.0, rainfall: 175},
};
const form = document.getElementById('sliders');
const result = document.getElementById('result');
let colors = {}, timer = null;

// Build one slider + number box per feature
META.forEach(m => {
  const row = document.createElement('div');
  row.className = 'field';
  row.innerHTML = `
    <label for="r-${m.key}">${m.label}<small>${m.hint}</small></label>
    <span class="val"><input type="number" id="n-${m.key}" min="${m.min}" max="${m.max}" step="${m.step}" value="${m.value}" aria-label="${m.label} value"> ${m.unit}</span>
    <input type="range" id="r-${m.key}" min="${m.min}" max="${m.max}" step="${m.step}" value="${m.value}">`;
  form.appendChild(row);
  const r = row.querySelector('[type=range]'), n = row.querySelector('[type=number]');
  r.addEventListener('input', () => { n.value = r.value; schedule(); });
  n.addEventListener('input', () => { r.value = n.value; schedule(); });
});

function values() {
  const v = {};
  META.forEach(m => v[m.key] = parseFloat(document.getElementById('r-' + m.key).value));
  return v;
}
function setValues(v) {
  META.forEach(m => {
    document.getElementById('r-' + m.key).value = v[m.key];
    document.getElementById('n-' + m.key).value = v[m.key];
  });
  schedule(0);
}
function schedule(delay = 120) { clearTimeout(timer); timer = setTimeout(() => predict(false), delay); }

document.querySelectorAll('[data-preset]').forEach(b =>
  b.addEventListener('click', () => setValues(PRESETS[b.dataset.preset])));

async function predict(save, fieldName) {
  const res = await fetch('/api/predict', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({...values(), save, field_name: fieldName})
  });
  if (!res.ok) { result.innerHTML = '<p class="muted">Check that every value is a number.</p>'; return; }
  const data = await res.json();
  colors = data.colors;
  if (save) toast('Saved to your fields.');
  render(data);
}

function render(d) {
  const best = d.top[0], c = colors[best.crop];
  const adv = d.advice.length
    ? d.advice.map(a => `<li class="${a.status}">${a.message}</li>`).join('')
    : '<li class="ok">Conditions look close to ideal for this crop.</li>';
  const keepName = (document.getElementById('fieldName') || {}).value || '';
  result.style.setProperty('--crop', c);
  result.innerHTML = `
    <p class="muted">Best match</p>
    <h2 class="crop-name">${best.crop}</h2>
    <p class="conf"><strong>${best.probability}%</strong> of the model's trees agree</p>
    <div class="bars">
      ${d.top.map(t => `
        <div class="bar"><span>${t.crop}</span>
          <div class="track"><i style="width:${t.probability}%;background:${colors[t.crop]}"></i></div>
          <b>${t.probability}%</b></div>`).join('')}
    </div>
    <dl class="facts">
      <div><dt>Season</dt><dd>${d.info.season}</dd></div>
      <div><dt>Water need</dt><dd>${d.info.water}</dd></div>
      <div><dt>Soil</dt><dd>${d.info.soil}</dd></div>
      <div><dt>Duration</dt><dd>${d.info.days}</dd></div>
    </dl>
    <p class="tip">${d.info.tip}</p>
    <h3>What to adjust</h3>
    <ul class="advice">${adv}</ul>
    <div class="save">
      <input id="fieldName" maxlength="40" placeholder="Field name, e.g. North plot" value="${keepName}" aria-label="Field name">
      <button class="btn" id="saveBtn" type="button">Save this field</button>
    </div>`;
  document.getElementById('saveBtn').addEventListener('click', () =>
    predict(true, document.getElementById('fieldName').value));
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}
predict(false);
