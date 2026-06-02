#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';

const rootDir = path.resolve(process.cwd(), 'frontend/public/mathlab');
const curriculumPath = path.join(rootDir, 'js/curriculum.js');
const outputJsonDir = path.join(rootDir, 'data/manuals');
const outputMdDir = path.join(rootDir, 'manuals');

const stageOrder = ['primary', 'junior'];
const subjectOrder = ['travel', 'funcGraph', 'calculus'];
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
  calculus: '微积分专题册'
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
  await fs.writeFile(path.join(outputMdDir, 'README.md'), [
    '# MathLab 学生活动实验手册索引',
    '',
    `生成时间：${index.generatedAt}`,
    '',
    '## 学段主册',
    ...index.stageVolumes.map((v) => `- ${v.title}（${v.taskCount} 课）`),
    '',
    '## 专题册',
    ...index.subjectVolumes.map((v) => `- ${v.title}（${v.taskCount} 课）`),
    ''
  ].join('\n'), 'utf8');

  process.stdout.write(`Generated ${volumes.length} manuals.\n`);
}

main().catch((err) => {
  process.stderr.write(`${err.stack || err.message}\n`);
  process.exit(1);
});
