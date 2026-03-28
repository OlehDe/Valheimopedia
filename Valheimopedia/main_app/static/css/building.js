document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.getElementById('items-grid');
    const filterContainer = document.getElementById('category-filters');
    const itemsDataElement = document.getElementById('building-data');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');

    if (!mainContainer || !filterContainer || !itemsDataElement) {
        console.error('Потрібні елементи DOM не знайдено');
        return;
    }

    let buildingItems;
    try {
        buildingItems = JSON.parse(itemsDataElement.textContent);
        if (!Array.isArray(buildingItems)) {
            throw new Error('Дані мають бути масивом');
        }
        console.log('Завантажені дані:', buildingItems);
    } catch (e) {
        console.error('Помилка парсингу building-data:', e);
        mainContainer.innerHTML = '<p class="empty-message">Помилка завантаження даних</p>';
        return;
    }

    // Збір унікальних типів для фільтрів
    const typesSet = new Set();
    buildingItems.forEach(item => {
        if (item.type) typesSet.add(item.type);
    });
    const uniqueTypes = Array.from(typesSet).sort();

    // Додаємо кнопки фільтрів
    uniqueTypes.forEach(type => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = type;
        btn.dataset.category = type;
        filterContainer.appendChild(btn);
    });

    // Стан
    let currentCategory = 'Всі';
    let searchTerm = '';
    let sortOrder = 'name-asc';

    // Функції фільтрації, сортування, рендеру (аналогічно all_items.js)
    function filterItems() {
        return buildingItems.filter(item => {
            if (currentCategory !== 'Всі' && item.type !== currentCategory) return false;
            const name = (item.name || '').toLowerCase();
            const engName = (item.englishName || '').toLowerCase();
            const search = searchTerm.toLowerCase();
            return name.includes(search) || engName.includes(search);
        });
    }

    function sortItems(items) {
        const sorted = [...items];
        if (sortOrder === 'name-asc') {
            sorted.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'uk'));
        } else if (sortOrder === 'name-desc') {
            sorted.sort((a, b) => (b.name || '').localeCompare(a.name || '', 'uk'));
        }
        return sorted;
    }

    function renderItems(items) {
        mainContainer.innerHTML = '';
        mainContainer.className = 'items-grid';
        if (!items.length) {
            mainContainer.innerHTML = '<p class="empty-message">Нічого не знайдено 😢</p>';
            return;
        }

        items.forEach(item => {
            const card = document.createElement('a');
            const id = item.token || item.assetId;
            if (!id) return;
            card.href = `/item/${id}/`;
            card.className = 'item-card item-card-link';
            const name = item.name || 'Без назви';
            const englishName = item.englishName || '';
            const type = item.type || '—';
            const imageUrl = item.image_url || '';
            let html = `<div class="item-image-container">`;
            if (imageUrl) {
                html += `<img src="${imageUrl}" alt="${name}" class="item-image" loading="lazy">`;
            } else {
                html += `<div class="item-image-placeholder">🏗️</div>`;
            }
            html += `</div><div class="item-info"><h3>${escapeHtml(name)}</h3>`;
            if (englishName && englishName.trim() !== name) {
                html += `<p><strong>Англ.:</strong> ${escapeHtml(englishName.trim())}</p>`;
            }
            html += `<div class="item-type-badge">${escapeHtml(type)}</div></div>`;
            card.innerHTML = html;
            mainContainer.appendChild(card);
        });
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function refreshDisplay() {
        const filtered = filterItems();
        const sorted = sortItems(filtered);
        renderItems(sorted);
    }

    // Обробники подій
    const allFilterButtons = filterContainer.querySelectorAll('button');
    allFilterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            allFilterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.dataset.category;
            refreshDisplay();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchTerm = e.target.value;
            refreshDisplay();
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            sortOrder = e.target.value;
            refreshDisplay();
        });
    }

    // Ініціалізація
    const firstFilter = document.querySelector('.category-filters button');
    if (firstFilter) {
        firstFilter.classList.add('active');
        currentCategory = firstFilter.dataset.category;
    }
    refreshDisplay();
});