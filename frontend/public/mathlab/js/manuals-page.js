(function () {
  'use strict';

  const state = {
    index: null,
    volumeById: new Map(),
    activeVolumeId: null,
    isEmbedded: false
  };

  function qs(id) {
    return document.getElementById(id);
  }

  function formatGeneratedAt(iso) {
    if (!iso) return '未找到生成时间';
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return iso;
    return `最近生成：${date.toLocaleString('zh-CN', { hour12: false })}`;
  }

  async function getJson(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`加载失败: ${path}`);
    return res.json();
  }

  function volumeBtnHtml(volume) {
    return [
      `<button class="volume-btn${state.activeVolumeId === volume.id ? ' active' : ''}" data-volume-id="${volume.id}">`,
      `${volume.title}`,
      `<span class="meta">${volume.taskCount} 课 · ${volume.sectionCount} 章</span>`,
      '</button>'
    ].join('');
  }

  function renderVolumeList() {
    const stageList = qs('stageList');
    const subjectList = qs('subjectList');
    stageList.innerHTML = state.index.stageVolumes.map((v) => `<li>${volumeBtnHtml(v)}</li>`).join('');
    subjectList.innerHTML = state.index.subjectVolumes.map((v) => `<li>${volumeBtnHtml(v)}</li>`).join('');

    document.querySelectorAll('.volume-btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.volumeId;
        await openVolume(id);
        renderVolumeList();
      });
    });
  }

  function renderSummary(volume) {
    qs('volumeSummary').innerHTML = [
      `<h2>${volume.title}</h2>`,
      `<p class="chips">类型：${volume.type === 'stage' ? '学段主册' : '专题册'} · 总任务：${volume.taskCount} · 章节：${volume.sections.length}</p>`,
      '<ul>',
      '<li>册前说明：用于按章组织课堂实验活动。</li>',
      '<li>任务编码：保留原始 task.id，便于与仿真任务联动。</li>',
      '<li>内容字段：目标、挑战、公式、提示、场景配置摘要。</li>',
      '</ul>'
    ].join('');
  }

  function renderToc(volume) {
    const sectionNameKey = volume.type === 'stage' ? 'gradeName' : 'levelName';
    const sectionItemHtml = volume.sections.map((section, sectionIdx) => {
      const sectionTitle = section[sectionNameKey];
      const taskItems = (section.tasks || []).map((task, idx) => (
        `<li><a href="#task-${task.id}">${idx + 1}. ${task.title}</a></li>`
      )).join('');
      return [
        '<li>',
        `<button type="button" class="toc-section-title" data-toc-toggle="${sectionIdx}" aria-expanded="false">`,
        `<span>${sectionTitle}（${section.taskCount} 课）</span>`,
        '<span class="toc-toggle-icon">▸</span>',
        '</button>',
        `<ol class="toc-sublist" data-toc-panel="${sectionIdx}" hidden>${taskItems}</ol>`,
        '</li>'
      ].join('');
    }).join('');

    qs('volumeToc').innerHTML = [
      '<h2>目录</h2>',
      '<ol class="toc-list toc-with-sub">',
      sectionItemHtml,
      '</ol>'
    ].join('');

    bindTocToggleEvents();
  }

  function bindTocToggleEvents() {
    const buttons = document.querySelectorAll('[data-toc-toggle]');
    buttons.forEach((btn) => {
      btn.addEventListener('click', () => {
        const key = btn.dataset.tocToggle;
        const panel = document.querySelector(`[data-toc-panel="${key}"]`);
        if (!panel) return;
        const expanded = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', expanded ? 'false' : 'true');
        panel.hidden = expanded;
      });
    });
  }

  function renderTasks(volume) {
    const sectionNameKey = volume.type === 'stage' ? 'gradeName' : 'levelName';
    const blocks = [];
    volume.sections.forEach((section, sectionIdx) => {
      blocks.push(`<h3>第${sectionIdx + 1}章 ${section[sectionNameKey]}</h3>`);
      section.tasks.forEach((task, idx) => {
        blocks.push(`<div class="task-item" id="task-${task.id}">`);
        blocks.push(`<strong>${sectionIdx + 1}.${idx + 1} ${task.title}</strong>`);
        blocks.push(`<p class="chips">ID: ${task.id} · 单元: ${task.unit || '未标注'} · 场景: ${task.scene}</p>`);
        blocks.push(`<div class="task-actions"><button type="button" class="btn ghost btn-practice" data-task-id="${task.id}">开始练习</button></div>`);
        blocks.push(`<p><b>标签：</b>${task.tags?.length ? task.tags.join('、') : '无'}</p>`);
        blocks.push(`<p><b>教学目标：</b>${task.goals?.length ? task.goals.join('；') : '无'}</p>`);
        blocks.push(`<p><b>挑战任务：</b>${task.challenges?.length ? task.challenges.join('；') : '无'}</p>`);
        blocks.push(renderFormulaBlock(task.formulas));
        blocks.push(`<p><b>提示：</b>${task.hint || '无'}</p>`);
        blocks.push(renderStarterBlocks(task));
        blocks.push('</div>');
      });
    });
    qs('volumeTasks').innerHTML = `<h2>任务详情</h2>${blocks.join('')}`;
    bindPracticeEvents();
  }

  function bindPracticeEvents() {
    document.querySelectorAll('.btn-practice').forEach((btn) => {
      btn.addEventListener('click', () => {
        const taskId = btn.dataset.taskId;
        if (!taskId) return;
        if (state.isEmbedded && window.parent && window.parent !== window) {
          try {
            if (typeof window.parent.loadTaskById === 'function') {
              const ok = window.parent.loadTaskById(taskId);
              if (ok) return;
            }
          } catch (_) {
            // Ignore direct call failures and fallback to postMessage.
          }
          const payload = { source: 'mathlab-manual', type: 'load-task', taskId };
          window.parent.postMessage(payload, '*');
          return;
        }
        const next = new URL(window.location.href);
        next.pathname = next.pathname.replace(/manuals\.html$/, 'index.html');
        next.searchParams.set('task', taskId);
        window.location.href = next.toString();
      });
    });
  }

  function renderFormulaBlock(formulas) {
    if (!Array.isArray(formulas) || !formulas.length) {
      return '<p><b>数学公式：</b>无</p>';
    }
    const items = formulas.map((f) => {
      const title = f?.title || '未命名';
      const tex = f?.tex || '';
      return `<li><span class="formula-title">${title}：</span><span class="formula-tex">${tex}</span></li>`;
    }).join('');
    return [
      '<div class="formula-block">',
      '<b>数学公式：</b>',
      `<ul class="formula-list">${items}</ul>`,
      '</div>'
    ].join('');
  }

  function blockToken(label, value) {
    if (value === undefined || value === null || value === '') return `<span class="ml-block">${label}</span>`;
    return `<span class="ml-block">${label}<span class="ml-block-num">${value}</span></span>`;
  }

  function travelParallelSummary(starter) {
    const list = starter?.travelParallel;
    if (!Array.isArray(list) || !list.length) return '';
    const pair = list.map((item) => `${item.robot || 'A'}:${item.cm ?? 0}cm`).join('，');
    return `<div class="ml-example-line">双车并行：${pair}</div>`;
  }

  function renderStarterBlocks(task) {
    const s = task?.starter;
    if (!s) return '<div class="ml-starter"><b>积木示意：</b>无 starter 示例</div>';

    const chain = [];
    if (s.speed != null) chain.push(blockToken('设置速度', `${s.speed} cm/s`));
    if (s.forward != null) chain.push(blockToken('前进', `${s.forward} cm`));
    if (s.backward != null) chain.push(blockToken('后退', `${s.backward} cm`));
    if (s.turn != null) chain.push(blockToken('右转', `${s.turn}°`));
    if (s.wait != null) chain.push(blockToken('等待', `${s.wait} s`));
    if (s.speed2 != null) chain.push(blockToken('设置速度', `${s.speed2} cm/s`));
    if (s.forward2 != null) chain.push(blockToken('前进', `${s.forward2} cm`));
    if (s.turn2 != null) chain.push(blockToken('右转', `${s.turn2}°`));
    if (s.speed3 != null) chain.push(blockToken('设置速度', `${s.speed3} cm/s`));
    if (s.forward3 != null) chain.push(blockToken('前进', `${s.forward3} cm`));
    if (s.extraForward != null) chain.push(blockToken('前进', `${s.extraForward} cm`));

    if (s.repeat != null && s.forward != null && s.turn != null) {
      chain.length = 0;
      chain.push(`<span class="ml-block ml-repeat">重复 ${s.repeat} 次</span>`);
      chain.push(blockToken('前进', `${s.forward} cm`));
      chain.push(blockToken('右转', `${s.turn}°`));
    } else if (s.repeat != null && s.forward != null) {
      chain.length = 0;
      chain.push(`<span class="ml-block ml-repeat">重复 ${s.repeat} 次</span>`);
      chain.push(blockToken('前进', `${s.forward} cm`));
    }

    if (Array.isArray(s.turns) && s.turns.length) {
      chain.length = 0;
      s.turns.forEach((t) => {
        const dir = t.dir === 'left' ? '左转' : '右转';
        chain.push(blockToken(dir, `${t.deg}°`));
      });
    }

    if (s.goto) {
      chain.length = 0;
      const points = Array.isArray(s.goto) ? s.goto : [s.goto];
      points.forEach((p) => chain.push(blockToken('移动到', `(${p.x ?? 0}, ${p.y ?? 0})`)));
    }

    if (s.move2d) {
      chain.length = 0;
      const steps = Array.isArray(s.move2d) ? s.move2d : [s.move2d];
      steps.forEach((m) => chain.push(blockToken('向角度移动', `${m.angle ?? 0}°, ${m.dist ?? 0}cm`)));
    }

    if ('travelParallel' in s) {
      chain.length = 0;
      chain.push('<span class="ml-block ml-dual">双车并行 · A 前进</span>');
      chain.push('<span class="ml-block ml-dual">双车并行 · B 前进</span>');
    }

    if (s.travelDelayStart) {
      const d = s.travelDelayStart;
      chain.length = 0;
      chain.push('<span class="ml-block ml-dual">A 程序 · 前进</span>');
      if (d.waitSec != null) chain.push(blockToken('B 等待', `${d.waitSec} s`));
      chain.push('<span class="ml-block ml-dual">B 程序 · 前进</span>');
    }

    if (s.curveTravelRun) {
      chain.length = 0;
      chain.push('<span class="ml-block ml-dual">A · 曲线拦截演示</span>');
      chain.push('<span class="ml-block ml-dual">B · （可自定义 goto）</span>');
    }

    const flow = chain.length
      ? chain.map((item, i) => `${item}${i < chain.length - 1 ? '<span class="ml-arrow">→</span>' : ''}`).join('')
      : '<span class="ml-empty">该任务暂无可视化积木链</span>';

    const concreteExamples = [];
    if (s.forward != null) {
      concreteExamples.push(`示例：拖入“前进”积木，填入 ${s.forward}，点击运行。`);
    }
    if (s.repeat != null && s.forward != null && s.turn != null) {
      concreteExamples.push(`示例：重复 ${s.repeat} 次：前进 ${s.forward} cm，右转 ${s.turn}°。`);
    }
    if (s.goto) {
      const p = Array.isArray(s.goto) ? s.goto[0] : s.goto;
      concreteExamples.push(`示例：用“移动到 x y”先到 (${p.x ?? 0}, ${p.y ?? 0})。`);
    }
    if (s.move2d) {
      const m = Array.isArray(s.move2d) ? s.move2d[0] : s.move2d;
      concreteExamples.push(`示例：用“向角度移动”，角度 ${m.angle ?? 0}°，距离 ${m.dist ?? 0} cm。`);
    }
    if ('travelParallel' in s) {
      concreteExamples.push('示例：在「双车并行」的 A/B 槽分别拖入「小车 A/B 前进」，两车同时运动。');
    }
    if (s.travelDelayStart) {
      concreteExamples.push('示例：A 槽写前进，B 槽先等待再前进，表示延迟出发。');
    }
    if (s.curveTravelRun) {
      concreteExamples.push('示例：A 槽使用「曲线拦截演示」；B 槽可写等待 + goto 至交汇点。');
    }

    return [
      '<div class="ml-starter">',
      '<b>积木示意：</b>',
      `<div class="ml-chain">${flow}</div>`,
      travelParallelSummary(s),
      concreteExamples.length
        ? `<div class="ml-example-line">${concreteExamples.join(' ')}</div>`
        : '<div class="ml-example-line">示例：可点击“加载示例程序”直接观察默认积木链。</div>',
      '<b class="ml-code-title">代码示例：</b>',
      `<pre class="ml-code"><code>${escapeHtml(renderStarterCode(s))}</code></pre>`,
      '</div>'
    ].join('');
  }

  function renderStarterCode(s) {
    if (!s) return '// 无 starter 示例';

    if ('travelParallel' in s) {
      return [
        'await __runRobotsParallel(',
        '  async () => { await __robotA.forward(dA); },',
        '  async () => { await __robotB.forward(dB); }',
        ');'
      ].join('\n');
    }

    if (s.travelDelayStart) {
      const w = s.travelDelayStart.waitSec ?? 2;
      return [
        'await __runRobotsParallel(',
        '  async () => { await __robotA.forward(dA); },',
        `  async () => { await __robotB.wait(${w}); await __robotB.forward(dB); }`,
        ');'
      ].join('\n');
    }

    if (s.curveTravelRun) {
      return [
        'await __runRobotsParallel(',
        "  async () => { await __curveTravelRun('meet'); },",
        '  async () => { /* B 槽自定义 */ }',
        ');'
      ].join('\n');
    }

    if (s.goto) {
      const points = Array.isArray(s.goto) ? s.goto : [s.goto];
      return [
        'start();',
        ...points.map((p) => `gotoXY(${p.x ?? 0}, ${p.y ?? 0});`),
        'stop();'
      ].join('\n');
    }

    if (s.move2d) {
      const steps = Array.isArray(s.move2d) ? s.move2d : [s.move2d];
      return [
        'start();',
        ...steps.map((m) => `moveAt(${m.angle ?? 0}, ${m.dist ?? 0});`),
        'stop();'
      ].join('\n');
    }

    if (Array.isArray(s.turns) && s.turns.length) {
      return [
        'start();',
        ...s.turns.map((t) => `${t.dir === 'left' ? 'turnLeft' : 'turnRight'}(${t.deg});`),
        'stop();'
      ].join('\n');
    }

    if (s.repeat != null && s.forward != null && s.turn != null) {
      return [
        'start();',
        `repeat(${s.repeat}) {`,
        `  forward(${s.forward});`,
        `  turnRight(${s.turn});`,
        '}',
        'stop();'
      ].join('\n');
    }

    if (s.repeat != null && s.forward != null) {
      return [
        'start();',
        `repeat(${s.repeat}) {`,
        `  forward(${s.forward});`,
        '}',
        'stop();'
      ].join('\n');
    }

    const lines = ['start();'];
    if (s.speed != null) lines.push(`setSpeed(${s.speed});`);
    if (s.forward != null) lines.push(`forward(${s.forward});`);
    if (s.backward != null) lines.push(`backward(${s.backward});`);
    if (s.turn != null) lines.push(`turnRight(${s.turn});`);
    if (s.wait != null) lines.push(`wait(${s.wait});`);
    if (s.speed2 != null) lines.push(`setSpeed(${s.speed2});`);
    if (s.forward2 != null) lines.push(`forward(${s.forward2});`);
    if (s.turn2 != null) lines.push(`turnRight(${s.turn2});`);
    if (s.speed3 != null) lines.push(`setSpeed(${s.speed3});`);
    if (s.forward3 != null) lines.push(`forward(${s.forward3});`);
    if (s.extraForward != null) lines.push(`forward(${s.extraForward});`);
    lines.push('stop();');
    return lines.join('\n');
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function renderMathIfNeeded() {
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
      window.MathJax.typesetPromise().catch(() => {});
    }
  }

  async function openVolume(id) {
    state.activeVolumeId = id;
    if (!state.volumeById.has(id)) {
      const all = [...state.index.stageVolumes, ...state.index.subjectVolumes];
      const meta = all.find((v) => v.id === id);
      if (!meta) return;
      const volume = await getJson(`./data/manuals/${meta.id}.json`);
      state.volumeById.set(id, volume);
    }
    const volume = state.volumeById.get(id);
    renderSummary(volume);
    renderToc(volume);
    renderTasks(volume);
    renderMathIfNeeded();
  }

  async function init() {
    const params = new URLSearchParams(window.location.search);
    state.isEmbedded = params.get('embed') === '1';
    if (state.isEmbedded) {
      document.body.classList.add('embed-mode');
    }
    const index = await getJson('./data/manuals/index.json');
    state.index = index;
    qs('generatedAt').textContent = formatGeneratedAt(index.generatedAt);
    const firstVolume = index.stageVolumes[0] || index.subjectVolumes[0];
    if (!firstVolume) return;
    await openVolume(firstVolume.id);
    renderVolumeList();
  }

  init().catch((err) => {
    qs('volumeSummary').innerHTML = `<h2>加载失败</h2><p>${err.message}</p>`;
  });
})();
