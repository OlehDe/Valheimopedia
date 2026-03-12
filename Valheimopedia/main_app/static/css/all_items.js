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
        console.log('Завантажені дані:', allCategoriesData);
    } catch (e) {
        console.error('Помилка парсингу items-data:', e);
        mainContainer.innerHTML = '<p class="empty-message">Помилка завантаження даних</p>';
        return;
    }

    const armorSets = allCategoriesData['Комплект обладунків'] || [];

    // --- Допоміжні функції ---
    function collectAllItems(data) {
        const items = [];
        function traverse(obj) {
            if (Array.isArray(obj)) {
                obj.forEach(item => {
                    if (item && typeof item === 'object') {
                        if (item.name || item.token || item.assetId) {
                            items.push(item);
                        } else {
                            traverse(item);
                        }
                    }
                });
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

    // Отримання луків з правильного шляху: Зброя -> Далекобійна зброя -> Луки
    function getBowsFromRangedWeapons() {
        const bows = [];
        const weapons = allCategoriesData['Зброя'];
        const ranged = weapons?.['Далекобійна зброя'];
        if (ranged && Array.isArray(ranged['Луки'])) {
            ranged['Луки'].forEach(bow => {
                if (bow && bow.name) bows.push(bow);
            });
        }
        return bows;
    }

    // Отримання стріл: Зброя -> Далекобійна зброя -> Боєприпаси (Ammunition) -> Стріли (Arrows)
    function getArrowsFromAmmunition() {
        const arrows = [];
        const weapons = allCategoriesData['Зброя'];
        const ranged = weapons?.['Далекобійна зброя'];
        const ammo = ranged?.['Боєприпаси (Ammunition)'];
        if (ammo && Array.isArray(ammo['Стріли (Arrows)'])) {
            ammo['Стріли (Arrows)'].forEach(arrow => {
                if (arrow && arrow.name) arrows.push(arrow);
            });
        }
        return arrows;
    }

    // Отримання всієї далекобійної зброї (включно з луками, арбалетами тощо)
    function getAllRangedWeapons() {
        const weapons = allCategoriesData['Зброя'];
        const ranged = weapons?.['Далекобійна зброя'];
        return ranged ? collectAllItems(ranged) : [];
    }

    // --- Рендеринг ---
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
            let html = `<div class="item-image-container">`;
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
    let currentCategory = 'Всі';
    let currentItems = [];
    let searchTerm = '';
    let sortOrder = 'name-asc';

    function getItemsForCategory(categoryKey) {
        console.log('Отримання предметів для категорії:', categoryKey);

        if (categoryKey === 'Всі') {
            let all = [];
            for (const [key, data] of Object.entries(allCategoriesData)) {
                if (key !== 'Комплект обладунків') {
                    all = all.concat(collectAllItems(data));
                }
            }
            return all;
        }
        else if (categoryKey === 'Луки') {
            return getBowsFromRangedWeapons();
        }
        else if (categoryKey === 'Стріли') {
            return getArrowsFromAmmunition();
        }
        else if (categoryKey === 'Нагрудні обладунки') {
            const chestData = allCategoriesData['Обладунки']?.['Нагрудні обладунки'];
            return chestData ? collectAllItems(chestData) : [];
        }
        else if (categoryKey === 'Далекобійна зброя') {
            return getAllRangedWeapons();
        }
        else if (categoryKey === 'Зброя') {
            let allWeapons = [];
            if (allCategoriesData['Зброя']) {
                allWeapons = allWeapons.concat(collectAllItems(allCategoriesData['Зброя']));
            }
            if (allCategoriesData['Унікальні предмети']) {
                allWeapons = allWeapons.concat(collectAllItems(allCategoriesData['Унікальні предмети']));
            }
            return allWeapons;
        }
        // --- ПІДКАТЕГОРІЇ ЗБРОЇ: ОДНОРУЧНА ТА ДВОРУЧНА ---
        else if (categoryKey === 'Одноручна зброя') {
            const oneHandData = allCategoriesData['Зброя']?.['Одноручна зброя'];
            return oneHandData ? collectAllItems(oneHandData) : [];
        }
        else if (categoryKey === 'Дворучна зброя') {
            const twoHandData = allCategoriesData['Зброя']?.['Дворучна зброя'];
            return twoHandData ? collectAllItems(twoHandData) : [];
        }
        // --- ПІДКАТЕГОРІЇ ОБЛАДУНКІВ ---
        else if (categoryKey === 'Шоломи') {
            return allCategoriesData['Обладунки']?.['Шоломи'] || [];
        }
        else if (categoryKey === 'Штани') {
            return allCategoriesData['Обладунки']?.['Штани'] || [];
        }
        else if (categoryKey === 'Плащі') {
            return allCategoriesData['Обладунки']?.['Плащі'] || [];
        }
        // --- ІНШІ КАТЕГОРІЇ ---
        else {
            return collectAllItems(allCategoriesData[categoryKey]);
        }
    }

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

    function refreshDisplay() {
        console.log('Оновлення відображення для категорії:', currentCategory);
        if (currentCategory === 'Комплект обладунків') {
            renderSetCards(armorSets);
        } else {
            const filteredSorted = filterAndSortItems();
            renderItemCards(filteredSorted);
        }
    }

    function changeCategory(categoryKey) {
        console.log('Зміна категорії на:', categoryKey);
        currentCategory = categoryKey;
        if (categoryKey !== 'Комплект обладунків') {
            currentItems = getItemsForCategory(categoryKey);
        }
        refreshDisplay();
    }

    // --- Обробники подій ---

    // Обробник для основних кнопок фільтрів (включаючи кнопку "Обладунки")
    filterContainer.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON') return;

        const category = e.target.dataset.category;

        // Видаляємо активний клас з усіх кнопок
        filterButtons.forEach(btn => btn.classList.remove('active'));

        // Додаємо активний клас натиснутій кнопці
        e.target.classList.add('active');

        // Видаляємо активний клас з усіх пунктів випадаючого меню
        document.querySelectorAll('.dropdown-content a.active').forEach(a => a.classList.remove('active'));

        // Змінюємо категорію
        changeCategory(category);
    });

    // Обробник для пунктів випадаючого меню
    const dropdownLinks = document.querySelectorAll('.dropdown-content a');
    dropdownLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const category = link.dataset.category;

            // Видаляємо активний клас з усіх основних кнопок
            filterButtons.forEach(btn => btn.classList.remove('active'));

            // Видаляємо активний клас з усіх пунктів випадаючого меню
            dropdownLinks.forEach(l => l.classList.remove('active'));

            // Додаємо активний клас натиснутому пункту
            link.classList.add('active');

            // Змінюємо категорію
            changeCategory(category);
        });
    });

    // Пошук
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchTerm = e.target.value;
            refreshDisplay();
        });
    }

    // Сортування
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            sortOrder = e.target.value;
            refreshDisplay();
        });
    }

    // Ініціалізація
    changeCategory('Всі');
});