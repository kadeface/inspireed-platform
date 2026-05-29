/* MathLab 课堂竞赛模式 — URL 参数 + postMessage 与 InspireEd 通信 */
(function () {
  'use strict';

  const params = new URLSearchParams(window.location.search);
  const mode = params.get('mode');
  const contestId = params.get('contestId');

  /** 专题课竞赛冒烟推荐（任意 curriculum 内 task id 均可） */
  const TOPIC_TASK_EXAMPLES = ['fg_l2_1', 'calc_l2_3'];

  const ContestBridge = {
    active: mode === 'contest' && !!contestId,
    contestId: contestId ? parseInt(contestId, 10) : null,
    taskId: params.get('task') || null,
    submitted: false,
    TOPIC_TASK_EXAMPLES,

    canLoadTask(taskId) {
      if (!taskId || typeof findMathlabTaskById !== 'function') return false;
      return !!findMathlabTaskById(taskId);
    },

    _computeAutoScore(sim, analysis) {
      const task = typeof getCurrentMathlabTask === 'function' ? getCurrentMathlabTask() : null;
      let base = analysis.matchPercent != null ? analysis.matchPercent : 0;

      if (task?.plotValidate && window.FunctionPlot && sim.getPrimaryRobot) {
        const v = task.plotValidate;
        const r = window.FunctionPlot.validateTrailAgainstExpr(
          sim.getPrimaryRobot().trail,
          v.expr,
          {
            originX: sim.state.startX,
            originY: sim.state.startY,
            pxPerCm: sim.getPxPerCm(),
            toleranceCm: v.toleranceCm ?? 1
          }
        );
        if (r.ok) return Math.max(base, 92);
        return Math.min(base, 55);
      }

      if (task?.calcValidate && window.CalcGraph && sim.motionSamples?.length) {
        const cv = task.calcValidate;
        const samples = sim.motionSamples;
        if (cv.type === 'slope') {
          const slope = window.CalcGraph.slopeBetween(
            { t: cv.t0, s: window.CalcGraph.interpolateS(samples, cv.t0) },
            { t: cv.t1, s: window.CalcGraph.interpolateS(samples, cv.t1) }
          );
          const ok = slope != null && Math.abs(slope - cv.expected) <= (cv.tolerance ?? 1);
          return ok ? 92 : 50;
        }
        if (cv.type === 'area') {
          const area = window.CalcGraph.riemannSum(samples, {
            t0: cv.t0,
            t1: cv.t1,
            n: cv.n ?? 10
          });
          const ok = Math.abs(area - cv.expected) <= (cv.tolerance ?? 5);
          return ok ? 92 : 50;
        }
      }

      return base;
    },

    init() {
      if (!this.active) return;
      document.body.classList.add('contest-mode');
      this._injectSubmitButton();
      this._lockLessonPicker();
      window.addEventListener('message', (e) => this._onParentMessage(e));
      if (this.taskId) {
        setTimeout(() => {
          if (!this.canLoadTask(this.taskId)) {
            console.warn('[Contest] Unknown task id:', this.taskId);
          } else if (typeof loadTaskById === 'function') {
            loadTaskById(this.taskId);
          }
        }, 300);
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
      const task = typeof getCurrentMathlabTask === 'function' ? getCurrentMathlabTask() : null;
      const autoScore = this._computeAutoScore(sim, analysis);
      const elapsedSec = sim.state && sim.state.elapsed != null ? sim.state.elapsed : undefined;
      this._postToParent('contest:submit', {
        contestId: this.contestId,
        analysis: analysis,
        autoScore: autoScore,
        autoPassed: autoScore >= 85,
        elapsedSec: elapsedSec,
        taskId: task?.id || this.taskId,
        series: task?.series || null,
        travelSubtype: analysis?.subtype || null,
        meetTimeSec: analysis?.meetTimeSec ?? null,
        finalDistanceCm: analysis?.finalDistanceCm ?? null
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
