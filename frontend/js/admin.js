// Admin panel: courses, lessons, users CRUD
document.addEventListener('DOMContentLoaded', async () => {
  Auth.requireAdmin();

  const user = Auth.currentUser();
  const nameEl = document.getElementById('admin-user-name');
  if (nameEl && user) nameEl.textContent = user.name;

  // ─── Section navigation ──────────────────────────────────────────────────
  const menuItems = document.querySelectorAll('.admin-menu-item');
  const sections  = document.querySelectorAll('.admin-section');

  menuItems.forEach(item => {
    item.addEventListener('click', () => {
      menuItems.forEach(i => i.classList.remove('active'));
      sections.forEach(s => s.classList.add('hidden'));
      item.classList.add('active');
      document.getElementById(`section-${item.dataset.section}`)?.classList.remove('hidden');
    });
  });

  // ─── Load initial data ───────────────────────────────────────────────────
  await loadCourses();
  await loadUsers();

  // Populate course filter in lessons section
  const filterCourse = document.getElementById('filter-course');
  filterCourse?.addEventListener('change', async () => {
    const cid = filterCourse.value;
    document.getElementById('btn-new-lesson').disabled = !cid;
    if (cid) await loadLessons(cid);
    else document.getElementById('lessons-tbody').innerHTML = '';
  });

  // ─── Courses CRUD ────────────────────────────────────────────────────────
  document.getElementById('btn-new-course')?.addEventListener('click', () => openCourseModal());
  document.getElementById('btn-cancel-course')?.addEventListener('click', closeCourseModal);
  document.getElementById('course-form')?.addEventListener('submit', saveCourse);

  // ─── Lessons CRUD ────────────────────────────────────────────────────────
  document.getElementById('btn-new-lesson')?.addEventListener('click', () => {
    const cid = document.getElementById('filter-course').value;
    openLessonModal(null, cid);
  });
  document.getElementById('btn-cancel-lesson')?.addEventListener('click', closeLessonModal);
  document.getElementById('lesson-form')?.addEventListener('submit', saveLesson);

  // Toggle exercise content textarea visibility
  document.getElementById('lesson-has-exercise')?.addEventListener('change', e => {
    document.getElementById('exercise-content-group').style.display = e.target.checked ? '' : 'none';
  });
  document.getElementById('exercise-content-group').style.display = 'none';
});

// ─── Courses ─────────────────────────────────────────────────────────────────
async function loadCourses() {
  const tbody = document.getElementById('courses-tbody');
  try {
    const courses = await API.get('/admin/courses');
    tbody.innerHTML = '';

    const filterSelect = document.getElementById('filter-course');
    if (filterSelect) filterSelect.innerHTML = '<option value="">— Seleccionar curso —</option>';

    (courses || []).forEach(c => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${_esc(c.title)}</td>
          <td>${c.price_cop ? '$' + Number(c.price_cop).toLocaleString('es-CO') : '—'}</td>
          <td>${c.is_published ? '<span class="badge-published">● Publicado</span>' : '<span class="badge-draft">Borrador</span>'}</td>
          <td class="table-actions">
            <button class="btn btn-ghost btn-sm" onclick="openCourseModal('${c.id}')">Editar</button>
          </td>
        </tr>`);
      if (filterSelect) {
        filterSelect.insertAdjacentHTML('beforeend', `<option value="${c.id}">${_esc(c.title)}</option>`);
      }
    });
  } catch (err) { tbody.innerHTML = `<tr><td colspan="4" style="color:var(--red)">${err.message}</td></tr>`; }
}

async function openCourseModal(courseId = null) {
  const modal = document.getElementById('modal-course');
  const titleEl = document.getElementById('modal-course-title');
  const errEl   = document.getElementById('course-form-error');
  errEl.classList.add('hidden');

  if (courseId) {
    titleEl.textContent = 'Editar curso';
    const courses = await API.get('/admin/courses').catch(() => []);
    const c = (courses || []).find(x => x.id === courseId);
    if (c) {
      document.getElementById('course-id').value         = c.id;
      document.getElementById('course-title-input').value = c.title;
      document.getElementById('course-desc-input').value  = c.description || '';
      document.getElementById('course-price-input').value = c.price_cop || '';
      document.getElementById('course-published-input').checked = !!c.is_published;
    }
  } else {
    titleEl.textContent = 'Nuevo curso';
    document.getElementById('course-form').reset();
    document.getElementById('course-id').value = '';
  }
  modal.classList.remove('hidden');
}

function closeCourseModal() {
  document.getElementById('modal-course').classList.add('hidden');
}

async function saveCourse(e) {
  e.preventDefault();
  const errEl = document.getElementById('course-form-error');
  errEl.classList.add('hidden');
  const id      = document.getElementById('course-id').value;
  const payload = {
    title:        document.getElementById('course-title-input').value.trim(),
    description:  document.getElementById('course-desc-input').value,
    price_cop:    Number(document.getElementById('course-price-input').value) || null,
    is_published: document.getElementById('course-published-input').checked,
  };
  try {
    if (id) { await API.put(`/admin/courses/${id}`, payload); }
    else     { await API.post('/admin/courses', payload); }
    closeCourseModal();
    await loadCourses();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
}

// ─── Lessons ──────────────────────────────────────────────────────────────────
async function loadLessons(courseId) {
  const tbody = document.getElementById('lessons-tbody');
  try {
    const lessons = await API.get(`/admin/lessons?course_id=${courseId}`);
    tbody.innerHTML = '';
    (lessons || []).forEach(l => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${l.module_num} — ${_esc(l.module_name || '')}</td>
          <td>${l.order_in_module}</td>
          <td>${_esc(l.title)}</td>
          <td>${l.video_provider}</td>
          <td class="table-actions">
            <button class="btn btn-ghost btn-sm" onclick="openLessonModal('${l.id}', '${courseId}')">Editar</button>
          </td>
        </tr>`);
    });
  } catch (err) { tbody.innerHTML = `<tr><td colspan="5" style="color:var(--red)">${err.message}</td></tr>`; }
}

