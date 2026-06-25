#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const curriculumPath = path.join(rootDir, 'js/curriculum.js');
const outputJsonDir = path.join(rootDir, 'data/manuals');
const outputMdDir = path.join(rootDir, 'manuals');

const stageOrder = ['primary', 'junior'];
const subjectOrder = ['travel', 'funcGraph', 'pathPlan', 'calculus'];
const gradeOrderByStage = {
  primary: ['2', '3', '4', '5', '6'],
  junior: ['7u', '7d', '8u', '8d', '9u', '9d']
};

const stageDisplayName = {
  primary: '小学阶段',
  junior: '初中阶段'
};

const subjectDisplayName = {
  travel: '行程问题专题册',
  funcGraph: '函数图像专题册',
  pathPlan: '路径规划专题册',
  calculus: '微积分专题册'
};

const subjectIntroNotes = {
  travel: [
    '',
    '## 双车并行说明',
    '',
    '本专题任务使用 **「当程序开始时（双车并行）」** 入口：在 **A 程序** / **B 程序** 槽分别编写甲、乙两车逻辑，运行后同时执行。',
    '简单相向/同向场景可用「同时 A/B 前进」积木；**延迟出发**请在 B 槽使用「等待」后再前进。',
    ''
  ],
  pathPlan: [
    '',
    '## 双车并行说明',
    '',
    '路径规划任务同样使用双槽入口：A 槽可放「曲线拦截演示」或沿曲线 goto；B 槽可放等待 + 直线 goto 至交汇点。',
    '**相距同步**：「小车 B 等待直到与 A 相距小于 ε cm」——仅阻塞 B，A 可继续沿曲线运动。',
    '拦截的关键是 **同时到达同一点**，勿将 A 的全部 goto 复制给 B。',
    ''
  ]
};

function safeJson(value) {
  return JSON.stringify(value, null, 2);
}

async function loadCurriculum(filePath) {
  const source = await fs.readFile(filePath, 'utf8');
  const sandbox = {
    window: {},
    console
  };
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox, { filename: filePath });
  if (!sandbox.window.CURRICULUM) {
    throw new Error('CURRICULUM not found in curriculum.js');
  }
  return sandbox.window.CURRICULUM;
}

function normalizeTask(stageKey, gradeKey, gradeName, task) {
  return {
    id: task.id,
    title: task.title,
    unit: task.unit || '',
    stageKey,
    gradeKey,
    gradeName,
    scene: task.scene || '',
    tags: task.tags || [],
    goals: task.goals || [],
    focus: task.focus || '',
    challenges: task.challenges || [],
    hint: task.hint || '',
    formulas: task.formulas || [],
    sceneConfig: task.sceneConfig || {},
    starter: task.starter || null,
    demo: task.demo || null
  };
}

function normalizeTaskFull(stageKey, gradeKey, gradeName, task) {
  return { ...task, stageKey, gradeKey, gradeName };
}

function isEmptyValue(value) {
  if (value == null) return true;
  if (Array.isArray(value) && value.length === 0) return true;
  if (typeof value === 'object' && !Array.isArray(value) && Object.keys(value).length === 0) {
    return true;
  }
  return false;
}

function mdJsonBlock(label, value) {
  if (isEmptyValue(value)) return [];
  return [`- **\`${label}\`**：`, '```json', safeJson(value), '```', ''];
}

const MERGED_SCALAR_FIELDS = [
  ['id', '任务 ID', true],
  ['stageKey', '学段键', true],
  ['gradeKey', '章节键', true],
  ['gradeName', '章节名', false],
  ['unit', '单元', false],
  ['scene', '场景', true],
  ['mode', 'mode', true],
  ['travelSubtype', 'travelSubtype', true],
  ['series', 'series', true],
  ['level', 'level', true],
  ['focus', '教学聚焦', false],
  ['hint', '提示', false],
  ['demo', 'demo', true]
];

const MERGED_ARRAY_FIELDS = [
  ['tags', '标签'],
  ['goals', '教学目标'],
  ['challenges', '挑战任务']
];

const MERGED_OBJECT_FIELDS = ['sceneConfig', 'starter', 'plotValidate', 'calcValidate'];

