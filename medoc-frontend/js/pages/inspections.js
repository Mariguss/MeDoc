import { h, icon, toast, formModal, empty, fmtDateTime, statusLabel, toIso, toLocalInput } from '../ui.js';
import * as api from '../api.js';

const ADDR = 'ул. Малая Семеновская д.13';
const nz = v => (v === '' || v == null ? undefined : v);
const statusOpts = Object.entries(statusLabel).map(([value, label]) => ({ value, label }));

// журнал приёмов, созданных в этом браузере (в бэкенде пока нет списка приёмов)
const jkey = () => 'medoc_journal_' + api.session.uid;
const jread = () => { try { return JSON.parse(localStorage.getItem(jkey())) || []; } catch { return []; } };
const jwrite = a => { try { localStorage.setItem(jkey(), JSON.stringify(a.slice(0, 200))); } catch {} };
const jupsert = rec => { const a = jread().filter(x => x.id !== rec.id); a.unshift({ ...(jread().find(x => x.id === rec.id) || {}), ...rec }); jwrite(a); };

// конструктор назначений: лекарство + способ приёма
function prescriptionsField(meds) {
  const list = h('div', { class: 'rx-list' });
  const add = () => {
    const med = h('select', { 'aria-label': 'Лекарство' }, h('option', { value: '' }, 'Лекарство…'), meds.map(m => h('option', { value: m.id }, m.name)));
    const how = h('input', { placeholder: 'Как принимать: 2 раза в день после еды', 'aria-label': 'Способ приёма' });
    const row = h('div', { class: 'rx-row' }, med, how, h('button', { type: 'button', class: 'icon-btn danger', 'aria-label': 'Убрать назначение', onclick: () => row.remove() }, icon('trash')));
    list.append(row);
  };
  const el = h('div', { class: 'rx' }, list, h('button', { type: 'button', class: 'btn ghost sm', onclick: add }, icon('plus'), 'Назначить лекарство'));
  return {
    el,
    get: () => [...list.children].map(r => ({ medicine_id: Number(r.querySelector('select').value), intake_method: nz(r.querySelector('input').value.trim()) })).filter(x => x.medicine_id),
  };
}