async function openLessonModal(lessonId = null, courseId) {
  const modal  = document.getElementById('modal-lesson');
  const titleEl = document.getElementById('modal-lesson-title');
  const errEl   = document.getElementById('lesson-form-error');
  errEl.classList.add('hidden');
  document.getElementById('lesson-form').reset();
  document.getElementById('exercise-content-group').style.display = 'none';
  document.getElementById('lesson-course-id').value = courseId;

  if (lessonId) {
    titleEl.textContent = 'Editar lección';
    const lessons = await API.get(`/admin/lessons?course_id=${courseId}`).catch(() => []);
    const l = (lessons || []).find(x => x.id === lessonId);
    if (l) {
      document.getElementById('lesson-id').value              = l.id;
      document.getElementById('lesson-module-num').value      = l.module_num;
      document.getElementById('lesson-module-name').value     = l.module_name || '';
      document.getElementById('lesson-order').value           = l.order_in_module;
      document.getElementById('lesson-title-input').value     = l.title;
      document.getElementById('lesson-desc-input').value      = l.description || '';
      document.getElementById('lesson-provider').value        = l.video_provider;
      document.getElementById('lesson-video-id').value        = l.video_id || '';
      document.getElementById('lesson-duration').value        = l.duration_seconds || '';
      document.getElementById('lesson-has-exercise').checked  = !!l.has_exercise;
      document.getElementById('lesson-exercise-content').value = l.exercise_content || '';
      if (l.has_exercise) document.getElementById('exercise-content-group').style.display = '';
    }
  } else {
    titleEl.textContent = 'Nueva lección';
    document.getElementById('lesson-id').value = '';
  }
  modal.classList.remove('hidden');
}

function closeLessonModal() {
  document.getElementById('modal-lesson').classList.add('hidden');
}

async function saveLesson(e) {
  e.preventDefault();
  const errEl = document.getElementById('lesson-form-error');
  errEl.classList.add('hidden');
  const id       = document.getElementById('lesson-id').value;
  const courseId = document.getElementById('lesson-course-id').value;
  const payload  = {
    course_id:       courseId,
    module_num:      Number(document.getElementById('lesson-module-num').value),
    module_name:     document.getElementById('lesson-module-name').value,
    order_in_module: Number(document.getElementById('lesson-order').value),
    title:           document.getElementById('lesson-title-input').value.trim(),
    description:     document.getElementById('lesson-desc-input').value,
    video_provider:  document.getElementById('lesson-provider').value,
    video_id:        document.getElementById('lesson-video-id').value,
    duration_seconds: Number(document.getElementById('lesson-duration').value) || null,
    has_exercise:    document.getElementById('lesson-has-exercise').checked,
    exercise_content: document.getElementById('lesson-exercise-content').value,
  };
  try {
    if (id) { await API.put(`/admin/lessons/${id}`, payload); }
    else     { await API.post('/admin/lessons', payload); }
    closeLessonModal();
    await loadLessons(courseId);
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
}

// ─── Users ────────────────────────────────────────────────────────────────────
async function loadUsers() {
  const tbody = document.getElementById('users-tbody');
  try {
    const users = await API.get('/admin/users');
    tbody.innerHTML = '';
    (users || []).forEach(u => {
      tbody.insertAdjacentHTML('beforeend', `
        <tr>
          <td>${_esc(u.name)}</td>
          <td>${_esc(u.email)}</td>
          <td>${u.is_admin ? '<span class="badge-published">Admin</span>' : '—'}</td>
          <td>${new Date(u.created_at).toLocaleDateString('es-CO')}</td>
        </tr>`);
    });
  } catch (err) { tbody.innerHTML = `<tr><td colspan="4" style="color:var(--red)">${err.message}</td></tr>`; }
}

function _esc(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
