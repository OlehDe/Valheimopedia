document.addEventListener('DOMContentLoaded', () => {

    let allCategoriesData;

    const mainContainer = document.getElementById('items-grid');
    const filterContainer = document.getElementById('category-filters');
    const buttons = filterContainer.querySelectorAll('button');

    // Отримуємо дані з Django
    try {
      allCategoriesData = JSON.parse(document.getElementById('items-data').textContent);

      if (typeof allCategoriesData !== 'object' || Array.isArray(allCategoriesData) || allCategoriesData === null) {
           throw new Error("Очікувана структура даних - об'єкт (словник) категорій.");
      }

    } catch (e) {
      console.error("Не вдалося завантажити дані предметів:", e);
      if(mainContainer) {
          mainContainer.innerHTML = `<p class="empty-message">Помилка завантаження даних.</p>`;
      }
      return;
    }

    // Рекурсивна функція для отримання всіх предметів
    function getAllItemsFrom(data) {
        if (Array.isArray(data)) {
            return data.flatMap(item => getAllItemsFrom(item));
        }
        if (typeof data === 'object' && data !== null) {
            if (data.assetId && data.name) {
                return [data];
            }
            return Object.values(data).flatMap(value => getAllItemsFrom(value));
        }
        return [];
    }

    // Функція для створення картки предмета з зображенням
    function renderItemCards(itemsArray) {
        mainContainer.innerHTML = '';
        mainContainer.className = 'items-grid';

        if (!itemsArray || itemsArray.length === 0) {
            mainContainer.innerHTML = `<p class="empty-message">Предмети відсутні.</p>`;
            return;
        }

        itemsArray.forEach(item => {
          if (item && item.assetId) {
            const card = document.createElement('a');
            card.href = `/item/${item.assetId}/`;
            card.className = 'item-card item-card-link';

            const englishName = item.englishName || item[' englishName'];
            const internalName = item.name || 'N/A';
            const itemType = item.type || 'N/A';
            const imageUrl = item.image_url;

            let cardHTML = `
              <div class="item-image-container">
            `;

            if (imageUrl) {
              cardHTML += `
                <img src="${imageUrl}" alt="${internalName}" class="item-image" loading="lazy">
              `;
            } else {
              cardHTML += `
                <div class="item-image-placeholder">
                  Немає зображення
                </div>
              `;
            }

            cardHTML += `
              </div>
              <div class="item-info">
                <h3>${internalName}</h3>
            `;

            if (englishName && englishName.trim() !== internalName) {
              cardHTML += `<p><strong>Англ. назва:</strong> ${englishName.trim()}</p>`;
            }

            cardHTML += `
                <div class="item-type-badge">${itemType}</div>
              </div>
            `;

            card.innerHTML = cardHTML;
            mainContainer.appendChild(card);
          }
        });
    }

    // Функція для створення карток комплексів з групами
    function renderSetCards(setsArray) {
        mainContainer.innerHTML = '';
        mainContainer.className = '';

        if (!setsArray || setsArray.length === 0) {
            mainContainer.innerHTML = `<p class="empty-message">Комплекти відсутні.</p>`;
            return;
        }

        const groups = {};
        setsArray.forEach(set => {
            const category = set.setCategory || 'Інше';
            if (!groups[category]) {
                groups[category] = [];
            }
            groups[category].push(set);
        });

        for (const categoryName in groups) {
            const groupWrapper = document.createElement('div');
            groupWrapper.className = 'set-category-group';

            const title = document.createElement('h2');
            title.className = 'set-category-title';
            title.textContent = categoryName;
            groupWrapper.appendChild(title);

            const groupGrid = document.createElement('div');
            groupGrid.className = 'items-grid';

            groups[categoryName].forEach(set => {
                if (set && set.setSlug) {
                    const card = document.createElement('a');
                    card.href = `/set/${set.setSlug}/`;
                    card.className = 'item-card item-card-link';

                    let cardHTML = `<h3>${set.setName || 'N/A'}</h3>`;

                    if (set.set_image_url) {
                        cardHTML += `
                            <div class="set-image-container">
                                <img src="${set.set_image_url}" alt="${set.setName}" class="set-image" loading="lazy">
                            </div>
                        `;
                    } else {
                        cardHTML += `
                            <div class="set-image-container">
                                <div class="item-image-placeholder">
                                    Немає зображення комплекту
                                </div>
                            </div>
                        `;
                    }

                    card.innerHTML = cardHTML;
                    groupGrid.appendChild(card);
                }
            });

            groupWrapper.appendChild(groupGrid);
            mainContainer.appendChild(groupWrapper);
        }
    }

    // Функція-розподільник для рендерингу контенту
    function renderContent(categoryKey) {
      const categoryData = allCategoriesData[categoryKey];

      if (categoryKey === 'Комплект обладунків') {
          renderSetCards(categoryData || []);
      } else {
          mainContainer.className = 'items-grid';
          let itemsToShow = [];

          if (categoryKey === 'Всі') {
              for (const key in allCategoriesData) {
                  if (key !== 'Комплект обладунків') {
                      itemsToShow = itemsToShow.concat(getAllItemsFrom(allCategoriesData[key]));
                  }
              }
          } else if (categoryKey === 'Нагрудні обладунки') {
              const chestData = allCategoriesData['Обладунки'] ? allCategoriesData['Обладунки']['Нагрудні обладунки'] : undefined;
              itemsToShow = getAllItemsFrom(chestData);
          } else {
              itemsToShow = getAllItemsFrom(categoryData);
          }

          renderItemCards(itemsToShow);
      }
    }

    // Обробник кліків на кнопки фільтрів
    filterContainer.addEventListener('click', (event) => {
      if (event.target.tagName === 'BUTTON') {
        buttons.forEach(btn => btn.classList.remove('active'));
        const clickedButton = event.target;
        clickedButton.classList.add('active');
        const category = clickedButton.dataset.category;
        renderContent(category);
      }
    });

    // Завантажуємо всі предмети при першому відкритті сторінки
    renderContent('Всі');
    // Додайте цей код до вашого існуючого JavaScript

    document.addEventListener('DOMContentLoaded', function() {
      // Обробка кліків по підкатегоріях зброї
      const weaponSubButtons = document.querySelectorAll('.weapon-subcategories button');
      weaponSubButtons.forEach(button => {
        button.addEventListener('click', function() {
          const category = this.getAttribute('data-category');
          filterItems(category);

          // Оновлення активного стану
          document.querySelectorAll('.category-filters button').forEach(btn => {
            btn.classList.remove('active');
          });
          this.classList.add('active');
        });
      });

      // Функція фільтрації предметів (ваша існуюча функція)
      function filterItems(category) {
        // Ваша існуюча логіка фільтрації
        const itemsGrid = document.getElementById('items-grid');
        // ... ваш код фільтрації
      }
    });
    const itemsData = JSON.parse(document.getElementById("items-data").textContent);
    const itemsGrid = document.getElementById("items-grid");
    const filterButtons = document.querySelectorAll("#category-filters button");
    const typeSelect = document.getElementById("type-select");

     function displayItems(items) {
       itemsGrid.innerHTML = "";

        if (items.length === 0) {
          itemsGrid.innerHTML = `<p class="empty-message">Немає предметів у цій категорії.</p>`;
          return;
        }

        items.forEach(item => {
          const card = document.createElement("div");
          card.className = "item-card";
          card.innerHTML = `
            <img src="${item.image_url}" alt="${item.name}">
            <h3>${item.name}</h3>
            <p>${item.category}</p>
            <p>${item.type}</p>
          `;
          itemsGrid.appendChild(card);
        });
      }

      // поточні фільтри
      let selectedCategory = "Всі";
      let selectedType = "Всі";

      function applyFilters() {
        let filtered = [...itemsData];

        if (selectedCategory !== "Всі") {
          filtered = filtered.filter(item => item.category === selectedCategory);
        }

        if (selectedType !== "Всі") {
          filtered = filtered.filter(item => item.type === selectedType);
        }

        displayItems(filtered);
      }

      // натискання кнопок категорій
      filterButtons.forEach(button => {
        button.addEventListener("click", () => {
          filterButtons.forEach(btn => btn.classList.remove("active"));
          button.classList.add("active");
          selectedCategory = button.dataset.category;
          applyFilters();
        });
      });

      // вибір типу зі списку
      typeSelect.addEventListener("change", () => {
        selectedType = typeSelect.value;
        applyFilters();
      });

      displayItems(itemsData);


  });