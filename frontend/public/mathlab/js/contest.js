/* MathLab 课堂竞赛模式 — URL 参数 + postMessage 与 InspireEd 通信 */
(function () {
  'use strict';

  const params = new URLSearchParams(window.location.search);
  const mode = params.get('mode');
  const contestId = params.get('contestId');

  const ContestBridge = {
    active: mode === 'contest' && !!contestId,
    contestId: contestId ? parseInt(contestId, 10) : null,
    taskId: params.get('task') || null,
    submitted: false,

    init() {
      if (!this.active) return;
      document.body.classList.add('contest-mode');
      this._injectSubmitButton();
      this._lockLessonPicker();
      window.addEventListener('message', (e) => this._onParentMessage(e));
      if (this.taskId && typeof loadTaskById === 'function') {
        setTimeout(() => loadTaskById(this.taskId), 300);
      }
      this._postToParent('contest:ready', { contestId: this.contestId, taskId: this.taskId });
    },

    _injectSubmitButton() {
      const bar = document.querySelector('.topbar-actions');
      if (!bar || document.getElementById('btnContestSubmit')) return;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-run';
      btn.id = 'btnContestSubmit';
      btn.textContent = '📤 提交成绩';
      btn.addEventListener('click', () => this.submitScore());
      bar.insertBefore(btn, bar.querySelector('#btnRun'));
    },

    _lockLessonPicker() {
      ['selStage', 'selGrade', 'selTask'].forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.disabled = true;
      });
      const btnLesson = document.getElementById('btnDrawerLesson');
      if (btnLesson) btnLesson.style.display = 'none';
    },

    _onParentMessage(e) {
      const msg = e.data;
      if (!msg || msg.source !== 'inspireed') return;
      if (msg.type === 'contest:start' || msg.type === 'contest:task') {
        const taskId = msg.data && msg.data.taskId;
        if (taskId && typeof loadTaskById === 'function') {
          loadTaskById(taskId);
          this.taskId = taskId;
        }
      }
      if (msg.type === 'contest:end') {
        this.active = false;
        document.body.classList.remove('contest-mode');
        const btn = document.getElementById('btnContestSubmit');
        if (btn) btn.disabled = true;
      }
    },

    _postToParent(type, data) {
      if (window.parent === window) return;
      window.parent.postMessage({ source: 'mathlab', type, data: data || {} }, '*');
    },

    submitScore() {
      const sim = window.__simRef;
      if (!sim) {
        alert('仿真未就绪');
        return;
      }
      if (sim.busy) {
        alert('请等待程序运行结束后再提交');
        return;
      }
      let analysis = sim.lastAnalysis;
      if (!analysis && typeof TrailAnalysis !== 'undefined') {
        analysis = sim.runAnalysis();
      }
      if (!analysis) {
        analysis = { matchPercent: 0, message: '无轨迹数据' };
      }
      const autoScore = analysis.matchPercent != null ? analysis.matchPercent : 0;
      const elapsedSec = sim.state && sim.state.elapsed != null ? sim.state.elapsed : undefined;
      this._postToParent('contest:submit', {
        contestId: this.contestId,
        analysis: analysis,
        autoScore: autoScore,
        elapsedSec: elapsedSec
      });
      this.submitted = true;
      const btn = document.getElementById('btnContestSubmit');
      if (btn) {
        btn.textContent = '✓ 已提交';
        btn.disabled = true;
      }
      if (typeof ViewShell !== 'undefined' && ViewShell.setStatus) {
        ViewShell.setStatus('成绩已提交到课堂', 'ok');
      }
    }
  };

  window.ContestBridge = ContestBridge;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => ContestBridge.init());
  } else {
    ContestBridge.init();
  }
})();