export async function inspectionsPage(root) {
  const admin = api.session.isAdmin;
  const head = h('div', { class: 'page-head' },
    h('div', {}, h('h1', {}, admin ? 'Приёмы и вызовы' : 'Мои приёмы'), h('p', { class: 'sub' }, admin ? 'Запись пациентов к врачам и правка записей' : 'Осмотры пациентов: симптомы, диагнозы и назначения')),
    h('button', { class: 'btn primary', onclick: () => openCreate() }, icon('plus'), admin ? 'Записать на приём' : 'Новый осмотр'));
  const list = h('div', { class: 'card table-card' });
  const byId = h('form', { class: 'by-id', onsubmit: e => { e.preventDefault(); const n = Number(num.value); if (n > 0) openEdit({ id: n }); } });
  const num = h('input', { type: 'number', min: 1, placeholder: 'Номер приёма', 'aria-label': 'Номер приёма' });
  byId.append(num, h('button', { class: 'btn ghost sm' }, icon('edit'), 'Изменить по номеру'));
  root.append(head, h('div', { class: 'toolbar' }, byId), list);

  let names = { p: new Map(), d: new Map() };
  async function loadNames() {
    try { (await api.listAll('patient')).forEach(p => names.p.set(p.id, p.name)); } catch {}
    if (admin) { try { (await api.listAll('employee')).forEach(e => names.d.set(e.id, e.name)); } catch {} }
  }

  async function draw() {
    let rows = null, server = false;
    try { rows = await api.inspections.tryList(); server = !!rows; } catch {}
    if (!rows) rows = jread();
    if (!rows.length) {
      list.replaceChildren(empty('Приёмов пока нет', 'Созданные здесь приёмы появятся в этом списке. Полный список появится, когда в бэкенде включат GET /inspection/.'));
      return;
    }
    const table = h('table', {},
      h('thead', {}, h('tr', {}, ['№', 'Дата', 'Пациент', admin ? 'Врач' : null, 'Адрес', 'Статус', ''].filter(x => x !== null).map((t, i) => h('th', { class: t === '№' ? 'num' : t === '' ? 'act' : '' }, t)))),
      h('tbody', {}, rows.map(r => h('tr', {},
        h('td', { class: 'num', 'data-label': '№' }, r.id),
        h('td', { 'data-label': 'Дата' }, fmtDateTime(r.inspection_at)),
        h('td', { 'data-label': 'Пациент' }, h('strong', {}, names.p.get(r.patient_id) || `№${r.patient_id}`)),
        admin ? h('td', { 'data-label': 'Врач' }, names.d.get(r.doctor_id) || `№${r.doctor_id}`) : null,
        h('td', { 'data-label': 'Адрес' }, r.address || '—'),
        h('td', { 'data-label': 'Статус' }, r.status ? h('span', { class: 'pill ' + (r.status === 'completed' ? 'ok' : r.status === 'scheduled' ? 'cool' : 'warn') }, statusLabel[r.status] || r.status) : '—'),
        h('td', { class: 'act' }, h('button', { class: 'icon-btn', title: 'Изменить', 'aria-label': 'Изменить приём', onclick: () => openEdit(r) }, icon('edit')))))));
    list.replaceChildren(...[h('div', { class: 'table-wrap' }, table),
      server ? null : h('p', { class: 'note' }, 'Показаны приёмы, созданные в этом браузере.')].filter(Boolean));
  }

  const people = async () => {
    const [patients, diseases, meds, doctors] = await Promise.all([
      api.listAll('patient'), api.listAll('disease'), api.listAll('medicine'),
      admin ? api.listAll('employee') : Promise.resolve([]),
    ]);
    return { patients, diseases, meds, doctors: doctors.filter(d => String(d.role).toLowerCase() === 'doctor') };
  };

  async function openCreate() {
    let d;
    try { d = await people(); } catch (e) { toast(e.message, 'err'); return; }
    if (!d.patients.length) { toast('Сначала добавьте пациента в разделе «Пациенты»', 'err'); return; }
    const patientField = { name: 'patient_id', label: 'Пациент', type: 'select', required: true, full: true, options: d.patients.map(p => ({ value: p.id, label: p.name })) };
    if (admin) {
      if (!d.doctors.length) { toast('Нет ни одного врача — добавьте сотрудника с ролью «Врач»', 'err'); return; }
      formModal({
        title: 'Записать на приём',
        fields: [
          patientField,
          { name: 'doctor_id', label: 'Врач', type: 'select', required: true, full: true, options: d.doctors.map(x => ({ value: x.id, label: x.name + (x.speciality ? ` — ${x.speciality}` : '') })) },
          { name: 'inspection_at', label: 'Дата и время', type: 'datetime-local', required: true },
          { name: 'address', label: 'Адрес', full: true, placeholder: ADDR },
        ],
        values: { address: ADDR }, submitLabel: 'Записать',
        onSubmit: async v => {
          const r = await api.inspections.createAdmin({ patient_id: +v.patient_id, doctor_id: +v.doctor_id, inspection_at: toIso(v.inspection_at), address: v.address || ADDR });
          jupsert({ ...r, status: 'scheduled' });
          toast(`Приём №${r.id} создан`); await draw();
        },
      });
    } else {
      formModal({
        title: 'Новый осмотр', wide: true,
        fields: [
          patientField,
          { name: 'inspection_at', label: 'Дата и время', type: 'datetime-local' },
          { name: 'status', label: 'Статус', type: 'select', options: statusOpts },
          { name: 'address', label: 'Место осмотра', full: true, placeholder: ADDR },
          { name: 'symptoms', label: 'Симптомы', type: 'textarea', full: true },
          { name: 'disease_ids', label: 'Диагноз', type: 'chips', full: true, options: d.diseases.map(x => ({ value: x.id, label: x.name })), emptyText: 'В справочнике нет болезней — их добавляет администратор' },
          { name: 'rx', label: 'Назначения', full: true, custom: () => prescriptionsField(d.meds) },
          { name: 'instructions', label: 'Предписания больному', type: 'textarea', full: true },
        ],
        values: { status: 'completed', address: ADDR }, submitLabel: 'Сохранить осмотр',
        onSubmit: async v => {
          const body = { patient_id: +v.patient_id, address: v.address || ADDR, symptoms: nz(v.symptoms), instructions: nz(v.instructions), status: v.status || 'completed', inspection_at: toIso(v.inspection_at) || undefined };
          // Диагнозы и назначения отправляем вторым шагом (PATCH): так надёжнее при текущем бэкенде.
          const r = await api.inspections.createDoctor(body);
          jupsert({ ...r, status: body.status });
          if (v.disease_ids.length || v.rx.length) {
            const extra = {};
            if (v.disease_ids.length) extra.disease_ids = v.disease_ids;
            if (v.rx.length) extra.prescriptions_create = v.rx;
            try { await api.inspections.patchDoctor(r.id, extra); }
            catch (e) { toast(`Осмотр №${r.id} создан, но диагноз и назначения не сохранились: ${e.message}`, 'err'); await draw(); return; }
          }
          toast(`Осмотр №${r.id} сохранён`); await draw();
        },
      });
    }
  }

  async function openEdit(rec) {
    let d;
    try { d = await people(); } catch (e) { toast(e.message, 'err'); return; }
    const pf = { name: 'patient_id', label: 'Пациент', type: 'select', full: true, options: d.patients.map(p => ({ value: p.id, label: p.name })) };
    const hint = rec.patient_id ? null : 'Заполните только то, что нужно изменить — остальное останется как есть.';
    const common = { title: `Приём №${rec.id}`, submitLabel: 'Сохранить' };
    if (admin) {
      formModal({ ...common,
        fields: [pf,
          { name: 'doctor_id', label: 'Врач', type: 'select', full: true, options: d.doctors.map(x => ({ value: x.id, label: x.name })) },
          { name: 'inspection_at', label: 'Дата и время', type: 'datetime-local', hint },
          { name: 'address', label: 'Адрес', full: true }],
        values: { ...rec, inspection_at: toLocalInput(rec.inspection_at) },
        onSubmit: async v => {
          const body = {};
          if (v.patient_id) body.patient_id = +v.patient_id;
          if (v.doctor_id) body.doctor_id = +v.doctor_id;
          if (v.inspection_at) body.inspection_at = toIso(v.inspection_at);
          if (v.address) body.address = v.address;
          const r = await api.inspections.patchAdmin(rec.id, body);
          jupsert({ ...r }); toast('Приём обновлён'); await draw();
        } });
    } else {
      formModal({ ...common, wide: true,
        fields: [pf,
          { name: 'status', label: 'Статус', type: 'select', options: statusOpts },
          { name: 'inspection_at', label: 'Дата и время', type: 'datetime-local', hint },
          { name: 'address', label: 'Место осмотра', full: true },
          { name: 'symptoms', label: 'Симптомы', type: 'textarea', full: true },
          { name: 'disease_ids', label: 'Диагноз (заменит прежний)', type: 'chips', full: true, options: d.diseases.map(x => ({ value: x.id, label: x.name })), emptyText: 'В справочнике нет болезней' },
          { name: 'rx', label: 'Добавить назначения', full: true, custom: () => prescriptionsField(d.meds) },
          { name: 'instructions', label: 'Предписания больному', type: 'textarea', full: true }],
        values: { ...rec, inspection_at: toLocalInput(rec.inspection_at) },
        onSubmit: async v => {
          const body = {};
          if (v.patient_id) body.patient_id = +v.patient_id;
          if (v.status) body.status = v.status;
          if (v.inspection_at) body.inspection_at = toIso(v.inspection_at);
          for (const k of ['address', 'symptoms', 'instructions']) if (v[k]) body[k] = v[k];
          if (v.disease_ids.length) body.disease_ids = v.disease_ids;
          if (v.rx.length) body.prescriptions_create = v.rx;
          const r = await api.inspections.patchDoctor(rec.id, body);
          jupsert({ ...r, status: body.status || rec.status }); toast('Осмотр обновлён'); await draw();
        } });
    }
  }

  list.append(h('div', { class: 'skeleton' }, h('i'), h('i')));
  await loadNames();
  draw();
}
