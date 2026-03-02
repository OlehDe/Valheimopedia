document.addEventListener('DOMContentLoaded', () => {
    const mainContainer = document.getElementById('items-grid');
    const filterContainer = document.getElementById('category-filters');
    const filterButtons = filterContainer.querySelectorAll('button');
    const itemsDataElement = document.getElementById('items-data');
    const searchInput = document.getElementById('search-input');
    const sortSelect = document.getElementById('sort-select');

    if (!mainContainer || !filterContainer || !itemsDataElement) {
        console.error('Потрібні елементи DOM не знайдено');
        return;
    }

    let allCategoriesData;
    try {
        allCategoriesData = JSON.parse(itemsDataElement.textContent);
        if (typeof allCategoriesData !== 'object' || Array.isArray(allCategoriesData) || allCategoriesData === null) {
            throw new Error('Дані мають бути об\'єктом категорій');
        }
    } catch (e) {
        console.error('Помилка парсингу items-data:', e);
        mainContainer.innerHTML = '<p class="empty-message">Помилка завантаження даних</p>';
        return;
    }

    // Зберігаємо окремо комплекти обладунків
    const armorSets = allCategoriesData['Комплект обладунків'] || [];

    // --- Допоміжні функції ---
    function collectAllItems(data) {
        const items = [];
        function traverse(obj) {
            if (Array.isArray(obj)) {
                obj.forEach(traverse);
            } else if (obj && typeof obj === 'object') {
                if ((obj.token || obj.assetId) && obj.name) {
                    items.push(obj);
                } else {
                    Object.values(obj).forEach(traverse);
                }
            }
        }
        traverse(data);
        return items;
    }

    // Функція рендерингу предметів (картки)
    function renderItemCards(items) {
        mainContainer.innerHTML = '';
        mainContainer.className = 'items-grid';

        if (!items.length) {
            mainContainer.innerHTML = '<p class="empty-message">Предмети відсутні</p>';
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

            let html = `
                <div class="item-image-container">
            `;

            if (imageUrl) {
                html += `<img src="${imageUrl}" alt="${name}" class="item-image" loading="lazy">`;
            } else {
                html += `<div class="item-image-placeholder">Немає зображення</div>`;
            }

            html += `</div><div class="item-info"><h3>${name}</h3>`;

            if (englishName && englishName.trim() !== name) {
                html += `<p><strong>Англ.:</strong> ${englishName.trim()}</p>`;
            }

            html += `<div class="item-type-badge">${type}</div></div>`;
            card.innerHTML = html;
            mainContainer.appendChild(card);
        });
    }

    // Рендеринг комплектів (без змін)
    function renderSetCards(sets) {
        mainContainer.innerHTML = '';
        mainContainer.className = '';

        if (!sets.length) {
            mainContainer.innerHTML = '<p class="empty-message">Комплекти відсутні</p>';
            return;
        }

        const groups = {};
        sets.forEach(set => {
            const cat = set.setCategory || 'Інше';
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push(set);
        });

        for (const [catName, catSets] of Object.entries(groups)) {
            const groupWrapper = document.createElement('div');
            groupWrapper.className = 'set-category-group';

            const title = document.createElement('h2');
            title.className = 'set-category-title';
            title.textContent = catName;
            groupWrapper.appendChild(title);

            const groupGrid = document.createElement('div');
            groupGrid.className = 'items-grid';

            catSets.forEach(set => {
                const slug = set.setSlug;
                if (!slug) return;
                const card = document.createElement('a');
                card.href = `/set/${slug}/`;
                card.className = 'item-card item-card-link';

                const setName = set.setName || 'Без назви';
                const imageUrl = set.set_image_url || '';

                let html = `<h3>${setName}</h3><div class="set-image-container">`;
                if (imageUrl) {
                    html += `<img src="${imageUrl}" alt="${setName}" class="set-image" loading="lazy">`;
                } else {
                    html += `<div class="item-image-placeholder">Немає зображення комплекту</div>`;
                }
                html += '</div>';
                card.innerHTML = html;
                groupGrid.appendChild(card);
            });

            groupWrapper.appendChild(groupGrid);
            mainContainer.appendChild(groupWrapper);
        }
    }

    // --- Логіка фільтрації та сортування ---
    let currentCategory = 'Всі';          // активна категорія
    let currentItems = [];                // "сирі" предмети для поточної категорії (без фільтрів)
    let searchTerm = '';
    let sortOrder = 'name-asc';

    // Отримати "сирі" предмети для категорії (крім комплектів)
    function getRawItemsForCategory(categoryKey) {
        if (categoryKey === 'Всі') {
            let all = [];
            for (const [key, data] of Object.entries(allCategoriesData)) {
                if (key !== 'Комплект обладунків') {
                    all = all.concat(collectAllItems(data));
                }
            }
            return all;
        } else if (categoryKey === 'Нагрудні обладунки') {
            const chestData = allCategoriesData['Обладунки']?.['Нагрудні обладунки'];
            return collectAllItems(chestData);
        } else {
            return collectAllItems(allCategoriesData[categoryKey]);
        }
    }

    // Застосувати пошук і сортування до поточного набору
// Застосувати пошук і сортування до поточного набору
function filterAndSortItems() {
    if (!currentItems) return [];

    let filtered = currentItems.filter(item => {
        const name = (item.name || '').toLowerCase();
        const engName = (item.englishName || '').toLowerCase();
        const search = searchTerm.toLowerCase();
        return name.includes(search) || engName.includes(search);
    });

    if (sortOrder === 'name-asc') {
        filtered.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'uk'));
    } else if (sortOrder === 'name-desc') {
        filtered.sort((a, b) => (b.name || '').localeCompare(a.name || '', 'uk'));
    }

    return filtered;
}

    // Оновити відображення з поточними фільтрами
    function refreshDisplay() {
        if (currentCategory === 'Комплект обладунків') {
            renderSetCards(armorSets);
        } else {
            const filteredSorted = filterAndSortItems();
            renderItemCards(filteredSorted);
        }
    }

    // Зміна категорії
    function changeCategory(categoryKey) {
        currentCategory = categoryKey;
        if (categoryKey !== 'Комплект обладунків') {
            currentItems = getRawItemsForCategory(categoryKey);
        }
        refreshDisplay();
    }

    // --- Обробники подій ---
    filterContainer.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON') return;
        filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        changeCategory(e.target.dataset.category);
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
    changeCategory('Всі');
});