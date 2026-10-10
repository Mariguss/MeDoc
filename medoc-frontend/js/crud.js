// Универсальная страница-справочник: поиск, таблица, постраничный вывод, добавление, правка, удаление.
import { h, icon, toast, formModal, confirmBox, empty, skeleton } from './ui.js';
import * as api from './api.js';

const PAGE = 10;

export function crudPage(cfg) {
  return async function render(root) {
    const can = {
      create: cfg.canCreate ? cfg.canCreate(api.session.role) : true,
      edit: cfg.canEdit ? cfg.canEdit(api.session.role) : true,
      del: cfg.canDelete ? cfg.canDelete(api.session.role) : true,
    };
    let items = [], q = '', page = 1;

    const search = h('input', { type: 'search', placeholder: cfg.searchPlaceholder || 'Поиск…', 'aria-label': 'Поиск', oninput: e => { q = e.target.value.toLowerCase(); page = 1; draw(); } });
    const addBtn = can.create ? h('button', { class: 'btn primary', onclick: () => openForm() }, icon('plus'), cfg.addLabel || 'Добавить') : null;
    const head = h('div', { class: 'page-head' },
      h('div', {}, h('h1', {}, cfg.title), h('p', { class: 'sub' }, cfg.subtitle)),
      addBtn);
    const bar = h('div', { class: 'toolbar' }, h('label', { class: 'search' }, icon('search'), search), h('span', { class: 'count' }));
    const body = h('div', { class: 'card table-card' }, skeleton());
    root.append(head, bar, body);

    async function load(force) {
      try { items = await api.listAll(cfg.resource, { force }); draw(); }
      catch (e) {
        body.replaceChildren(empty('Не удалось загрузить данные', e.message,
          h('button', { class: 'btn ghost', onclick: () => { body.replaceChildren(skeleton()); load(true); } }, 'Повторить')));
      }
    }

    function draw() {
      const list = items.filter(it => !q || cfg.searchKeys.some(k => String(cfg.text ? cfg.text(it, k) : it[k] ?? '').toLowerCase().includes(q)));
      bar.querySelector('.count').textContent = `${list.length} из ${items.length}`;
      if (!list.length) {
        body.replaceChildren(items.length
          ? empty('Ничего не найдено', 'Измените запрос поиска.')
          : empty(cfg.emptyTitle, cfg.emptyText, can.create ? h('button', { class: 'btn primary', onclick: () => openForm() }, icon('plus'), cfg.addLabel || 'Добавить') : null));
        return;
      }
      const pages = Math.ceil(list.length / PAGE);
      page = Math.min(page, pages);
      const slice = list.slice((page - 1) * PAGE, page * PAGE);
      const table = h('table', {},
        h('thead', {}, h('tr', {}, cfg.columns.map(c => h('th', { class: c.cls }, c.label)), (can.edit || can.del) ? h('th', { class: 'act' }, '') : null)),
        h('tbody', {}, slice.map(it => h('tr', {},
          cfg.columns.map(c => h('td', { class: c.cls, 'data-label': c.label }, c.render ? c.render(it) : (it[c.key] ?? '—'))),
          (can.edit || can.del) ? h('td', { class: 'act' },
            can.edit ? h('button', { class: 'icon-btn', title: 'Изменить', 'aria-label': 'Изменить', onclick: () => openForm(it) }, icon('edit')) : null,
            can.del ? h('button', { class: 'icon-btn danger', title: 'Удалить', 'aria-label': 'Удалить', onclick: () => del(it) }, icon('trash')) : null) : null))));
      const pager = pages > 1 ? h('div', { class: 'pager' },
        h('button', { class: 'btn ghost sm', disabled: page === 1, onclick: () => { page--; draw(); } }, 'Назад'),
        h('span', {}, `Страница ${page} из ${pages}`),
        h('button', { class: 'btn ghost sm', disabled: page === pages, onclick: () => { page++; draw(); } }, 'Вперёд')) : null;
      body.replaceChildren(...[h('div', { class: 'table-wrap' }, table), pager].filter(Boolean));
    }

    async function openForm(it) {
      const fields = typeof cfg.fields === 'function' ? await cfg.fields(it) : cfg.fields;
      formModal({
        title: it ? cfg.editTitle : cfg.addLabel, fields, values: it ? (cfg.toForm ? cfg.toForm(it) : it) : {},
        submitLabel: it ? 'Сохранить' : (cfg.addLabel || 'Добавить'),
        onSubmit: async v => {
          const payload = cfg.toBody(v, !!it);
          if (it) { await api.patch(cfg.resource, it.id, payload); toast(cfg.savedText || 'Изменения сохранены'); }
          else { await api.create(cfg.resource, payload); toast(cfg.createdText || 'Добавлено'); }
          await load(true);
        },
      });
    }

    async function del(it) {
      if (!await confirmBox(cfg.deleteTitle || 'Удалить запись?', `«${cfg.label(it)}» будет удалено без возможности восстановления.`)) return;
      try { await api.remove(cfg.resource, it.id); toast(cfg.deletedText || 'Удалено'); await load(true); }
      catch (e) { toast(e.message, 'err'); }
    }

    load(true);
  };
}
