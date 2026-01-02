class MenuManager {
    constructor() {
        this.menuData = null;
        this.categories = [];
        this.currentCategory = null;
        this.order = {}; // { itemName: quantity }
        this.searchQuery = '';
        this.allItems = []; // Store all items across categories
        this.currentRestaurant = 'kfc'; // 'kfc' or 'tacobell'
        this.restaurantData = {
            kfc: {
                name: 'KFC',
                icon: '🍗',
                dataPath: 'KFC/data/menu.csv',
                locationsPath: 'KFC/data/locations.csv',
                categories: [
                    'The Latest',
                    'Combos',
                    'Family Meals',
                    'Fried Chicken',
                    'Tenders',
                    'Nuggets',
                    'Drinks',
                    'Sandwiches',
                    'Pot Pies & Bowls',
                    'Side, Sweets, Sauces'
                ]
            },
            tacobell: {
                name: 'Taco Bell',
                icon: '🌮',
                dataPath: 'data/menu.csv',
                locationsPath: 'data/locations.csv',
                categories: [
                    'Tacos',
                    'Burritos',
                    'Quesadillas',
                    'Specialties',
                    'Nachos',
                    'Bowls',
                    'Sides & Sweets',
                    'Drinks',
                    'Breakfast',
                    'Combos & Boxes',
                    'Cravings Value Menu',
                    'Cantina Chicken Menu',
                    'Veggie Cravings',
                    'Best Sellers',
                    'New',
                    'Online Exclusives',
                    'Member Exclusives',
                    'Groups',
                    'Live Más Café and Drinks'
                ]
            }
        };
    }

    async initialize() {
        await this.loadMenuData();
        await this.loadCategories();
        this.buildAllItemsList();
        this.renderCategories();
        this.setupSearchBar();
        
        // Load first category by default
        if (this.categories.length > 0) {
            this.selectCategory(this.categories[0]);
        }
    }

    async loadMenuData() {
        const restaurant = this.restaurantData[this.currentRestaurant];
        console.log('Loading menu data from:', restaurant.dataPath);
        this.menuData = await CSVParser.loadMenu(restaurant.dataPath);
        console.log('Menu data loaded:', this.menuData ? `${this.menuData.headers.length} headers, ${this.menuData.data.length} stores` : 'null');
    }

    async loadCategories() {
        try {
            const restaurant = this.restaurantData[this.currentRestaurant];
            console.log('Loading categories for:', this.currentRestaurant, restaurant.categories);
            
            for (const category of restaurant.categories) {
                const items = this.getItemsForCategoryFallback(category);
                console.log(`Category ${category}: ${items.length} items`);
                if (items.length > 0) {
                    this.categories.push({ name: category, items });
                }
            }
            console.log('Total categories loaded:', this.categories.length);
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    }

    getItemsForCategoryFallback(category) {
        console.log(`Getting items for category: ${category} (restaurant: ${this.currentRestaurant})`);
        
        // For KFC, use hardcoded categories as before
        if (this.currentRestaurant === 'kfc') {
            const categoryMap = {
                'The Latest': [
                    'Gravy Fest Flight', 'Festive Pot Pie', 'Festive Pot Pie Meal', 'Gravy Fest Tenders Box',
                    'Signature Brown Gravy', 'White Peppercorn Gravy', 'Southwest Cheddar Gravy',
                    'Extra Crispy Festive Feast', 'Sidesgiving'
                ],
                'Combos': [
                    'Festive Pot Pie Meal', 'Gravy Fest Tenders Box', 'Original Honey BBQ 2 pc. Chicken Combo',
                    'Original Honey BBQ 3 pc. Chicken Combo', 'Original Honey BBQ 3 pc. Tenders Combo',
                    'Original Honey BBQ 4 pc. Tenders Combo', 'Original Honey BBQ Chicken Sandwich Combo',
                    'Wings & Wedges Combo', '3 pc. Mike\'s Hot Honey Chicken Combo', '4 pc. Mike\'s Hot Honey Tenders Combo',
                    'Mike\'s Hot Honey Chicken Sandwich Combo', 'Meal for Two: 2 Sandwiches + 4 pc. Tenders Combo',
                    'Meal for Two: 2 Sandwiches + 10 pc. Nuggets Combo', 'Meal for Two: 5 pc. Chicken Combo',
                    'Chicken Combo', '3 pc. Chicken Big Box Meal', 'Tenders Combos', '5 pc. Tenders Big Box Meal',
                    'Classic Chicken Sandwich Combo', 'Spicy Chicken Sandwich Combo',
                    'Classic Chicken Sandwich + Nuggets Big Box Meal', 'Spicy Chicken Sandwich + Nuggets Big Box Meal',
                    'Famous Bowl Combo', 'Pot Pie Combo'
                ],
                'Family Meals': [
                    'Extra Crispy Festive Feast', 'Wings and Wedges Fan Favorites Box', 'Fan Favorites Box',
                    'Double Mash Meal', 'Mike\'s Hot Honey Fan Favorite\'s Box',
                    'Chicken & Tenders Feast: 6 pc. Chicken + 6 pc. Tenders', 'Taste of KFC 4 pc. Deal',
                    'Taste of KFC 6 pc. Deal', '6 pc. Tenders + 12 pc. Nuggets Family Meal',
                    '6 pc. Chicken + 12 pc. Nuggets Family Meal', 'Chicken Meal', 'Tenders Meals',
                    'Chicken Only', 'Tenders Only', '5 pc. Nugget Kids Meal', '2 pc. Tenders Kids Meal'
                ],
                'Fried Chicken': [
                    'Original Honey BBQ 2 pc. Chicken Combo', 'Original Honey BBQ 3 pc. Chicken Combo',
                    'Hot & Spicy Wings', '3 pc. Mike\'s Hot Honey Chicken Combo', 'Taste of KFC Deal',
                    'Meal for Two: 5 pc. Chicken Combo', 'Chicken Combo', '3 pc. Chicken Big Box Meal',
                    'Double Mash Meal', 'Chicken Meal', 'Chicken Only', 'Chicken Breast',
                    'Chicken Drum', 'Chicken Thigh', 'Chicken Wing'
                ],
                'Tenders': [
                    'Gravy Fest Tenders Box', 'Original Honey BBQ 3 pc. Tenders Combo',
                    'Original Honey BBQ 4 pc. Tenders Combo', '4 pc. Mike\'s Hot Honey Tenders Combo',
                    'Tenders Combos', '5 pc. Tenders Big Box Meal', 'Tenders Meals',
                    'Tenders Only', '2 pc. Tenders Kids Meal', 'Chicken Tender'
                ],
                'Nuggets': [
                    'Nuggets Combo', 'Nuggets Only', '5 pc. Nugget Kids Meal'
                ],
                'Drinks': [
                    'Mountain Dew Sweet Lightning Peaches & Cream Soda', 'Pepsi with Sweet, Vanilla Cream',
                    'Lemonade with Sweet, Vanilla Cream', '1/2 Gallon Drink', 'Pepsi',
                    'Pepsi Zero Sugar', 'Starry', 'Mountain Dew', 'Mountain Dew Sweet Lightning',
                    'Sweet Tea', "The Colonel's Lemonade"
                ],
                'Sandwiches': [
                    'Original Honey BBQ Chicken Sandwich Combo', 'Original Honey BBQ Chicken Sandwich',
                    'Mike\'s Hot Honey Chicken Sandwich Combo', 'Meal for Two: 2 Sandwiches + 4 pc. Tenders Combo',
                    'Meal for Two: 2 Sandwiches + 10 pc. Nuggets Combo', 'Mike\'s Hot Honey Chicken Sandwich',
                    'Classic Chicken Sandwich Combo', 'Spicy Chicken Sandwich Combo',
                    'Classic Chicken Sandwich + Nuggets Big Box Meal', 'Spicy Chicken Sandwich + Nuggets Big Box Meal',
                    'Chicken Little Combo', 'Chicken Sandwich', 'Spicy Chicken Sandwich', 'Chicken Little'
                ],
                'Pot Pies & Bowls': [
                    'Festive Pot Pie Meal', 'Festive Pot Pie', 'Famous Bowl Combo', 'Pot Pie Combo', 'Famous Bowl'
                ],
                'Side, Sweets, Sauces': [
                    'Signature Brown Gravy', 'White Peppercorn Gravy', 'Southwest Cheddar Gravy', 'Sidesgiving',
                    'Gravy Fest Flight', 'Biscuit', 'Original Honey BBQ Drum', 'Potato Wedges',
                    'Mike\'s Hot Honey Biscuits', 'Pie Poppers', 'Secret Recipe Fries', 'Mashed Potatoes and Gravy',
                    'Mac & Cheese', 'Biscuit', 'Cole Slaw', 'Sweet Corn', 'Mashed Potatoes',
                    'Chicken Little', 'Chicken Breast', 'Chicken Drum', 'Chicken Thigh',
                    'Chicken Wing', 'Chicken Tender', 'Chocolate Chip Cake'
                ]
            };
            
            const items = [];
            const categoryItems = categoryMap[category] || [];
            
            categoryItems.forEach(itemName => {
                if (this.menuData.headers.includes(itemName)) {
                    const imagePath = `KFC/images/${category}/${encodeURIComponent(itemName)}.jpg`;
                    items.push({
                        name: itemName,
                        category: category,
                        imagePath: imagePath
                    });
                }
            });
            
            return items;
        }
        
        // For Taco Bell, use the complete hardcoded mapping from Taco-Bell-Crawler
        if (!this.menuData || !this.menuData.headers) {
            console.log('No menu data available for Taco Bell');
            return [];
        }
        
        const categoryMap = {
            'Tacos': [
                'Soft Taco', 'Crunchy Taco', 'Soft Taco Supreme®', 'Crunchy Taco Supreme®',
                'Nacho Cheese Doritos® Locos Tacos', 'Nacho Cheese Doritos® Locos Tacos Supreme®',
                'Chalupa Supreme', 'Chalupa Supreme®', 'Black Bean Chalupa Supreme', 'Black Bean Chalupa Supreme®', 
                'Cheesy Gordita Crunch', 'Doritos® Cheesy Gordita Crunch - Nacho Cheese', 'Double Stacked Taco',
                'Spicy Potato Soft Taco', 'Cantina Chicken Soft Taco', 'Cantina Chicken Crispy Taco',
                'Avocado Ranch Crispy Chicken Soft Taco', 'Creamy Chipotle Crispy Chicken Soft Taco',
                'Frank\'s RedHot® Diablo Crispy Chicken Soft Taco'
            ],
            'Burritos': [
                'Bean Burrito', 'Burrito Supreme®', 'Beefy 5-Layer Burrito', 'Cheesy Bean and Rice Burrito',
                'Cheesy Double Beef Burrito', 'Grilled Cheese Burrito', 'Quesarito', 'Chicken Enchilada Burrito',
                'Black Bean Grilled Cheese Burrito - Black Beans', 'Cantina Chicken Burrito',
                'Avocado Ranch Crispy Chicken Burrito', 'Creamy Chipotle Crispy Chicken Burrito',
                'Frank\'s RedHot® Diablo Crispy Chicken Burrito', 'Slow Roasted Chicken Cheesy Dipping Burritos',
                'Steak Cheesy Dipping Burritos'
            ],
            'Quesadillas': [
                'Cheese Quesadilla', 'Chicken Quesadilla', 'Steak Quesadilla',
                'Cantina Chicken Quesadilla', 'Steak & Poblano Rolled Quesadilla'
            ],
            'Specialties': [
                'Crunchwrap Supreme®', 'Black Bean Crunchwrap Supreme®', 'Mexican Pizza',
                'Veggie Mexican Pizza'
            ],
            'Nachos': [
                'Nachos BellGrande®', 'Chips and Nacho Cheese Sauce', 'Chips and Guacamole',
                'Loaded Beef Nachos', 'Nacho Fries', 'Large Nacho Fries', 'Steak Garlic Nacho Fries',
                'Frank\'s RedHot® Diablo Chicken Nacho Fries'
            ],
            'Bowls': [
                'Cantina Chicken Bowl', 'Veggie Bowl'
            ],
            'Sides & Sweets': [
                'Cheesy Fiesta Potatoes', 'Cheesy Roll Up', 'Black Beans', 'Black Beans and Rice',
                'Pintos N Cheese', 'Cinnamon Twists', 'Cinnabon Delights® 2 Pack',
                'Cinnabon Delights® 12 Pack', 'Hash Brown'
            ],
            'Drinks': [
                'Pepsi®', 'Diet Pepsi®', 'Pepsi® Zero Sugar', 'MTN DEW®', 'MTN DEW® Baja Blast®',
                'MTN DEW® Baja Blast™ Zero Sugar', 'MTN DEW® Zero', 'Dr Pepper®', 'Diet Dr Pepper®',
                'Starry®', 'Mug® Root Beer', 'Cherry Pepsi®', 'Brisk® Mango Fiesta', 'Lipton® Sweet Tea',
                'Lipton® Unsweetened Iced Tea', 'Tropicana® Original Lemonade', 'Tropicana® Orange Juice',
                'Aquafina® Bottled Water', 'Milk', 'MTN DEW® Baja Blast® Freeze', 'Wild Strawberry Freeze',
                'Blue Raspberry Freeze', 'Strawberry Vanilla Cream Soda Freeze', 'Vanilla Cream Soda Freeze',
                'Confetti Cookie Freeze', 'Mountain Dew Baja Midnight™', 'Dragonfruit Agua Refresca',
                'Dragonfruit Berry Agua Refresca', 'Mango Peach Agua Refresca', 'Strawberry Passionfruit Agua Refresca',
                'Premium Hot Coffee', 'Regular Iced Coffee', 'Hot Cinnabon Delights® Coffee',
                'Iced Cinnabon Delights® Coffee', 'Pineapple Lime Rockstar® Energy Refresca',
                'Tropical Punch Rockstar® Energy Refresca', 'G2 Gatorade® Fruit Punch'
            ],
            'Breakfast': [
                'Breakfast Crunchwrap Bacon', 'Breakfast Crunchwrap Sausage', 'Breakfast California Crunchwrap',
                'Breakfast Quesadilla Bacon', 'Breakfast Quesadilla Sausage', 'Breakfast Quesadilla Steak',
                'Cheesy Toasted Breakfast Burrito Bacon', 'Cheesy Toasted Breakfast Burrito Sausage',
                'Cheesy Toasted Breakfast Burrito Potato', 'Grande Toasted Breakfast Burrito Bacon',
                'Grande Toasted Breakfast Burrito Sausage', 'Grande Toasted Breakfast Burrito Steak'
            ],
            'Combos & Boxes': [
                '3 Crunchy Tacos Combo', '3 Crunchy Tacos Supreme Combo', '3 Crunchy Tacos Supreme® Combo',
                '3 Soft Tacos Combo', '3 Soft Tacos Supreme® Combo', '3 Doritos® Locos Tacos Combo',
                '3 Doritos® Locos Tacos Supreme Combo', '2 Chicken Chalupas Supreme Combo',
                'Chicken Quesadilla Combo', 'Crunchwrap Supreme® Combo', 'Nachos BellGrande® Combo',
                'Mexican Pizza Combo', 'Burrito Supreme® Combo', 'Steak Grilled Cheese Burrito Combo',
                'Cantina Chicken Burrito Meal', 'Cantina Chicken Quesadilla Meal', 'Cantina Chicken Crispy Taco Meal',
                'Breakfast Crunchwrap Combo', 'Breakfast Quesadilla Combo', 'Grande Toasted Breakfast Burrito Combo',
                'Classic Luxe Box', 'Supreme Luxe Box', 'Discovery Luxe Box', 'Build Your Own Luxe Cravings Box',
                'Taco Party Pack', 'Soft Taco Party Pack', 'Supreme Taco Party Pack',
                'Supreme Soft Taco Party Pack', 'Variety Taco Party Pack', 'Supreme Variety Taco Party Pack',
                'Taco & Burrito Cravings Pack', 'Meal for 2', 'Meal for 4', 'Veggie Meal for 2',
                'Drinks Party Pack'
            ],
            'Cravings Value Menu': [
                'Cheesy Roll Up', 'Spicy Potato Soft Taco', 'Cheesy Bean and Rice Burrito',
                'Cinnamon Twists', '3 Cheese Chicken Flatbread Melt', 'Classic Stacker'
            ],
            'Cantina Chicken Menu': [
                'Cantina Chicken Bowl', 'Cantina Chicken Burrito', 'Cantina Chicken Quesadilla',
                'Cantina Chicken Soft Taco', 'Cantina Chicken Crispy Taco', 'Cantina Chicken Burrito Meal',
                'Cantina Chicken Quesadilla Meal', 'Cantina Chicken Crispy Taco Meal'
            ],
            'Veggie Cravings': [
                'Black Bean Chalupa Supreme', 'Black Bean Chalupa Supreme®', 'Black Bean Crunchwrap Supreme®',
                'Black Bean Grilled Cheese Burrito - Black Beans', 'Spicy Potato Soft Taco',
                'Veggie Mexican Pizza', 'Veggie Bowl', 'Veggie Meal for 2'
            ],
            'Best Sellers': [
                'Crunchwrap Supreme®', 'Cheesy Gordita Crunch', 'Beefy 5-Layer Burrito',
                'Nachos BellGrande®', 'Mexican Pizza', 'Crunchy Taco', 'Soft Taco'
            ],
            'New': [],
            'Online Exclusives': [],
            'Member Exclusives': [],
            'Groups': []
        };

        const items = [];
        const categoryItems = categoryMap[category] || [];
        
        categoryItems.forEach(itemName => {
            if (this.menuData.headers.includes(itemName)) {
                const imagePath = `images/${category}/${encodeURIComponent(itemName)}.jpg`;
                items.push({
                    name: itemName,
                    category: category,
                    imagePath: imagePath
                });
            } else {
                console.log(`Item "${itemName}" not found in menu headers for ${category}`);
            }
        });
        
        console.log(`Found ${items.length} items for Taco Bell category: ${category}`);
        return items;
    }

    buildAllItemsList() {
        this.allItems = [];
        this.categories.forEach(category => {
            category.items.forEach(item => {
                this.allItems.push(item);
            });
        });
    }

    setupSearchBar() {
        const searchInput = document.getElementById('menuSearch');
        const clearBtn = document.getElementById('clearSearch');
        
        searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase().trim();
            clearBtn.style.display = this.searchQuery ? 'flex' : 'none';
            this.renderMenuItems();
        });
        
        clearBtn.addEventListener('click', () => {
            searchInput.value = '';
            this.searchQuery = '';
            clearBtn.style.display = 'none';
            this.renderMenuItems();
        });
        
        // Setup restaurant toggle
        this.setupRestaurantToggle();
        
        // Setup clear selection button
        this.setupClearSelection();
    }
    
    setupRestaurantToggle() {
        const restaurantBtn = document.getElementById('restaurantBtn');
        const restaurantName = document.getElementById('restaurantName');
        const restaurantIcon = restaurantBtn.querySelector('.restaurant-icon');
        
        restaurantBtn.addEventListener('click', async () => {
            // Switch restaurant
            this.currentRestaurant = this.currentRestaurant === 'kfc' ? 'tacobell' : 'kfc';
            const restaurant = this.restaurantData[this.currentRestaurant];
            
            // Update UI
            restaurantName.textContent = restaurant.name;
            restaurantIcon.textContent = restaurant.icon;
            
            // Update loading text
            const loadingEl = document.getElementById('loading');
            loadingEl.textContent = `Loading ${restaurant.name} locations...`;
            loadingEl.style.display = 'block';
            
            // Clear current order and reload data
            this.clearOrder();
            await this.switchRestaurant();
            
            // Hide loading
            loadingEl.style.display = 'none';
        });
    }
    
    setupClearSelection() {
        const clearSelectionBtn = document.getElementById('clearSelectionBtn');
        
        clearSelectionBtn.addEventListener('click', () => {
            this.clearOrder();
        });
    }
    
    clearOrder() {
        this.order = {};
        this.updateUI();
        
        // Force update all open popups to ensure they reflect cleared selection
        if (window.mapManager) {
            window.mapManager.forceUpdateAllPopups();
        }
    }
    
    async switchRestaurant() {
        // Reset all data
        this.menuData = null;
        this.categories = [];
        this.currentCategory = null;
        this.allItems = [];
        this.searchQuery = '';
        
        // Clear UI elements
        const searchInput = document.getElementById('menuSearch');
        const clearBtn = document.getElementById('clearSearch');
        const categoryContainer = document.getElementById('categorySelector');
        const menuItemsContainer = document.getElementById('menuItems');
        
        searchInput.value = '';
        clearBtn.style.display = 'none';
        categoryContainer.innerHTML = '';
        menuItemsContainer.innerHTML = '';
        
        // Reload data for new restaurant
        await this.loadMenuData();
        await this.loadCategories();
        this.buildAllItemsList();
        this.renderCategories();
        
        // Select first category by default
        if (this.categories.length > 0) {
            this.selectCategory(this.categories[0]);
        }
        
        // Notify map to reload locations
        if (window.mapManager) {
            const restaurant = this.restaurantData[this.currentRestaurant];
            window.mapManager.switchRestaurant(restaurant.locationsPath);
        }
    }

    renderCategories() {
        const container = document.getElementById('categorySelector');
        container.innerHTML = '';

        this.categories.forEach(category => {
            const btn = document.createElement('button');
            btn.className = 'category-btn';
            btn.textContent = category.name;
            btn.addEventListener('click', () => this.selectCategory(category));
            container.appendChild(btn);
        });
    }

    selectCategory(category) {
        this.currentCategory = category;
        
        // Update active button
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent === category.name);
        });
        
        this.renderMenuItems();
    }

    renderMenuItems() {
        const container = document.getElementById('menuItems');
        container.innerHTML = '';

        if (!this.currentCategory) return;

        // Determine which items to show
        let itemsToShow;
        if (this.searchQuery) {
            // Search across all items
            itemsToShow = this.allItems.filter(item => 
                item.name.toLowerCase().includes(this.searchQuery)
            );
            
            if (itemsToShow.length === 0) {
                container.innerHTML = '<p class="no-results">No items found matching "' + this.searchQuery + '"</p>';
                return;
            }
        } else {
            // Show current category items
            itemsToShow = this.currentCategory.items;
        }

        itemsToShow.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.className = 'menu-item';
            
            const quantity = this.order[item.name] || 0;
            console.log(`Rendering item: ${item.name}, quantity: ${quantity}, order object:`, this.order);
            
            itemEl.innerHTML = `
                <img src="${item.imagePath}" alt="${item.name}" class="menu-item-image" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22%3E%3Crect width=%22100%22 height=%22100%22 fill=%22%23333%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 fill=%22%23666%22 font-size=%2212%22 text-anchor=%22middle%22 dy=%22.3em%22%3ENo Image%3C/text%3E%3C/svg%3E'">
                <div class="menu-item-info">
                    <h4 class="menu-item-name">${item.name}</h4>
                    <div class="menu-item-counter">
                        <button class="counter-btn decrement-btn" data-item="${item.name.replace(/'/g, "\\'")}">−</button>
                        <span class="counter-value">${quantity}</span>
                        <button class="counter-btn increment-btn" data-item="${item.name.replace(/'/g, "\\'")}">+</button>
                    </div>
                </div>
            `;
            
            // Add event listeners
            const incrementBtn = itemEl.querySelector('.increment-btn');
            const decrementBtn = itemEl.querySelector('.decrement-btn');
            
            incrementBtn.addEventListener('click', () => {
                console.log('Increment button clicked for:', item.name);
                this.incrementItem(item.name);
            });
            
            decrementBtn.addEventListener('click', () => {
                console.log('Decrement button clicked for:', item.name);
                this.decrementItem(item.name);
            });
            
            container.appendChild(itemEl);
        });
    }

    incrementItem(itemName) {
        console.log(`Incrementing item: ${itemName}`);
        this.order[itemName] = (this.order[itemName] || 0) + 1;
        console.log(`New quantity: ${this.order[itemName]}`);
        console.log('Order object:', this.order);
        this.updateUI();
    }

    decrementItem(itemName) {
        console.log(`Decrementing item: ${itemName}`);
        if (this.order[itemName] > 0) {
            this.order[itemName]--;
            if (this.order[itemName] === 0) {
                delete this.order[itemName];
            }
            console.log(`New quantity: ${this.order[itemName] || 0}`);
            this.updateUI();
        }
    }

    updateUI() {
        // Update counter display in menu items
        this.renderMenuItems();
        
        // Update order summary
        this.renderOrderSummary();
        
        // Update pricing
        this.calculateAndDisplayPricing();
    }

    renderOrderSummary() {
        const orderList = document.getElementById('orderList');
        const clearSelectionContainer = document.getElementById('clearSelectionContainer');
        const orderItems = Object.entries(this.order).filter(([_, qty]) => qty > 0);
        
        if (orderItems.length === 0) {
            orderList.innerHTML = '<p class="empty-order">No items in order</p>';
            clearSelectionContainer.style.display = 'none';
            return;
        }
        
        orderList.innerHTML = orderItems.map(([itemName, quantity]) => `
            <div class="order-item">
                <span class="order-item-name">${itemName}</span>
                <span class="order-item-quantity">×${quantity}</span>
            </div>
        `).join('');
        
        // Show clear selection button when there are items
        clearSelectionContainer.style.display = 'block';
    }

    calculateAndDisplayPricing() {
        const orderItems = Object.entries(this.order).filter(([_, qty]) => qty > 0);
        const pricingContainer = document.getElementById('orderPricing');
        
        if (orderItems.length === 0) {
            pricingContainer.style.display = 'none';
            return;
        }
        
        pricingContainer.style.display = 'block';
        
        // First, calculate average price for each item across all stores
        const itemAveragePrices = {};
        orderItems.forEach(([itemName]) => {
            const prices = [];
            this.menuData.data.forEach(storeData => {
                if (storeData.prices[itemName] !== undefined) {
                    prices.push(storeData.prices[itemName]);
                }
            });
            
            if (prices.length > 0) {
                itemAveragePrices[itemName] = prices.reduce((a, b) => a + b, 0) / prices.length;
            } else {
                itemAveragePrices[itemName] = 0; // Fallback if no stores have this item
            }
        });
        
        // Calculate total prices per location, using average price if item is missing
        const locationPrices = {};
        
        this.menuData.data.forEach(storeData => {
            let totalPrice = 0;
            
            orderItems.forEach(([itemName, quantity]) => {
                if (storeData.prices[itemName] !== undefined) {
                    totalPrice += storeData.prices[itemName] * quantity;
                } else {
                    // Use average price if item is not available at this store
                    totalPrice += itemAveragePrices[itemName] * quantity;
                }
            });
            
            locationPrices[storeData.storeId] = totalPrice;
        });
        
        const prices = Object.values(locationPrices);
        
        if (prices.length === 0) {
            document.getElementById('minPrice').textContent = 'N/A';
            document.getElementById('avgPrice').textContent = 'N/A';
            document.getElementById('maxPrice').textContent = 'N/A';
            return;
        }
        
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
        
        document.getElementById('minPrice').textContent = `$${minPrice.toFixed(2)}`;
        document.getElementById('avgPrice').textContent = `$${avgPrice.toFixed(2)}`;
        document.getElementById('maxPrice').textContent = `$${maxPrice.toFixed(2)}`;
        
        // Store for use by map coloring
        this.locationPrices = locationPrices;
    }

    getLocationPriceForColoring(storeId) {
        return this.locationPrices?.[storeId] || null;
    }
}

// Global instance
let menuManager;