function renderTaskFullMarkdown(task, headingPrefix) {
  const lines = [`${headingPrefix} ${task.title}`, ''];
  const rendered = new Set(['title']);

  for (const [key, label, code] of MERGED_SCALAR_FIELDS) {
    rendered.add(key);
    const value = task[key];
    if (value == null || value === '') continue;
    lines.push(code ? `- ${label}：\`${value}\`` : `- ${label}：${value}`);
  }

  for (const [key, label] of MERGED_ARRAY_FIELDS) {
    rendered.add(key);
    if (task[key]?.length) {
      lines.push(`- ${label}：`);
      lines.push(mdList(task[key]));
    }
  }

  rendered.add('formulas');
  if (task.formulas?.length) {
    lines.push('- 数学公式：');
    lines.push(mdFormulas(task.formulas));
  }

  for (const key of MERGED_OBJECT_FIELDS) {
    rendered.add(key);
    lines.push(...mdJsonBlock(key, task[key]));
  }

  for (const key of Object.keys(task).sort()) {
    if (rendered.has(key)) continue;
    const value = task[key];
    if (isEmptyValue(value)) continue;
    if (typeof value === 'object') {
      lines.push(...mdJsonBlock(key, value));
    } else {
      lines.push(`- ${key}：${value}`);
    }
  }

  lines.push('---', '');
  return lines.join('\n');
}

function buildStageSectionsFull(curriculum, stageKey) {
  const stage = curriculum[stageKey];
  const grades = stage?.grades || {};
  const gradeKeys = sortGradeKeys(stageKey, Object.keys(grades));
  return gradeKeys.map((gradeKey) => {
    const grade = grades[gradeKey];
    const tasks = (grade.tasks || []).map((t) => normalizeTaskFull(stageKey, gradeKey, grade.name, t));
    return {
      gradeKey,
      gradeName: grade.name,
      taskCount: tasks.length,
      tasks
    };
  });
}

function buildSubjectSectionsFull(curriculum, subjectKey) {
  const subject = curriculum[subjectKey];
  const grades = subject?.grades || {};
  const levelKeys = sortLevelKeys(Object.keys(grades));
  return levelKeys.map((levelKey) => {
    const level = grades[levelKey];
    const tasks = (level.tasks || []).map((t) => normalizeTaskFull(subjectKey, levelKey, level.name, t));
    return {
      levelKey,
      levelName: level.name,
      taskCount: tasks.length,
      tasks
    };
  });
}

function buildMergedVolume(curriculum) {
  const stageParts = stageOrder.map((stageKey) => {
    const sections = buildStageSectionsFull(curriculum, stageKey);
    return {
      type: 'stage',
      stageKey,
      partTitle: stageDisplayName[stageKey] || curriculum[stageKey]?.name,
      stageName: curriculum[stageKey]?.name,
      sections,
      taskCount: sections.reduce((sum, s) => sum + s.taskCount, 0)
    };
  });

  const subjectParts = subjectOrder.map((subjectKey) => {
    const sections = buildSubjectSectionsFull(curriculum, subjectKey);
    return {
      type: 'subject',
      subjectKey,
      partTitle: subjectDisplayName[subjectKey] || curriculum[subjectKey]?.name,
      stageName: curriculum[subjectKey]?.name,
      sections,
      taskCount: sections.reduce((sum, s) => sum + s.taskCount, 0)
    };
  });

  const taskCount = stageParts.reduce((sum, p) => sum + p.taskCount, 0)
    + subjectParts.reduce((sum, p) => sum + p.taskCount, 0);

  return {
    generatedAt: new Date().toISOString(),
    sourceFile: 'js/curriculum.js',
    taskCount,
    stageParts,
    subjectParts
  };
}

const partOrdinal = ['一', '二', '三'];

