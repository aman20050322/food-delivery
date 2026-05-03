// PLEASE DO NOT SAVE THIS FILE IN YOUR EDITOR - IT IS OVERWRITING THE BACKEND LOGIC!
// Food data (100% Vegetarian)
const foods = [
  { id: 1, name: 'Margherita Pizza', desc: 'Italian Delight', price: 350, badge: 'Best Seller', badgeColor: '#ef4444', image: 'images/margherita.png' },
  { id: 2, name: 'Gourmet Veggie Burger', desc: 'Classic Fast Food', price: 199, badge: 'Popular', badgeColor: '#f59e0b', image: 'images/veggie_burger.png' },
  { id: 3, name: 'Avocado Salad', desc: 'Fresh Greens', price: 220, badge: 'Healthy', badgeColor: '#10b981', image: 'images/avocado_salad.png' },
  { id: 4, name: 'Spicy Veg Noodles', desc: 'Asian Cuisine', price: 290, badge: 'Spicy', badgeColor: '#f97316', image: 'images/spicy_noodles.png' },
  { id: 5, name: 'Mushroom Alfredo', desc: 'Creamy & Rich', price: 380, badge: 'Classic', badgeColor: '#3b82f6', image: 'images/mushroom_alfredo.png' },
  { id: 6, name: 'Chocolate Lava Cake', desc: 'Dessert', price: 260, badge: 'Sweet', badgeColor: '#ec4899', image: 'images/lava_cake.png' },
  { id: 7, name: 'Avocado Sushi Rolls', desc: 'Fresh Seaweed', price: 550, badge: 'Premium', badgeColor: '#8b5cf6', image: 'images/sushi_rolls.png' },
  { id: 8, name: 'Paneer Tikka Masala', desc: 'Rich & Creamy', price: 320, badge: 'Local Fav', badgeColor: '#f59e0b', image: 'images/tikka_masala.png' },
  { id: 9, name: 'Black Bean Tacos', desc: 'Authentic Mexican', price: 210, badge: 'New', badgeColor: '#10b981', image: 'images/bean_tacos.png' },
  { id: 10, name: 'Grilled Portobello', desc: 'Fine Dining', price: 850, badge: 'Deluxe', badgeColor: '#ef4444', image: 'images/portobello.png' },
  { id: 11, name: 'Fluffy Pancakes', desc: 'Breakfast Classic', price: 180, badge: 'Sweet', badgeColor: '#fcd34d', image: 'images/pancakes.png' },
  { id: 12, name: 'Greek Quinoa Salad', desc: 'Crisp & Fresh', price: 200, badge: 'Healthy', badgeColor: '#34d399', image: 'images/quinoa_salad.png' },
  { id: 13, name: 'Miso Veggie Ramen', desc: 'Japanese Comfort', price: 420, badge: 'Hot', badgeColor: '#f97316', image: 'images/ramen.png' },
  { id: 14, name: 'Italian Gelato', desc: 'Artisanal Ice Cream', price: 160, badge: 'Dessert', badgeColor: '#ec4899', image: 'images/gelato.png' }
];

let cart = [];

// DOM Elements
const menuGrid = document.getElementById('menu-grid');
const cartBadge = document.getElementById('cart-badge');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalPrice = document.getElementById('cart-total-price');
const cartSidebar = document.getElementById('cart-sidebar');
const cartToggleBtn = document.getElementById('cart-toggle');
const closeCartBtn = document.getElementById('close-cart');
const checkoutBtn = document.getElementById('checkout-btn');
const toast = document.getElementById('toast');

// Render Menu
function renderMenu() {
  menuGrid.innerHTML = foods.map(food => `
    <div class="card">
      <img src="${food.image}" alt="${food.name}" class="card-img">
      <div class="card-body">
        <span class="badge" style="background:${food.badgeColor}22; color:${food.badgeColor}">${food.badge}</span>
        <h3>${food.name}</h3>
        <div class="meta">${food.desc}</div>
        <div class="stars">&#9733;&#9733;&#9733;&#9733;&#9734;</div>
        <div class="card-footer">
          <div class="price">Rs. ${food.price}</div>
          <button class="add-btn" onclick="addToCart(${food.id})">Add to Cart</button>
        </div>
      </div>
    </div>
  `).join('');
}

// Add to Cart
window.addToCart = function(id) {
  const food = foods.find(f => f.id === id);
  if (!food) return;

  const existingItem = cart.find(item => item.id === id);
  if (existingItem) {
    existingItem.quantity += 1;
  } else {
    cart.push({ ...food, quantity: 1 });
  }

  updateCartUI();
  showToast(`Added ${food.name} to cart!`);
};

// Remove from Cart
window.removeFromCart = function(id) {
  cart = cart.filter(item => item.id !== id);
  updateCartUI();
};

// Update Cart UI
function updateCartUI() {
  // Update badge
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  cartBadge.textContent = totalItems;

  // Update items list
  if (cart.length === 0) {
    cartItemsContainer.innerHTML = '<div class="empty-cart">Your cart is empty.</div>';
    cartTotalPrice.textContent = 'Rs. 0';
    return;
  }

  cartItemsContainer.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div class="item-info">
        <h4><img src="${item.image}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover; vertical-align: middle; margin-right: 8px;"> ${item.name}</h4>
        <div class="item-price">Rs. ${item.price} <span class="item-quantity">x ${item.quantity}</span></div>
      </div>
      <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
    </div>
  `).join('');

  // Update total
  const totalprice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  cartTotalPrice.textContent = 'Rs. ' + totalprice;
}

// Show Toast
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2500);
}

// Event Listeners
cartToggleBtn.addEventListener('click', () => cartSidebar.classList.add('open'));
closeCartBtn.addEventListener('click', () => cartSidebar.classList.remove('open'));

checkoutBtn.addEventListener('click', () => {
  if (cart.length === 0) {
    showToast('Your cart is empty!');
    return;
  }
  // Save cart state
  localStorage.setItem('cart', JSON.stringify(cart));
  // Redirect to checkout
  window.location.href = 'checkout.html';
});

// Auth UI
function updateAuthUI() {
  const user = localStorage.getItem('user');
  const navLinks = document.querySelector('.nav-links');
  if (user && navLinks) {
    const firstLetter = user.charAt(0).toUpperCase();
    navLinks.innerHTML = `
      <a href="index.html" class="active">Menu</a>
      <div class="user-avatar" title="Logged in as ${user}" style="width: 38px; height: 38px; background: linear-gradient(135deg, #f97316, #fbbf24); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; cursor: pointer; box-shadow: 0 4px 12px rgba(249,115,22,0.3);" onclick="logout()">${firstLetter}</div>
    `;
  }
}

window.logout = function() {
  localStorage.removeItem('user');
  window.location.reload();
};

updateAuthUI();

// Initialize
renderMenu();
