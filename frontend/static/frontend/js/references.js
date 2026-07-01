const API = '/api';

// Текущее состояние модального окна
let currentResource = null;
let currentId = null;

// Конфигурация справочников
const RESOURCES = {
    'status': {
        label: 'Статус',
        endpoint: 'statuses',
        fields: () => `
            <div class="mb-3">
                <label class="form-label">Название</label>
                <input type="text" id="modal-name" class="form-control" required>
            </div>
        `,
        getData: () => ({ name: document.getElementById('modal-name').value }),
        setData: (item) => { document.getElementById('modal-name').value = item.name; },
        renderRow: (item) => `<td>${item.name}</td>`,
    },
    'transaction-type': {
        label: 'Тип операции',
        endpoint: 'transaction-types',
        fields: () => `
            <div class="mb-3">
                <label class="form-label">Название</label>
                <input type="text" id="modal-name" class="form-control" required>
            </div>
        `,
        getData: () => ({ name: document.getElementById('modal-name').value }),
        setData: (item) => { document.getElementById('modal-name').value = item.name; },
        renderRow: (item) => `<td>${item.name}</td>`,
    },
    'category': {
        label: 'Категория',
        endpoint: 'categories',
        fields: async () => {
            const types = await fetch(`${API}/transaction-types/`).then(r => r.json());
            const options = types.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
            return `
                <div class="mb-3">
                    <label class="form-label">Название</label>
                    <input type="text" id="modal-name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Тип операции</label>
                    <select id="modal-type" class="form-select" required>
                        <option value="">— выберите —</option>
                        ${options}
                    </select>
                </div>
            `;
        },
        getData: () => ({
            name: document.getElementById('modal-name').value,
            transaction_type: document.getElementById('modal-type').value,
        }),
        setData: (item) => {
            document.getElementById('modal-name').value = item.name;
            document.getElementById('modal-type').value = item.transaction_type;
        },
        renderRow: (item) => `<td>${item.name}</td><td class="text-muted">${item.transaction_type_name || ''}</td>`,
    },
    'subcategory': {
        label: 'Подкатегория',
        endpoint: 'subcategories',
        fields: async () => {
            const categories = await fetch(`${API}/categories/`).then(r => r.json());
            const options = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
            return `
                <div class="mb-3">
                    <label class="form-label">Название</label>
                    <input type="text" id="modal-name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Категория</label>
                    <select id="modal-category" class="form-select" required>
                        <option value="">— выберите —</option>
                        ${options}
                    </select>
                </div>
            `;
        },
        getData: () => ({
            name: document.getElementById('modal-name').value,
            category: document.getElementById('modal-category').value,
        }),
        setData: (item) => {
            document.getElementById('modal-name').value = item.name;
            document.getElementById('modal-category').value = item.category;
        },
        renderRow: (item) => `<td>${item.name}</td><td class="text-muted">${item.category_name || ''}</td>`,
    },
};

// Загружаем список для одного справочника
async function loadList(resource) {
    const config = RESOURCES[resource];
    const items = await fetch(`${API}/${config.endpoint}/`).then(r => r.json());
    const tbody = document.getElementById(`list-${resource}`);

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td class="text-muted p-2">Пусто</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(item => `
        <tr>
            ${config.renderRow(item)}
            <td class="text-end pe-2">
                <button class="btn btn-sm btn-outline-primary me-1"
                    onclick="openModal('${resource}', ${item.id})">✏️</button>
                <button class="btn btn-sm btn-outline-danger"
                    onclick="deleteItem('${resource}', ${item.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

// Загружаем все справочники
function loadAll() {
    Object.keys(RESOURCES).forEach(loadList);
}

// Открываем модальное окно
async function openModal(resource, id = null) {
    currentResource = resource;
    currentId = id;

    const config = RESOURCES[resource];
    const modal = new bootstrap.Modal(document.getElementById('refModal'));

    document.getElementById('modal-title').textContent =
        id ? `Редактировать: ${config.label}` : `Добавить: ${config.label}`;
    document.getElementById('modal-errors').classList.add('d-none');

    // Рендерим поля (fields может быть async)
    document.getElementById('modal-fields').innerHTML = await config.fields();

    // Если редактируем — заполняем поля данными
    if (id) {
        const item = await fetch(`${API}/${config.endpoint}/${id}/`).then(r => r.json());
        config.setData(item);
    }

    modal.show();
}

// Сохраняем (создание или редактирование)
async function saveItem() {
    const config = RESOURCES[currentResource];
    const data = config.getData();

    const url = currentId
        ? `${API}/${config.endpoint}/${currentId}/`
        : `${API}/${config.endpoint}/`;
    const method = currentId ? 'PUT' : 'POST';

    const response = await fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    });

    if (response.ok) {
        bootstrap.Modal.getInstance(document.getElementById('refModal')).hide();
        loadList(currentResource);
    } else {
        const errors = await response.json();
        const block = document.getElementById('modal-errors');
        block.classList.remove('d-none');
        block.innerHTML = Object.entries(errors)
            .map(([f, m]) => `<div>${f}: ${m}</div>`)
            .join('');
    }
}

// Удаление
async function deleteItem(resource, id) {
    if (!confirm('Удалить?')) return;

    const config = RESOURCES[resource];
    const response = await fetch(`${API}/${config.endpoint}/${id}/`, {
        method: 'DELETE',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
    });

    if (response.ok) {
        loadList(resource);
    } else {
        // Скорее всего PROTECT сработал — есть связанные записи
        alert('Нельзя удалить: есть связанные записи.');
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Запуск
loadAll();