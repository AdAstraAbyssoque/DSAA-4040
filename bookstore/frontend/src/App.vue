<template>
  <nav class="navbar navbar-expand-lg navbar-dark sticky-top" id="mainNav">
    <div class="container">
      <a class="navbar-brand" href="#" @click.prevent="showPage('books')">
        <i class="bi bi-book-half"></i> Cloud Bookstore
      </a>
      <div class="d-flex align-items-center gap-2">
        <form class="search-form d-flex" role="search" @submit.prevent="loadBooks">
          <div class="input-group input-group-sm">
            <span class="input-group-text bg-transparent border-end-0 text-white-50">
              <i class="bi bi-search"></i>
            </span>
            <input v-model="searchQuery" class="form-control border-start-0" type="search" placeholder="Search title or author..." />
          </div>
        </form>
        <button class="btn btn-nav position-relative" title="Shopping Cart" @click="showPage('cart')">
          <i class="bi bi-bag"></i>
          <span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
        </button>
        <button class="btn btn-nav" title="My Orders" @click="showPage('orders')">
          <i class="bi bi-clock-history"></i>
        </button>
      </div>
    </div>
  </nav>

  <section v-if="page === 'books'" class="hero-banner">
    <div class="container">
      <div class="row align-items-center">
        <div class="col-lg-7">
          <p class="hero-kicker">Cloud-native bookstore</p>
          <h1 class="hero-title">Build Your<br /><span>Cloud Bookshelf</span></h1>
          <p class="hero-subtitle">A focused reading collection for cloud computing, data systems, DevOps, and modern software engineering.</p>
        </div>
        <div class="col-lg-5">
          <div class="ops-card">
            <div class="ops-card-header">
              <span><i class="bi bi-activity me-1"></i>Deployment Snapshot</span>
              <button class="ops-refresh" title="Refresh metrics" @click="refreshOpsStatus"><i class="bi bi-arrow-clockwise"></i></button>
            </div>
            <div class="ops-grid">
              <div class="ops-metric">
                <div class="ops-value">
                  <span class="status-dot" :class="ops.statusClass"></span>{{ ops.status }}
                </div>
                <div class="ops-label">API Health</div>
              </div>
              <div class="ops-metric">
                <div class="ops-value">{{ ops.latency }}</div>
                <div class="ops-label">API Latency</div>
              </div>
              <div class="ops-metric">
                <div class="ops-value">2 → 8</div>
                <div class="ops-label">API Pods</div>
              </div>
              <div class="ops-metric">
                <div class="ops-value">Redis</div>
                <div class="ops-label">Read Cache</div>
              </div>
            </div>
            <div class="ops-route">
              <span><i class="bi bi-diagram-3 me-1"></i>Ingress route</span>
              <code>/api/* → backend-service:8000</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <main class="container main-content">
    <section v-if="page === 'books'">
      <div class="toolbar">
        <div class="d-flex align-items-center gap-2">
          <h5 class="mb-0 fw-bold"><i class="bi bi-grid-3x3-gap-fill me-2"></i>Catalog</h5>
          <span class="results-count">{{ books.length }} books</span>
        </div>
        <select v-model="categoryFilter" class="form-select form-select-sm category-select" @change="loadBooks">
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
        </select>
      </div>

      <div class="category-rail">
        <button class="category-chip" :class="{ active: categoryFilter === '' }" @click="selectCategory('')">All</button>
        <button v-for="category in categories" :key="category" class="category-chip" :class="{ active: categoryFilter === category }" @click="selectCategory(category)">
          {{ category }}
        </button>
      </div>

      <div v-if="books.length === 0" class="empty-state">
        <i class="bi bi-search"></i>
        <p>No books match your search.</p>
      </div>
      <div v-else class="row g-4">
        <div v-for="book in books" :key="book.id" class="col-6 col-md-4 col-lg-3">
          <div class="card book-card h-100" @click="openBook(book)">
            <div class="book-cover-wrap">
              <img :src="book.cover_url" class="book-cover" :alt="book.title" />
              <div class="book-overlay"><span><i class="bi bi-eye me-1"></i>View Details</span></div>
            </div>
            <div class="book-info">
              <span class="cat-pill" :class="catClass(book.category)">{{ book.category }}</span>
              <div class="book-title">{{ book.title }}</div>
              <div class="book-author">{{ book.author }}</div>
              <div class="book-bottom">
                <span class="book-price">${{ book.price.toFixed(2) }}</span>
                <span class="stock-text">
                  <span class="stock-dot" :class="book.stock > 0 ? 'stock-in' : 'stock-out'"></span>
                  {{ book.stock > 0 ? `${book.stock} left` : 'Sold out' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="page === 'cart'">
      <div class="page-header">
        <h4 class="fw-bold mb-0"><i class="bi bi-bag me-2"></i>Shopping Cart</h4>
      </div>
      <div v-if="cart.length === 0" class="empty-state">
        <i class="bi bi-bag-x"></i>
        <p>Your cart is empty.</p>
        <button class="btn-browse" @click="showPage('books')"><i class="bi bi-arrow-left me-1"></i>Browse Books</button>
      </div>
      <div v-else class="cart-card">
        <div v-for="item in cart" :key="item.id" class="cart-item">
          <img :src="item.book.cover_url" class="cart-item-img" alt="" />
          <div class="cart-item-info">
            <div class="cart-item-title">{{ item.book.title }}</div>
            <div class="cart-item-author">{{ item.book.author }}</div>
          </div>
          <div class="qty-control">
            <button @click="updateQty(item.id, item.quantity - 1)">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="updateQty(item.id, item.quantity + 1)">+</button>
          </div>
          <div class="cart-item-price ms-3">${{ (item.book.price * item.quantity).toFixed(2) }}</div>
          <button class="btn-remove ms-2" title="Remove" @click="removeFromCart(item.id)"><i class="bi bi-x-lg"></i></button>
        </div>
        <div class="cart-summary">
          <span class="cart-total">Total: <span class="book-price">${{ cartTotal.toFixed(2) }}</span></span>
          <button class="btn-checkout" @click="placeOrder"><i class="bi bi-bag-check me-1"></i>Place Order</button>
        </div>
      </div>
    </section>

    <section v-if="page === 'orders'">
      <div class="page-header">
        <h4 class="fw-bold mb-0"><i class="bi bi-clock-history me-2"></i>Order History</h4>
      </div>
      <div v-if="orders.length === 0" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p>No orders yet.</p>
        <button class="btn-browse" @click="showPage('books')"><i class="bi bi-arrow-left me-1"></i>Start Shopping</button>
      </div>
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="order-header">
          <div class="d-flex align-items-center gap-2">
            <span class="order-id">Order #{{ order.id }}</span>
            <span class="order-status" :class="order.status === 'confirmed' ? 'status-confirmed' : 'status-pending'">{{ order.status }}</span>
          </div>
          <span class="order-date"><i class="bi bi-calendar3 me-1"></i>{{ new Date(order.created_at).toLocaleString() }}</span>
        </div>
        <div class="order-body">
          <div v-for="item in order.items" :key="item.id" class="order-item">
            <span class="order-item-name">{{ item.book_title }} <span class="text-muted">x {{ item.quantity }}</span></span>
            <span class="order-item-price">${{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
          <div class="order-total">Total: <span class="book-price">${{ order.total_price.toFixed(2) }}</span></div>
        </div>
      </div>
    </section>
  </main>

  <div class="modal fade" id="bookModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div v-if="selectedBook" class="modal-content book-modal-content">
        <div class="modal-body p-0">
          <img :src="selectedBook.cover_url" class="modal-detail-cover" :alt="selectedBook.title" />
          <div class="modal-detail-body">
            <span class="cat-pill mb-2" :class="catClass(selectedBook.category)">{{ selectedBook.category }}</span>
            <h4>{{ selectedBook.title }}</h4>
            <div class="modal-detail-meta">
              <span><i class="bi bi-person"></i>{{ selectedBook.author }}</span>
              <span><i class="bi bi-tag"></i>${{ selectedBook.price.toFixed(2) }}</span>
              <span><i class="bi bi-box-seam"></i>{{ selectedBook.stock }} in stock</span>
            </div>
            <p class="modal-detail-desc">{{ selectedBook.description || 'No description available.' }}</p>
            <button class="btn-add-cart" :disabled="selectedBook.stock <= 0" @click="addToCart(selectedBook.id)">
              <i class="bi bi-bag-plus me-1"></i>{{ selectedBook.stock > 0 ? 'Add to Cart' : 'Out of Stock' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div id="appToast" class="toast align-items-center border-0 shadow-lg" :class="toast.type === 'danger' ? 'text-bg-danger' : 'text-bg-success'" role="alert">
      <div class="d-flex">
        <div class="toast-body fw-medium">{{ toast.message }}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  </div>

  <footer class="site-footer">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
        <span><i class="bi bi-book-half me-1"></i> Cloud Bookstore</span>
        <span>Vue 3 · FastAPI · PostgreSQL · Redis · Kubernetes</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { Modal, Toast } from 'bootstrap';

const API_BASE = '';
const SESSION_ID = localStorage.getItem('session_id') || (() => {
  const id = `sess_${Math.random().toString(36).substring(2, 12)}`;
  localStorage.setItem('session_id', id);
  return id;
})();

const page = ref('books');
const books = ref([]);
const categories = ref([]);
const cart = ref([]);
const orders = ref([]);
const searchQuery = ref('');
const categoryFilter = ref('');
const selectedBook = ref(null);
const toast = ref({ message: '', type: 'success' });
const ops = ref({ status: 'Checking', latency: '-- ms', statusClass: 'status-warn' });

const cartCount = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0));
const cartTotal = computed(() => cart.value.reduce((sum, item) => sum + item.book.price * item.quantity, 0));

const catClasses = {
  'Cloud Computing': 'cat-cloud',
  'Big Data': 'cat-bigdata',
  DevOps: 'cat-devops',
  Database: 'cat-database',
  'Software Engineering': 'cat-se',
};
const catClass = (category) => catClasses[category] || 'cat-default';

async function api(path, options = {}) {
  const response = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || data.error || 'Request failed');
  return data;
}

function showToast(message, type = 'success') {
  toast.value = { message, type };
  new Toast(document.getElementById('appToast'), { delay: 2400 }).show();
}

async function refreshOpsStatus() {
  ops.value = { status: 'Checking', latency: '-- ms', statusClass: 'status-warn' };
  try {
    const start = performance.now();
    const health = await api('/api/health');
    const latency = Math.round(performance.now() - start);
    ops.value = {
      status: health.status === 'ok' ? 'Healthy' : 'Degraded',
      latency: `${latency} ms`,
      statusClass: health.status === 'ok' ? 'status-ok' : 'status-bad',
    };
  } catch {
    ops.value = { status: 'Offline', latency: '-- ms', statusClass: 'status-bad' };
  }
}

async function loadBooks() {
  books.value = await api(`/api/books?q=${encodeURIComponent(searchQuery.value)}&category=${encodeURIComponent(categoryFilter.value)}`);
  await loadCart();
}

async function loadCategories() {
  categories.value = await api('/api/categories');
}

function selectCategory(category) {
  categoryFilter.value = category;
  loadBooks();
}

async function showPage(target) {
  page.value = target;
  if (target === 'books') {
    await loadBooks();
    refreshOpsStatus();
  }
  if (target === 'cart') await loadCart();
  if (target === 'orders') await loadOrders();
}

async function openBook(book) {
  selectedBook.value = await api(`/api/books/${book.id}`);
  new Modal(document.getElementById('bookModal')).show();
}

async function addToCart(bookId) {
  await api('/api/cart', {
    method: 'POST',
    body: JSON.stringify({ session_id: SESSION_ID, book_id: bookId, quantity: 1 }),
  });
  showToast('Added to cart!');
  await loadCart();
  Modal.getInstance(document.getElementById('bookModal'))?.hide();
}

async function loadCart() {
  cart.value = await api(`/api/cart?session_id=${SESSION_ID}`);
}

async function updateQty(id, quantity) {
  if (quantity <= 0) return removeFromCart(id);
  await api(`/api/cart/${id}`, { method: 'PUT', body: JSON.stringify({ quantity }) });
  await loadCart();
}

async function removeFromCart(id) {
  await api(`/api/cart/${id}`, { method: 'DELETE' });
  await loadCart();
}

async function placeOrder() {
  try {
    await api('/api/orders', {
      method: 'POST',
      body: JSON.stringify({ session_id: SESSION_ID }),
    });
    showToast('Order placed successfully!');
    await showPage('orders');
  } catch (error) {
    showToast(error.message, 'danger');
  }
}

async function loadOrders() {
  orders.value = await api(`/api/orders?session_id=${SESSION_ID}`);
  await loadCart();
}

onMounted(async () => {
  await loadCategories();
  await loadBooks();
  await loadCart();
  refreshOpsStatus();
});
</script>
