'use strict';
document.querySelectorAll('[data-confirm]').forEach(form => {
  form.addEventListener('submit', event => {
    if (!window.confirm('Удалить эту запись?')) event.preventDefault();
  });
});
const kind = document.querySelector('select[name=kind]');
if (kind) {
  const update = () => {
    const cardio = kind.value === 'cardio';
    for (const key of ['minutes', 'sets', 'reps', 'load']) {
      const label = document.querySelector('[data-field=' + key + ']');
      const input = label.querySelector('input');
      label.hidden = key === 'minutes' ? !cardio : cardio;
      input.disabled = label.hidden;
      input.required = !label.hidden && key !== 'load';
    }
  };
  kind.addEventListener('change', update);
  update();
}
for (const chart of document.querySelectorAll('.chart')) {
  const points = JSON.parse(chart.dataset.points);
  const times = points.map(([day]) => Date.parse(day));
  const values = points.map(([,value]) => value);
  const min = values.reduce((a,b) => Math.min(a,b));
  const max = values.reduce((a,b) => Math.max(a,b));
  const span = times.at(-1) - times[0];
  const xy = values.map((value,i) => [
    span ? 61 + 527 * (times[i]-times[0]) / span : 324.5,
    max === min ? 80 : 134 - 112 * (value-min) / (max-min)
  ]);
  const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 620 169');
  svg.setAttribute('aria-hidden','true');
  const add = (tag, attrs, content, parent = svg) => {
    const el = document.createElementNS(svg.namespaceURI,tag);
    for (const [k,v] of Object.entries(attrs)) el.setAttribute(k,v);
    if (content) el.textContent = content;
    parent.append(el);
    return el;
  };
  for (const [y, v] of max === min ? [[80,min]] : [[22,max],[78,(max+min)/2],[134,min]]) {
    add('line',{x1:60,x2:590,y1:y,y2:y,class:'guide'});
    add('text',{x:54,y:y+4,'text-anchor':'end'},String(+v.toFixed(1)));
  }
  add('polyline',{points:xy.map(p=>p.join(',')).join(' '),class:'trend'});
  xy.forEach(([x,y],i) => add('title',{},points[i].join(' · '),add('circle',{cx:x,cy:y,r:4})));
  add('text',{x:61,y:158},points[0][0]);
  if (span) add('text',{x:588,y:158,'text-anchor':'end'},points.at(-1)[0]);
  chart.append(svg);
}
