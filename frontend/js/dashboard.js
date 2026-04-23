// Dashboard: module list, progress bars, "continue where you left off"
document.addEventListener('DOMContentLoaded', async () => {
  Auth.requireAuth();

  const user = Auth.currentUser();
  const nameEl = document.getElementById('user-name');
  if (nameEl && user) nameEl.textContent = user.name;

  // Determine the first course (hardcoded id=1 or load from list)
  let courseId = null;
  try {
    const courses = await API.get('/courses');
    if (!courses || courses.length === 0) {
      showError('No hay cursos disponibles.');
      return;
    }
    // Find the first course the user is enrolled in
    for (const c of courses) {
      const detail = await API.get(`/courses/${c.id}`);
      if (detail?.is_enrolled) { courseId = c.id; break; }
    }
    if (!courseId) {
      showNotEnrolled();
      return;
    }
  } catch (err) {
    showError(err.message);
    return;
  }

  let modulesData = null;
  try {
    modulesData = await API.get(`/courses/${courseId}/lessons`);
  } catch {
    showNotEnrolled();
    return;
  }

  if (!modulesData) return;

  const { course, modules } = modulesData;

  // Course title
  document.getElementById('course-title').textContent = course.title;

  // Overall progress
  const allLessons = modules.flatMap(m => m.lessons);
  const completedCount = allLessons.filter(l => l.completed).length;
  const pct = allLessons.length ? Math.round(completedCount / allLessons.length * 100) : 0;
  document.getElementById('overall-pct').textContent = `${pct}%`;
  document.getElementById('overall-bar').style.width = `${pct}%`;

  // Find first incomplete lesson
  const firstIncomplete = allLessons.find(l => !l.completed);

  // Continue button
  const continueBtn = document.getElementById('continue-btn');
  if (firstIncomplete && continueBtn) {
    continueBtn.classList.remove('hidden');
    continueBtn.addEventListener('click', () => {
      window.location.href = `/lesson.html?id=${firstIncomplete.id}&course=${courseId}`;
    });
  }

  // Sidebar navigation
  renderSidebar(modules, courseId);

  // Main content modules
  renderModuleCards(modules, courseId);

  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('modules-container').classList.remove('hidden');
});

function renderSidebar(modules, courseId) {
  const nav = document.getElementById('module-nav');
  if (!nav) return;
  nav.innerHTML = '';

  modules.forEach(mod => {
    const total     = mod.lessons.length;
    const completed = mod.lessons.filter(l => l.completed).length;

    const group = document.createElement('div');
    group.className = 'module-group';

    const header = document.createElement('div');
    header.className = 'module-group-header';
    header.innerHTML = `
      <span>${mod.module_num}. ${mod.module_name || 'Módulo ' + mod.module_num}</span>
      <span class="module-progress-pill">${completed}/${total}</span>
      <i class="chevron">›</i>`;

    const list = document.createElement('div');
    list.className = 'lessons-list';

    mod.lessons.forEach(lesson => {
      const item = document.createElement('div');
      item.className = `lesson-item${lesson.completed ? ' completed' : ''}`;
      item.innerHTML = `
        <span class="lesson-check">${lesson.completed ? '✓' : '○'}</span>
        <span class="lesson-title-text">${lesson.title}</span>
        ${lesson.duration_seconds ? `<span class="lesson-duration">${_fmtDuration(lesson.duration_seconds)}</span>` : ''}`;
      item.addEventListener('click', () => {
        window.location.href = `/lesson.html?id=${lesson.id}&course=${courseId}`;
      });
      list.appendChild(item);
    });

    header.addEventListener('click', () => {
      header.classList.toggle('open');
      list.style.display = list.style.display === 'none' ? '' : 'none';
    });
    // Collapse by default if module is done
    if (completed === total && total > 0) {
      list.style.display = 'none';
    } else {
      header.classList.add('open');
    }

    group.appendChild(header);
    group.appendChild(list);
    nav.appendChild(group);
  });
}

function renderModuleCards(modules, courseId) {
  const container = document.getElementById('modules-container');
  if (!container) return;
  container.innerHTML = '';

  modules.forEach(mod => {
    const total     = mod.lessons.length;
    const completed = mod.lessons.filter(l => l.completed).length;
    const pct       = total ? Math.round(completed / total * 100) : 0;

    const block = document.createElement('div');
    block.className = 'module-block';
    block.innerHTML = `
      <div class="module-block-header">
        <h2>${mod.module_num}. ${mod.module_name || 'Módulo ' + mod.module_num}</h2>
        <span class="module-pct-label">${pct}% completado</span>
      </div>
      <div class="progress-bar" style="margin-bottom:1.25rem">
        <div class="progress-fill" style="width:${pct}%"></div>
      </div>`;

    mod.lessons.forEach(lesson => {
      const card = document.createElement('div');
      card.className = `lesson-card${lesson.completed ? ' completed-card' : ''}`;
      card.innerHTML = `
        <div class="lesson-card-icon">${lesson.completed ? '✓' : '▶'}</div>
        <div class="lesson-card-info">
          <h3>${lesson.title}</h3>
          ${lesson.description ? `<p>${lesson.description}</p>` : ''}
        </div>
        ${lesson.duration_seconds ? `<span class="lesson-card-duration">${_fmtDuration(lesson.duration_seconds)}</span>` : ''}`;
      card.addEventListener('click', () => {
        window.location.href = `/lesson.html?id=${lesson.id}&course=${courseId}`;
      });
      block.appendChild(card);
    });

    container.appendChild(block);
  });
}

function _fmtDuration(secs) {
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function showError(msg) {
  const el = document.getElementById('empty-state');
  if (el) el.innerHTML = `<p style="color:var(--red)">${msg}</p>`;
}

function showNotEnrolled() {
  const el = document.getElementById('empty-state');
  if (el) {
    el.innerHTML = `
      <div class="empty-icon">🎤</div>
      <h2>Aún no tienes acceso</h2>
      <p>Completa tu inscripción para ver el contenido del curso.</p>
      <a href="/checkout.html" class="btn btn-primary btn-lg" style="margin-top:1.5rem">Inscribirme ahora</a>`;
  }
}