function renderMergedMarkdown(merged) {
  const lines = [
    '# 轮式机器人数学融合教案（合并版）',
    '',
    '## 元信息',
    `- 生成时间：${merged.generatedAt}`,
    `- 总任务数：${merged.taskCount}`,
    `- 数据来源：\`${merged.sourceFile}\``,
    '- 使用方式：按学段/专题查阅章节，任务 ID 可与 MathLab 页面联动（`?task=…`）。',
    '',
    '## 目录',
    ''
  ];

  merged.stageParts.forEach((part, partIdx) => {
    lines.push(`### 第${partOrdinal[partIdx]}部分 ${part.partTitle}`);
    part.sections.forEach((section, idx) => {
      lines.push(`- ${idx + 1}. ${section.gradeName}（${section.taskCount} 课）`);
    });
    lines.push('');
  });

  lines.push('### 第三部分 专题课程');
  merged.subjectParts.forEach((part) => {
    lines.push(`- ${part.stageName}（${part.taskCount} 课）`);
  });
  lines.push('');

  merged.stageParts.forEach((part, partIdx) => {
    lines.push('', `## 第${partOrdinal[partIdx]}部分 ${part.partTitle}`, '');
    part.sections.forEach((section, chIdx) => {
      lines.push(`### 第${chIdx + 1}章 ${section.gradeName}`, '');
      section.tasks.forEach((task, tIdx) => {
        lines.push(renderTaskFullMarkdown(task, `#### ${chIdx + 1}.${tIdx + 1}`));
      });
    });
  });

  lines.push('', '## 第三部分 专题课程', '');
  merged.subjectParts.forEach((part) => {
    lines.push(`### ${part.stageName}`, '');
    if (subjectIntroNotes[part.subjectKey]) {
      lines.push(...subjectIntroNotes[part.subjectKey]);
    }
    part.sections.forEach((section, chIdx) => {
      lines.push(`#### 第${chIdx + 1}章 ${section.levelName}`, '');
      section.tasks.forEach((task, tIdx) => {
        lines.push(renderTaskFullMarkdown(task, `##### ${chIdx + 1}.${tIdx + 1}`));
      });
    });
  });

  return lines.join('\n');
}

function sortGradeKeys(stageKey, keys) {
  const preferred = gradeOrderByStage[stageKey] || [];
  return [...keys].sort((a, b) => {
    const ia = preferred.indexOf(a);
    const ib = preferred.indexOf(b);
    if (ia >= 0 && ib >= 0) return ia - ib;
    if (ia >= 0) return -1;
    if (ib >= 0) return 1;
    return a.localeCompare(b, 'zh-Hans-CN');
  });
}

function sortLevelKeys(keys) {
  return [...keys].sort((a, b) => {
    const ai = Number.parseInt(a.replace(/[^0-9]/g, ''), 10);
    const bi = Number.parseInt(b.replace(/[^0-9]/g, ''), 10);
    if (!Number.isNaN(ai) && !Number.isNaN(bi) && ai !== bi) return ai - bi;
    return a.localeCompare(b, 'zh-Hans-CN');
  });
}

function buildStageVolume(curriculum, stageKey) {
  const stage = curriculum[stageKey];
  const grades = stage?.grades || {};
  const gradeKeys = sortGradeKeys(stageKey, Object.keys(grades));
  const sections = gradeKeys.map((gradeKey) => {
    const grade = grades[gradeKey];
    const tasks = (grade.tasks || []).map((t) => normalizeTask(stageKey, gradeKey, grade.name, t));
    return {
      gradeKey,
      gradeName: grade.name,
      taskCount: tasks.length,
      tasks
    };
  });

  return {
    id: `stage-${stageKey}`,
    type: 'stage',
    stageKey,
    title: `${stageDisplayName[stageKey] || stage.name}学生活动实验手册`,
    stageName: stage.name,
    taskCount: sections.reduce((sum, s) => sum + s.taskCount, 0),
    sectionLabel: '年级',
    sections
  };
}

function buildSubjectVolume(curriculum, subjectKey) {
  const subject = curriculum[subjectKey];
  const grades = subject?.grades || {};
  const levelKeys = sortLevelKeys(Object.keys(grades));
  const sections = levelKeys.map((levelKey) => {
    const level = grades[levelKey];
    const tasks = (level.tasks || []).map((t) => normalizeTask(subjectKey, levelKey, level.name, t));
    return {
      levelKey,
      levelName: level.name,
      taskCount: tasks.length,
      tasks
    };
  });
  return {
    id: `subject-${subjectKey}`,
    type: 'subject',
    subjectKey,
    title: subjectDisplayName[subjectKey] || `${subject.name}专题册`,
    stageName: subject.name,
    taskCount: sections.reduce((sum, s) => sum + s.taskCount, 0),
    sectionLabel: '层级',
    sections
  };
}

function mdList(items, fallback = '无') {
  if (!items || !items.length) return fallback;
  return items.map((item) => `- ${item}`).join('\n');
}

function mdFormulas(formulas) {
  if (!formulas || !formulas.length) return '无';
  return formulas.map((f) => `- ${f.title}: ${f.tex}`).join('\n');
}

