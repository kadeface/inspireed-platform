'use strict';

function resolveToolboxLevel(task, stageKey) {
  if (task?.toolboxLevel === 'L1' || task?.toolboxLevel === 'L2') return task.toolboxLevel;
  if (stageKey === 'primary' || stageKey === 'travel') return 'L1';
  return 'L2';
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resolveToolboxLevel };
}
if (typeof window !== 'undefined') {
  window.resolveToolboxLevel = resolveToolboxLevel;
}
