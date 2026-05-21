async function refreshOpsStatus() {
  ops.value = { status: 'Checking', latency: '—', cls: 'warn' };
  try {
    const t0 = performance.now();
    const h  = await api('/api/health');
    const ms = Math.round(performance.now() - t0);
    ops.value = {
      status:  h.status === 'ok' ? 'Healthy' : 'Degraded',
      latency: `${ms} ms`,
      cls:     h.status === 'ok' ? 'ok' : 'bad',
    };
  } catch { ops.value = { status: 'Offline', latency: '—', cls: 'bad' }; }
}

async function addToCart(bookId) {
  await api('/api/cart', {
    method: 'POST',
    body: JSON.stringify({ session_id: SESSION_ID,
                           book_id: bookId, quantity: 1 }),
  });
  showToast('Added to cart!');
  await loadCart();           // refresh badge
}

async function placeOrder() {
  try {
    await api('/api/orders', {
      method: 'POST',
      body: JSON.stringify({ session_id: SESSION_ID }),
    });
    showToast('Order placed successfully!');
    await showPage('orders');
  } catch (e) { showToast(e.message, 'danger'); }
}
