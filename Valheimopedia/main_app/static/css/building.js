document.addEventListener('DOMContentLoaded', () => {
    // Отримуємо елементи
    const mainContainer = document.getElementById('items-grid');
    const filterContainer = document.getElementById('category-filters');
    const itemsDataElement = document.getElementById('building-data');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');

    // Перевіряємо наявність
    if (!mainContainer || !filterContainer || !itemsDataElement) {
        console.error('Не знайдено необхідні елементи');
        return;
    }

    // Завантажуємо дані
    let buildingItems;
    try {
        buildingItems = JSON.parse(itemsDataElement.textContent);
        if (!Array.isArray(buildingItems)) throw new Error('Дані не масив');
        console.log('Завантажено предметів:', buildingItems.length);
    } catch (e) {
        mainContainer.innerHTML = '<p class="empty-message">Помилка завантаження даних</p>';
        return;
    }

    // Збираємо унікальні типи для фільтрів (крім "Всі")
    const typesSet = new Set();
    buildingItems.forEach(item => {
        if (item.type) typesSet.add(item.type);
    });
    const uniqueTypes = Array.from(typesSet).sort();

    // Додаємо кнопки типів у контейнер фільтрів
    uniqueTypes.forEach(type => {
        const btn = document.createElement('button');
        btn.textContent = type;
        btn.dataset.category = type;
        filterContainer.appendChild(btn);
    });

    // Стан
    let currentCategory = 'Всі';
    let searchTerm = '';
    let sortOrder = 'name-asc';

    // Екранування HTML
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    // Фільтрація та сортування
    function filterAndSort() {
        let filtered = buildingItems.filter(item => {
            if (currentCategory !== 'Всі' && item.type !== currentCategory) return false;
            const name = (item.name || '').toLowerCase();
            const engName = (item.englishName || '').toLowerCase();
            const search = searchTerm.toLowerCase();
            return name.includes(search) || engName.includes(search);
        });
        if (sortOrder === 'name-asc') {
            filtered.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'uk'));
        } else {
            filtered.sort((a, b) => (b.name || '').localeCompare(a.name || '', 'uk'));
        }
        return filtered;
    }

    // Рендеринг
    function render(items) {
        mainContainer.innerHTML = '';
        mainContainer.className = 'items-grid';
        if (!items.length) {
            mainContainer.innerHTML = '<p class="empty-message">Нічого не знайдено 😢</p>';
            return;
        }
        items.forEach(item => {
            const card = document.createElement('a');
            card.href = `/building/${item.token}/`;
            card.className = 'item-card item-card-link';
            card.innerHTML = `
                <div class="item-image-container">
                    ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" class="item-image" loading="lazy">` : '<div class="item-image-placeholder">🏗️</div>'}
                </div>
                <div class="item-info">
                    <h3>${escapeHtml(item.name)}</h3>
                    ${item.englishName && item.englishName !== item.name ? `<p><strong>Англ.:</strong> ${escapeHtml(item.englishName)}</p>` : ''}
                    <div class="item-type-badge">${escapeHtml(item.type)}</div>
                </div>
            `;
            mainContainer.appendChild(card);
        });
    }

    function refresh() {
        render(filterAndSort());
    }

    // --- Обробники подій ---
    const allFilterButtons = filterContainer.querySelectorAll('button');
    allFilterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            allFilterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            refresh();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', e => {
            searchTerm = e.target.value;
            refresh();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', e => {
            sortOrder = e.target.value;
            refresh();
        });
    }

    // Початковий рендеринг
    refresh();
});

document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.getElementById('items-grid');
    const itemsDataElement = document.getElementById('building-data');

    if (!mainContainer || !itemsDataElement) {
        console.error('Елементи не знайдено');
        return;
    }

    let buildingItems;
    try {
        buildingItems = JSON.parse(itemsDataElement.textContent);
        if (!Array.isArray(buildingItems)) throw new Error('Дані не масив');
        console.log('Завантажено предметів:', buildingItems.length);
    } catch (e) {
        mainContainer.innerHTML = '<p class="empty-message">Помилка завантаження даних</p>';
        return;
    }

    // Спрощене відображення без фільтрів
    function render() {
        mainContainer.innerHTML = '';
        buildingItems.forEach(item => {
            const card = document.createElement('a');
            card.href = `/building/${item.token}/`;
            card.className = 'item-card item-card-link';
            card.innerHTML = `
                <div class="item-image-container">
                    ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" class="item-image">` : '<div class="item-image-placeholder">🏗️</div>'}
                </div>
                <div class="item-info">
                    <h3>${item.name}</h3>
                    <div class="item-type-badge">${item.type}</div>
                </div>
            `;
            mainContainer.appendChild(card);
        });
    }

    render();
});