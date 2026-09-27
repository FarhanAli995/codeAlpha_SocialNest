// Social Nest – shared frontend behavior
document.addEventListener('DOMContentLoaded', function () {
  // Render Lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Password visibility toggles
  document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = document.querySelector(btn.getAttribute('data-toggle-password'));
      if (!target) return;
      var isText = target.getAttribute('type') === 'text';
      target.setAttribute('type', isText ? 'password' : 'text');
      btn.innerHTML = isText ? '<i data-lucide="eye"></i>' : '<i data-lucide="eye-off"></i>';
      if (window.lucide) window.lucide.createIcons();
    });
  });

  // Image preview for avatar / cover uploads
  document.querySelectorAll('[data-preview-target]').forEach(function (input) {
    input.addEventListener('change', function () {
      var file = input.files && input.files[0];
      if (!file) return;
      var target = document.querySelector(input.getAttribute('data-preview-target'));
      if (!target) return;
      var reader = new FileReader();
      reader.onload = function (e) {
        if (target.tagName === 'IMG') {
          target.src = e.target.result;
        } else {
          target.style.backgroundImage = 'url(' + e.target.result + ')';
        }
      };
      reader.readAsDataURL(file);
    });
  });

  // Trigger hidden file inputs from overlay buttons
  document.querySelectorAll('[data-trigger-input]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var input = document.querySelector(btn.getAttribute('data-trigger-input'));
      if (input) input.click();
    });
  });

  // Auto-dismiss toasts
  document.querySelectorAll('.toast').forEach(function (toast) {
    setTimeout(function () {
      toast.style.transition = 'opacity .4s ease';
      toast.style.opacity = '0';
      setTimeout(function () { toast.remove(); }, 400);
    }, 4000);
  });

  // Notification badge polling
  var badge = document.getElementById('navNotifBadge');
  function refreshBadge() {
    if (!badge) return;
    fetch('/notifications/unread-count/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data) return;
        if (data.unread_count > 0) {
          badge.textContent = data.unread_count;
          badge.hidden = false;
        } else {
          badge.hidden = true;
        }
      })
      .catch(function () {});
  }
  if (badge) {
    refreshBadge();
    setInterval(refreshBadge, 30000);
  }
});
