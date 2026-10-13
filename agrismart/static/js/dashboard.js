fetch('/api/stats').then(r => r.json()).then(s => {
  const k = s.kpis;
  document.getElementById('kpis').innerHTML = [
    [k.rows, 'sample fields in the database'], [k.crops, 'crops the model knows'],
    [k.accuracy + '%', 'accuracy on unseen fields'], [k.saved, 'fields you have saved']
  ].map(([n, l]) => `<div class="kpi"><b>${n}</b><span>${l}</span></div>`).join('');

  const css = getComputedStyle(document.documentElement);
  Chart.defaults.font.family = "'Source Sans 3', sans-serif";
  Chart.defaults.color = css.getPropertyValue('--ink').trim();
  const label = f => ({N:'Nitrogen',P:'Phosphorus',K:'Potassium',temperature:'Temp',humidity:'Humidity',ph:'pH',rainfall:'Rainfall'}[f] || f);

  new Chart('scatter', {
    type: 'scatter',
    data: { datasets: Object.entries(s.scatter).map(([crop, pts]) =>
      ({label: crop, data: pts, backgroundColor: s.colors[crop], pointRadius: 4})) },
    options: { maintainAspectRatio: false,
      scales: { x: {title: {display: true, text: 'Temperature (°C)'}}, y: {title: {display: true, text: 'Rainfall (mm)'}} } }
  });

  const pick = document.getElementById('cropPick'), crops = Object.keys(s.radar);
  pick.innerHTML = crops.map(c => `<option>${c}</option>`).join('');
  const radar = new Chart('radar', {
    type: 'radar',
    data: { labels: s.features.map(label), datasets: [{label: crops[0], data: s.radar[crops[0]],
      backgroundColor: s.colors[crops[0]] + '55', borderColor: s.colors[crops[0]], borderWidth: 2 }] },
    options: { maintainAspectRatio: false, plugins: {legend: {display: false}},
      scales: { r: {min: 0, max: 100, ticks: {display: false}} } }
  });
  pick.addEventListener('change', () => {
    const c = pick.value, ds = radar.data.datasets[0];
    ds.data = s.radar[c]; ds.backgroundColor = s.colors[c] + '55'; ds.borderColor = s.colors[c];
    radar.update();
  });

  new Chart('importance', {
    type: 'bar',
    data: { labels: s.importance.map(i => label(i.feature)),
            datasets: [{data: s.importance.map(i => i.value), backgroundColor: css.getPropertyValue('--leaf').trim()}] },
    options: { indexAxis: 'y', maintainAspectRatio: false, plugins: {legend: {display: false}} }
  });

  const names = Object.keys(s.saved_by_crop);
  if (!names.length) { document.getElementById('saved').parentElement.hidden = true; document.getElementById('savedEmpty').hidden = false; }
  else new Chart('saved', {
    type: 'bar',
    data: { labels: names, datasets: [{data: names.map(n => s.saved_by_crop[n]), backgroundColor: names.map(n => s.colors[n])}] },
    options: { maintainAspectRatio: false, plugins: {legend: {display: false}}, scales: {y: {ticks: {precision: 0}}} }
  });
});
