// ─── LIVE TIME ───
function updateTime() {
  const el = document.getElementById('live-time');
  if (!el) return;
  const now = new Date();
  el.textContent = now.toLocaleString('en-IN', {
    weekday: 'short', year: 'numeric', month: 'short',
    day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}
setInterval(updateTime, 1000);
updateTime();

// ─── COUNT-UP ANIMATION ───
function animateCount(el) {
  const target = parseFloat(el.dataset.target);
  const isFloat = el.dataset.float === 'true';
  const prefix = el.dataset.prefix || '';
  const duration = 1400;
  const start = performance.now();
  function step(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = target * eased;
    if (isFloat) {
      el.textContent = prefix + current.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    } else {
      el.textContent = prefix + Math.floor(current).toLocaleString('en-IN');
    }
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-target]').forEach((el, i) => {
    setTimeout(() => animateCount(el), i * 120);
  });
});

// ─── FLASH MESSAGES ───
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash-msg').forEach(msg => {
    const close = msg.querySelector('.flash-close');
    if (close) close.addEventListener('click', () => dismissFlash(msg));
    setTimeout(() => dismissFlash(msg), 4500);
  });
});

function dismissFlash(el) {
  el.style.transition = 'all 0.3s ease';
  el.style.opacity = '0';
  el.style.transform = 'translateX(100%)';
  setTimeout(() => el.remove(), 320);
}

// ─── LIVE CHALLAN PREVIEW ───
function updatePreview() {
  const vehicle = document.getElementById('vehicle_number');
  const type = document.getElementById('violation_type');
  const location = document.getElementById('location');
  const fine = document.getElementById('fine_amount');
  const date = document.getElementById('date');

  if (!vehicle) return;

  const pv = document.getElementById('prev-vehicle');
  const pt = document.getElementById('prev-type');
  const pl = document.getElementById('prev-location');
  const pf = document.getElementById('prev-fine');
  const pd = document.getElementById('prev-date');

  if (pv) pv.textContent = vehicle.value.toUpperCase() || '—';
  if (pt) pt.textContent = type ? (type.value || '—') : '—';
  if (pl) pl.textContent = location ? (location.value || '—') : '—';
  if (pf) pf.textContent = fine ? (fine.value ? '₹' + parseFloat(fine.value).toLocaleString('en-IN') : '—') : '—';
  if (pd) pd.textContent = date ? (date.value || '—') : '—';

  if (vehicle.value) {
    vehicle.value = vehicle.value.toUpperCase();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  ['vehicle_number', 'violation_type', 'location', 'fine_amount', 'date'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updatePreview);
    if (el) el.addEventListener('change', updatePreview);
  });
  updatePreview();
});

// ─── SUBMIT LOADING STATE ───
document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form[data-loading]');
  forms.forEach(form => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('[type=submit]');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i> Processing...';
      }
    });
  });
});

// ─── MARK PAID CONFIRM ───
document.querySelectorAll('.mark-paid-form').forEach(form => {
  form.addEventListener('submit', (e) => {
    if (!confirm('Mark this challan as Paid?')) {
      e.preventDefault();
    }
  });
});