function renderVolumeMarkdown(volume) {
  const intro = [
    '# ' + volume.title,
    '',
    '## 册前说明',
    `- 手册类型：${volume.type === 'stage' ? '学段主册' : '专题册'}`,
    `- 总任务数：${volume.taskCount}`,
    '- 使用方式：按目录选择章节，再逐项开展实验任务。',
    '- 任务编码：保留原始任务 ID，便于与 MathLab 页面联动。'
  ];
  if (volume.type === 'subject' && subjectIntroNotes[volume.subjectKey]) {
    intro.push(...subjectIntroNotes[volume.subjectKey]);
  }

  const toc = ['## 目录'];
  volume.sections.forEach((section, idx) => {
    const sectionName = section.gradeName || section.levelName;
    toc.push(`- ${idx + 1}. ${sectionName}（${section.taskCount} 课）`);
  });

  const chapters = [];
  volume.sections.forEach((section, idx) => {
    const sectionName = section.gradeName || section.levelName;
    chapters.push('', `## 第${idx + 1}章 ${sectionName}`, '');
    section.tasks.forEach((task, taskIndex) => {
      chapters.push(`### ${idx + 1}.${taskIndex + 1} ${task.title}`);
      chapters.push(`- 任务 ID：\`${task.id}\``);
      chapters.push(`- 单元：${task.unit || '未标注'}`);
      chapters.push(`- 场景：\`${task.scene || 'path'}\``);
      chapters.push(`- 标签：${task.tags?.length ? task.tags.join('、') : '无'}`);
      chapters.push(`- 教学聚焦：${task.focus || '无'}`);
      chapters.push('- 教学目标：');
      chapters.push(mdList(task.goals));
      chapters.push('- 挑战任务：');
      chapters.push(mdList(task.challenges));
      chapters.push('- 数学公式：');
      chapters.push(mdFormulas(task.formulas));
      chapters.push(`- 提示：${task.hint || '无'}`);
      chapters.push('---');
    });
  });

  return [...intro, '', ...toc, ...chapters, ''].join('\n');
}

async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
}

async function writeVolumeOutputs(volume) {
  const baseName = volume.id;
  const jsonPath = path.join(outputJsonDir, `${baseName}.json`);
  const mdPath = path.join(outputMdDir, `${baseName}.md`);
  await fs.writeFile(jsonPath, safeJson(volume), 'utf8');
  await fs.writeFile(mdPath, renderVolumeMarkdown(volume), 'utf8');
}

async function main() {
  const curriculum = await loadCurriculum(curriculumPath);
  await ensureDir(outputJsonDir);
  await ensureDir(outputMdDir);

  const stageVolumes = stageOrder.map((key) => buildStageVolume(curriculum, key));
  const subjectVolumes = subjectOrder.map((key) => buildSubjectVolume(curriculum, key));
  const volumes = [...stageVolumes, ...subjectVolumes];

  for (const volume of volumes) {
    await writeVolumeOutputs(volume);
  }

  const index = {
    generatedAt: new Date().toISOString(),
    stageVolumes: stageVolumes.map((v) => ({
      id: v.id,
      title: v.title,
      stageName: v.stageName,
      taskCount: v.taskCount,
      sectionCount: v.sections.length,
      path: `./${v.id}.json`
    })),
    subjectVolumes: subjectVolumes.map((v) => ({
      id: v.id,
      title: v.title,
      stageName: v.stageName,
      taskCount: v.taskCount,
      sectionCount: v.sections.length,
      path: `./${v.id}.json`
    }))
  };

  await fs.writeFile(path.join(outputJsonDir, 'index.json'), safeJson(index), 'utf8');

  const merged = buildMergedVolume(curriculum);
  const mergedMdPath = path.join(outputMdDir, 'curriculum-merged.md');
  await fs.writeFile(mergedMdPath, renderMergedMarkdown(merged), 'utf8');

  await fs.writeFile(path.join(outputMdDir, 'README.md'), [
    '# MathLab 学生活动实验手册索引',
    '',
    `生成时间：${index.generatedAt}`,
    '',
    '## 合并总册',
    `- [轮式机器人数学融合教案（合并版）](./curriculum-merged.md)（${merged.taskCount} 课，完整字段镜像）`,
    '',
    '## 学段主册',
    ...index.stageVolumes.map((v) => `- ${v.title}（${v.taskCount} 课）`),
    '',
    '## 专题册',
    ...index.subjectVolumes.map((v) => `- ${v.title}（${v.taskCount} 课）`),
    ''
  ].join('\n'), 'utf8');

  process.stdout.write(`Generated ${volumes.length} manuals + merged curriculum (${merged.taskCount} tasks).\n`);
}

main().catch((err) => {
  process.stderr.write(`${err.stack || err.message}\n`);
  process.exit(1);
});
