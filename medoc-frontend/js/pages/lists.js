import { h, fmtDate, fmtPhone, sexLabel, roleLabel } from '../ui.js';
import { crudPage } from '../crud.js';

const nz = v => (v === '' || v == null ? null : v);
const isAdmin = r => r === 'admin';
const pill = (t, cls = '') => h('span', { class: 'pill ' + cls }, t);

export const patients = crudPage({
  resource: 'patient', title: 'Пациенты', subtitle: 'Люди, которых наблюдает кооператив',
  addLabel: 'Новый пациент', editTitle: 'Данные пациента', label: p => p.name,
  searchKeys: ['name', 'home_address', 'phone_number'], searchPlaceholder: 'Имя, адрес или телефон',
  emptyTitle: 'Пациентов пока нет', emptyText: 'Добавьте первого пациента, чтобы записывать его на приём.',
  canCreate: isAdmin, canEdit: isAdmin, canDelete: isAdmin,
  columns: [
    { label: '№', key: 'id', cls: 'num' },
    { label: 'ФИО', render: p => h('strong', {}, p.name) },
    { label: 'Пол', render: p => sexLabel(p.sex) },
    { label: 'Дата рождения', render: p => fmtDate(p.born_date) },
    { label: 'Телефон', render: p => fmtPhone(p.phone_number) },
    { label: 'Адрес', key: 'home_address' },
  ],
  fields: [
    { name: 'name', label: 'ФИО', required: true, maxlength: 50, full: true },
    { name: 'sex', label: 'Пол', type: 'select', required: true, options: [{ value: 'f', label: 'Женский' }, { value: 'm', label: 'Мужской' }] },
    { name: 'born_date', label: 'Дата рождения', type: 'date', required: true },
    { name: 'phone_number', label: 'Телефон', required: true, pattern: '\\d{11}', title: '11 цифр без пробелов', placeholder: '79001234567', hint: '11 цифр, например 79001234567' },
    { name: 'home_address', label: 'Домашний адрес', full: true },
  ],
  toForm: p => ({ ...p, sex: /^m/i.test(p.sex) ? 'm' : 'f' }),
  toBody: v => ({ name: v.name, sex: v.sex, born_date: v.born_date, phone_number: v.phone_number, home_address: nz(v.home_address) }),
  createdText: 'Пациент добавлен',
});

export const medicines = crudPage({
  resource: 'medicine', title: 'Лекарства', subtitle: 'Справочник препаратов, их действие и побочные эффекты',
  addLabel: 'Новое лекарство', editTitle: 'Данные лекарства', label: m => m.name,
  searchKeys: ['name', 'properties', 'side_effects'], searchPlaceholder: 'Название или действие',
  emptyTitle: 'Справочник пуст', emptyText: 'Добавьте лекарство с описанием действия и побочных эффектов.',
  canCreate: isAdmin, canEdit: isAdmin, canDelete: isAdmin,
  columns: [
    { label: '№', key: 'id', cls: 'num' },
    { label: 'Название', render: m => h('strong', {}, m.name) },
    { label: 'Действие', key: 'properties' },
    { label: 'Побочные эффекты', render: m => pill(m.side_effects, 'warn') },
  ],
  fields: [
    { name: 'name', label: 'Название', required: true, maxlength: 50, full: true },
    { name: 'properties', label: 'Действие и свойства', type: 'textarea', required: true, full: true },
    { name: 'side_effects', label: 'Побочные эффекты', type: 'textarea', required: true, full: true },
  ],
  toBody: v => ({ name: v.name, properties: v.properties, side_effects: v.side_effects }),
  createdText: 'Лекарство добавлено',
});

export const diseases = crudPage({
  resource: 'disease', title: 'Болезни', subtitle: 'Справочник диагнозов для приёмов',
  addLabel: 'Новая болезнь', editTitle: 'Название болезни', label: d => d.name,
  searchKeys: ['name'], searchPlaceholder: 'Название болезни',
  emptyTitle: 'Диагнозов пока нет', emptyText: 'Добавьте болезнь — её можно будет указать на приёме.',
  canCreate: isAdmin, canEdit: isAdmin, canDelete: isAdmin,
  columns: [
    { label: '№', key: 'id', cls: 'num' },
    { label: 'Название', render: d => h('strong', {}, d.name) },
  ],
  fields: [{ name: 'name', label: 'Название', required: true, maxlength: 50, full: true }],
  toBody: v => ({ name: v.name }),
  createdText: 'Болезнь добавлена',
});

export const employees = crudPage({
  resource: 'employee', title: 'Сотрудники', subtitle: 'Врачи и администраторы кооператива',
  addLabel: 'Новый сотрудник', editTitle: 'Данные сотрудника', label: e => e.name,
  searchKeys: ['name', 'login', 'speciality'], searchPlaceholder: 'Имя, логин или специальность',
  emptyTitle: 'Сотрудников нет', emptyText: 'Добавьте врача или администратора.',
  columns: [
    { label: '№', key: 'id', cls: 'num' },
    { label: 'ФИО', render: e => h('strong', {}, e.name) },
    { label: 'Логин', key: 'login' },
    { label: 'Роль', render: e => pill(roleLabel(e.role), String(e.role).toLowerCase() === 'admin' ? 'cool' : '') },
    { label: 'Специальность', render: e => e.speciality || '—' },
  ],
  fields: it => [
    { name: 'name', label: 'ФИО', required: true, maxlength: 50, full: true },
    { name: 'login', label: 'Логин', required: true, minlength: 5, maxlength: 15, pattern: '[A-Za-z0-9_]+', hint: '5–15 символов: латиница, цифры, _' },
    { name: 'role', label: 'Роль', type: 'select', required: true, options: [{ value: 'doctor', label: 'Врач' }, { value: 'admin', label: 'Администратор' }] },
    { name: 'speciality', label: 'Специальность', maxlength: 50, full: true },
    ...(it ? [] : [{ name: 'password', label: 'Пароль', type: 'password', required: true, minlength: 8, full: true, hint: 'От 8 символов: заглавная и строчная буква, цифра и спецсимвол (!@#$%…)' }]),
  ],
  toForm: e => ({ ...e, role: String(e.role).toLowerCase() }),
  toBody: (v, edit) => ({ login: v.login, name: v.name, role: v.role, speciality: nz(v.speciality), ...(edit ? {} : { password: v.password }) }),
  createdText: 'Сотрудник добавлен',
});
