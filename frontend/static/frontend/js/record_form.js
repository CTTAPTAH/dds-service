const API = '/api';

// Заполняет select вариантами из API
function fillSelect(elementId, items, placeholder) {
    const select = document.getElementById(elementId);
    select.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.textContent = item.name;
        select.appendChild(option);
    });
}

// Загружаем статусы и типы при старте
async function loadInitialData() {
    const [statuses, types] = await Promise.all([
        fetch(`${API}/statuses/`).then(r => r.json()),
        fetch(`${API}/transaction-types/`).then(r => r.json()),
    ]);
    fillSelect('field-status', statuses, '— выберите —');
    fillSelect('field-type', types, '— выберите —');
}

// При выборе типа — подгружаем категории этого типа
document.getElementById('field-type').addEventListener('change', async function() {
    const typeId = this.value;
    document.getElementById('field-category').innerHTML = '<option value="">— выберите —</option>';
    document.getElementById('field-subcategory').innerHTML = '<option value="">— сначала выберите категорию —</option>';

    if (!typeId) return;

    const categories = await fetch(`${API}/categories/?transaction_type=${typeId}`).then(r => r.json());
    fillSelect('field-category', categories, '— выберите —');
});

// При выборе категории — подгружаем подкатегории
document.getElementById('field-category').addEventListener('change', async function() {
    const categoryId = this.value;
    document.getElementById('field-subcategory').innerHTML = '<option value="">— выберите —</option>';

    if (!categoryId) return;

    const subcategories = await fetch(`${API}/subcategories/?category=${categoryId}`).then(r => r.json());
    fillSelect('field-subcategory', subcategories, '— выберите —');
});

// Если редактируем — загружаем данные записи и заполняем форму
async function loadRecord(id) {
    document.getElementById('form-title').textContent = 'Редактирование записи';

    const record = await fetch(`${API}/records/${id}/`).then(r => r.json());

    document.getElementById('field-date').value = record.date;
    document.getElementById('field-amount').value = record.amount;
    document.getElementById('field-comment').value = record.comment || '';

    // Загружаем статусы и типы, потом ставим нужные значения
    const [statuses, types] = await Promise.all([
        fetch(`${API}/statuses/`).then(r => r.json()),
        fetch(`${API}/transaction-types/`).then(r => r.json()),
    ]);
    fillSelect('field-status', statuses, '— выберите —');
    fillSelect('field-type', types, '— выберите —');

    document.getElementById('field-status').value = record.status;

    // Загружаем категории для типа этой записи
    const typeId = record.category_details?.transaction_type || null;
    const categories = await fetch(`${API}/categories/?transaction_type=${record.category}`).then(r => r.json());

    // Узнаём тип через категорию
    const categoryData = await fetch(`${API}/categories/${record.category}/`).then(r => r.json());
    fillSelect('field-type', types, '— выберите —');
    document.getElementById('field-type').value = categoryData.transaction_type;

    // Загружаем категории этого типа
    const categoriesForType = await fetch(`${API}/categories/?transaction_type=${categoryData.transaction_type}`).then(r => r.json());
    fillSelect('field-category', categoriesForType, '— выберите —');
    document.getElementById('field-category').value = record.category;

    // Загружаем подкатегории этой категории
    const subcategories = await fetch(`${API}/subcategories/?category=${record.category}`).then(r => r.json());
    fillSelect('field-subcategory', subcategories, '— выберите —');
    document.getElementById('field-subcategory').value = record.subcategory;
}

// Отправка формы
document.getElementById('record-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const data = {
        date: document.getElementById('field-date').value,
        status: document.getElementById('field-status').value,
        category: document.getElementById('field-category').value,
        subcategory: document.getElementById('field-subcategory').value,
        amount: document.getElementById('field-amount').value,
        comment: document.getElementById('field-comment').value,
    };

    const url = RECORD_ID ? `${API}/records/${RECORD_ID}/` : `${API}/records/`;
    const method = RECORD_ID ? 'PUT' : 'POST';

    const response = await fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    });

    if (response.ok) {
        window.location.href = '/';
    } else {
        const errors = await response.json();
        showErrors(errors);
    }
});

// Показываем ошибки валидации с сервера
function showErrors(errors) {
    const block = document.getElementById('form-errors');
    block.classList.remove('d-none');
    block.innerHTML = Object.entries(errors)
        .map(([field, messages]) => `<div>${field}: ${messages}</div>`)
        .join('');
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Запуск
if (RECORD_ID) {
    loadRecord(RECORD_ID);
} else {
    loadInitialData();
    // Ставим сегодняшнюю дату по умолчанию
    document.getElementById('field-date').value = new Date().toISOString().split('T')[0];
}