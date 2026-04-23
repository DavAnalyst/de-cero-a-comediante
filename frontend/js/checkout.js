// Checkout: fetches Wompi payment data from backend, then loads widget
document.addEventListener('DOMContentLoaded', async () => {
  const loadingEl = document.getElementById('checkout-loading');
  const errorEl   = document.getElementById('checkout-error');
  const errorMsg  = document.getElementById('checkout-error-msg');
  const container = document.getElementById('wompi-container');

  function showError(msg, showLogin = false) {
    loadingEl.classList.add('hidden');
    errorMsg.textContent = msg;
    errorEl.classList.remove('hidden');
    const loginLink = document.getElementById('checkout-login-link');
    if (!showLogin && loginLink) loginLink.classList.add('hidden');
  }

  if (!Auth.isLoggedIn()) {
    showError('Debes iniciar sesión para completar la compra.', true);
    const loginLink = document.getElementById('checkout-login-link');
    if (loginLink) loginLink.href = '/login.html?next=/checkout.html';
    return;
  }

  // Get course id from URL or default to first course
  const params   = new URLSearchParams(location.search);
  let courseId   = params.get('course');

  if (!courseId) {
    try {
      const courses = await API.get('/courses');
      if (!courses || !courses.length) { showError('No hay cursos disponibles.'); return; }
      courseId = courses[0].id;
      // Update price display
      const price = courses[0].price_cop;
      if (price) {
        document.getElementById('checkout-price').textContent =
          '$' + Number(price).toLocaleString('es-CO') + ' COP';
        document.getElementById('checkout-course-title').textContent = courses[0].title;
      }
    } catch (err) { showError(err.message); return; }
  }

  // Request payment data from backend
  let paymentData = null;
  try {
    paymentData = await API.post('/checkout/wompi', { course_id: courseId });
  } catch (err) {
    if (err.message.includes('already have access')) {
      showError('Ya tienes acceso a este curso. Revisa tu dashboard.');
    } else {
      showError(err.message);
    }
    return;
  }

  if (!paymentData) return;

  loadingEl.classList.add('hidden');
  container.classList.remove('hidden');

  // Load Wompi widget script dynamically
  const script = document.createElement('script');
  script.src = 'https://checkout.wompi.co/widget.js';
  script.setAttribute('data-render', 'button');
  script.setAttribute('data-public-key',          paymentData.public_key);
  script.setAttribute('data-currency',            paymentData.currency);
  script.setAttribute('data-amount-in-cents',     String(paymentData.amount_in_cents));
  script.setAttribute('data-reference',           paymentData.reference);
  script.setAttribute('data-signature:integrity', paymentData.signature_integrity);
  script.setAttribute('data-redirect-url',        `${location.origin}/dashboard.html`);
  container.appendChild(script);
});
