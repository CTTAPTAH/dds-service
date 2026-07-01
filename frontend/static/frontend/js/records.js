// Базовый URL нашего API
const API = '/api';

// Загружаем данные для фильтров при старте страницы
async function loadFilters() {
    // Загружаем статусы
    const statuses = await fetch(`${API}/statuses/`).then(r => r.json());
    fillSelect('filter-status', statuses);

    // Загружаем типы
    const types = await fetch(`${API}/transaction-types/`).then(r => r.json());
    fillSelect('filter-type', types);

    // Загружаем категории
    const categories = await fetch(`${API}/categories/`).then(r => r.json());
    fillSelect('filter-category', categories);

    // Загружаем подкатегории
    const subcategories = await fetch(`${API}/subcategories/`).then(r => r.json());
    fillSelect('filter-subcategory', subcategories);
}

// Заполняет select вариантами из API
function fillSelect(elementId, items) {
    const select = document.getElementById(elementId);
    // Оставляем первый option "Все" и добавляем остальные
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        select.appendChild(option);
    });
}

// Загружаем записи ДДС с учётом фильтров
async function loadRecords() {
    const params = new URLSearchParams();

    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    const status = document.getElementById('filter-status').value;
    const type = document.getElementById('filter-type').value;
    const category = document.getElementById('filter-category').value;
    const subcategory = document.getElementById('filter-subcategory').value;

    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    if (subcategory) params.append('subcategory', subcategory);

    // Фильтр по типу. Идём через категории
    if (type && !category) {
        const categories = await fetch(`${API}/categories/?transaction_type=${type}`).then(r => r.json());
        const categoryIds = categories.map(c => c.id);
        if (categoryIds.length > 0) {
            categoryIds.forEach(id => params.append('category', id));
        } else {
            // Нет категорий этого типа, таблица будет пустой
            renderRecords([]);
            return;
        }
    }

    const records = await fetch(`${API}/records/?${params.toString()}`).then(r => r.json());
    renderRecords(records);
}

// Отрисовываем записи в таблице
function renderRecords(records) {
    const tbody = document.getElementById('records-table-body');

    if (records.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Записей не найдено</td></tr>';
        return;
    }

    tbody.innerHTML = records.map(record => `
        <tr>
            <td>${record.date}</td>
            <td>${record.status_name}</td>
            <td>${record.transaction_type_name}</td>
            <td>${record.category_name}</td>
            <td>${record.subcategory_name}</td>
            <td>${Number(record.amount).toLocaleString('ru-RU')} р.</td>
            <td>${record.comment || '—'}</td>
            <td>
                <a href="/records/${record.id}/edit/" class="btn btn-sm btn-outline-primary">✏️</a>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteRecord(${record.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// Удаление записи
async function deleteRecord(id) {
    if (!confirm('Удалить эту запись?')) return;

    await fetch(`${API}/records/${id}/`, {
        method: 'DELETE',
        headers: {'X-CSRFToken': getCookie('csrftoken')},
    });

    loadRecords();
}

// CSRF-токен для Django
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Кнопки фильтров
document.getElementById('btn-apply-filters').addEventListener('click', loadRecords);
document.getElementById('btn-reset-filters').addEventListener('click', () => {
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    document.getElementById('filter-status').value = '';
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-subcategory').value = '';
    loadRecords();
});

// Запуск при загрузке страницы
loadFilters();
loadRecords();