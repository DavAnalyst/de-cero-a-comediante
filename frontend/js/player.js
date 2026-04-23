// Lesson player: loads signed video URL, tracks progress, marks completion
document.addEventListener('DOMContentLoaded', async () => {
  Auth.requireAuth();

  const params   = new URLSearchParams(location.search);
  const lessonId = params.get('id');
  const courseId = params.get('course');

  if (!lessonId) { window.location.href = '/dashboard.html'; return; }

  let lessonData = null;
  try {
    lessonData = await API.get(`/lessons/${lessonId}`);
  } catch (err) {
    _showError(err.message);
    return;
  }
  if (!lessonData) return;

  // Populate meta
  document.getElementById('lesson-title').textContent       = lessonData.title;
  document.getElementById('lesson-description').textContent = lessonData.description || '';
  document.getElementById('lesson-progress-pill').textContent = `Módulo ${lessonData.module_num} · Lección ${lessonData.order_in_module}`;

  // Exercise
  if (lessonData.has_exercise && lessonData.exercise_content) {
    const sec = document.getElementById('exercise-section');
    sec.classList.remove('hidden');
    document.getElementById('exercise-content').textContent = lessonData.exercise_content;
  }

  // Video
  const loading = document.getElementById('video-loading');
  const video   = document.getElementById('lesson-video');

  if (lessonData.video_url) {
    video.src = lessonData.video_url;
    video.classList.remove('hidden');
    loading.classList.add('hidden');
  } else {
    loading.innerHTML = '<p style="color:var(--text-muted)">Video no disponible.</p>';
  }

  // ─── Progress tracking ──────────────────────────────────────────────────
  let progressPosted = false;
  let lastPostedPct  = 0;

  video.addEventListener('timeupdate', async () => {
    if (!video.duration) return;
    const pct = Math.floor(video.currentTime / video.duration * 100);

    // Post every 10% increment
    if (pct >= lastPostedPct + 10 && pct < 90) {
      lastPostedPct = pct;
      API.post('/progress', { lesson_id: lessonId, watch_percentage: pct, completed: false }).catch(() => {});
    }

    // Mark complete at 90%
    if (pct >= 90 && !progressPosted) {
      progressPosted = true;
      try {
        await API.post('/progress', { lesson_id: lessonId, watch_percentage: pct, completed: true });
        _showCompletionOverlay(courseId, lessonId);
      } catch { progressPosted = false; }
    }
  });

  // ─── Sibling navigation (load course structure) ─────────────────────────
  if (courseId) {
    try {
      const { modules } = await API.get(`/courses/${courseId}/lessons`);
      const allLessons  = modules.flatMap(m => m.lessons);
      const idx         = allLessons.findIndex(l => l.id === lessonId);

      const prevBtn = document.getElementById('prev-btn');
      const nextBtn = document.getElementById('next-btn');

      if (idx > 0) {
        prevBtn.classList.remove('hidden');
        prevBtn.addEventListener('click', () => {
          window.location.href = `/lesson.html?id=${allLessons[idx - 1].id}&course=${courseId}`;
        });
      }
      if (idx < allLessons.length - 1) {
        nextBtn.classList.remove('hidden');
        nextBtn.addEventListener('click', () => {
          window.location.href = `/lesson.html?id=${allLessons[idx + 1].id}&course=${courseId}`;
        });
      }

      // Wire completion overlay next button
      document.getElementById('next-lesson-btn')?.addEventListener('click', () => {
        if (idx < allLessons.length - 1) {
          window.location.href = `/lesson.html?id=${allLessons[idx + 1].id}&course=${courseId}`;
        } else {
          window.location.href = '/dashboard.html';
        }
      });
    } catch { /* navigation optional */ }
  }
});

function _showCompletionOverlay(courseId, lessonId) {
  const overlay = document.getElementById('completion-overlay');
  overlay?.classList.remove('hidden');
}

function _showError(msg) {
  document.getElementById('video-loading').innerHTML = `<p style="color:var(--red)">${msg}</p>`;
  document.getElementById('lesson-title').textContent = 'Error al cargar la lección';
}
