# ModuleCard Component

Professional module preview card with enhanced information density and visual hierarchy.

## Features

- **Metadata badges**: Difficulty level and duration indicators
- **Progress tracking**: Circular progress ring showing completion percentage
- **Enhanced interactivity**: Hover effects with quick action buttons
- **Responsive design**: Adapts to desktop, tablet, and mobile layouts
- **Accessibility**: Keyboard navigation and screen reader support
- **Professional education styling**: Clear visual hierarchy and color coding

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| cell | Cell | required | Module data object with enhanced fields |
| index | number | required | Module index in list (0-based) |
| isActive | boolean | false | Whether this module is currently selected |
| loading | boolean | false | Whether module is in loading state |
| isMultiSelectMode | boolean | false | Whether in multi-select mode |
| isActivityActive | boolean | false | Whether this is the currently active activity |

## Cell Interface (Enhanced)

```typescript
interface CellBase {
  id: number | string
  type: CellType
  order: number
  title?: string

  // Enhanced fields (optional)
  preview?: string        // Short description (~60 chars)
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
  duration?: number        // Estimated duration in minutes
  progress?: number        // Completion percentage (0-100)
}
```

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| click | (cell, index) | Card clicked - activate this module |
| checkbox-click | (cell, index, event) | Checkbox clicked - for multi-select |
| checkbox-change | (cell, index, event) | Checkbox changed state |
| preview | (cell, index) | Preview button clicked (TODO: implement) |
| edit | (cell, index) | Edit button clicked (TODO: implement) |

## Usage

### Basic Usage

```vue
<ModuleCard
  :cell="{
    id: 1,
    type: 'VIDEO',
    title: 'Introduction to Physics',
    preview: 'Learn the fundamentals of motion and forces',
    difficulty: 'beginner',
    duration: 15,
    progress: 75,
    order: 0
  }"
  :index="0"
  :isActive="true"
  @click="handleModuleClick"
/>
```

### With All Props

```vue
<ModuleCard
  :cell="currentModule"
  :index="moduleIndex"
  :isActive="selectedModule === moduleIndex"
  :loading="isSwitchingModule"
  :isMultiSelectMode="batchMode"
  :isActivityActive="currentActivityId === cell.id"
  @click="selectModule"
  @checkbox-click="toggleCheckbox"
  @checkbox-change="updateSelection"
  @preview="showPreview"
  @edit="openEditor"
/>
```

### In a List

```vue
<div class="module-list">
  <ModuleCard
    v-for="(cell, index) in cells"
    :key="cell.id || index"
    v-memo="[isModuleActive(cell, index), loading, cell.id]"
    :cell="cell"
    :index="index"
    :is-active="isModuleActive(cell, index)"
    :loading="loading"
    @click="handleModuleClick"
  />
</div>
```

## Module Types and Color Themes

| Type | Theme Color | Icon | Use Case |
|------|-------------|------|----------|
| TEXT | Orange (#F59E0B) | 📄 | Text content, reading material |
| VIDEO | Blue (#3B82F6) | 🎥 | Video lessons, recordings |
| CODE | Green (#10B981) | 💻 | Code examples, exercises |
| ACTIVITY | Purple (#A855F7) | 🎯 | Quizzes, assignments, interactions |
| FLOWCHART | Indigo (#6366F1) | 📊 | Diagrams, flowcharts |
| BROWSER | Cyan (#06B6D4) | 🌐 | Embedded websites, iframes |
| INTERACTIVE | Purple (#A855F7) | 🎮 | Interactive content, simulations |

## Visual States

### Default State
- White background
- Gray border (#E5E7EB)
- Subtle shadow
- Module number in top-left corner
- Metadata badges at top
- Icon, title, and preview text
- Progress ring and status at bottom

### Hover State
- Lifts 4px upward
- Enhanced shadow
- Border brightens (type-specific color)
- Action buttons fade in (preview 👁️, edit ✏️)

### Active State
- Solid color background (type-specific)
- White text
- White module number badge
- Icon scales up 1.1x
- Strong shadow
- Transformed scale(1.02)

### Loading State
- Reduced opacity (0.6)
- Disabled cursor
- No interactions

### Disabled State
- Same as loading state
- Grayed out appearance

## Progress States

| Progress | Status Text | Ring Display |
|----------|-------------|--------------|
| 0% | 待开始 | Empty ring (gray) |
| 1-99% | 进行中 X% | Partial fill (type color) |
| 100% | 已完成 | Full ring (type color) |

## Difficulty Levels

| Level | Icon | Color | Label |
|-------|------|-------|-------|
| beginner | 🟢 | Green background | 入门 |
| intermediate | 🟡 | Yellow background | 中级 |
| advanced | 🔴 | Red background | 高级 |

## Responsive Breakpoints

### Desktop (>1024px)
- Grid: 3 columns minimum
- Card: min-width 200px, min-height 110px
- Action buttons: hover only

### Tablet (768-1024px)
- Grid: 2 columns minimum
- Card: min-width 180px, min-height 100px
- Action buttons: hover only

### Mobile (<768px)
- Grid: 1 column
- Card: Full width, min-height 100px
- Action buttons: always visible
- Compact font sizes

## Accessibility

### Keyboard Navigation
- **Tab**: Focus moves between cards
- **Enter/Space**: Activate focused card
- **Arrow Keys**: Navigate in grid (if implemented)

### ARIA Labels
- Card: `"{index}. {title} - {type} ({status})"`
- Difficulty: `"难度: {level}"`
- Duration: `"预计时长: {minutes}分钟"`
- Buttons: Descriptive labels

### Screen Reader Support
- Role: `button` (entire card)
- Live regions: Progress updates
- State announcements: Active/loading changes

## Performance Considerations

### v-memo Directive
Use `v-memo` to optimize re-renders in large lists:

```vue
<ModuleCard
  v-for="(cell, index) in cells"
  v-memo="[isModuleActive(cell, index), loading, cell.id]"
  ...
/>
```

### Virtualization
For lists with >20 modules, consider using `vue-virtual-scroller`.

### Image Lazy Loading
If cards contain thumbnails:

```vue
<img :src="thumbnail" loading="lazy" :alt="cell.title" />
```

## Styling Customization

### CSS Variables (Future Enhancement)

```css
:root {
  --module-card-min-height: 110px;
  --module-card-border-radius: 8px;
  --module-card-transition: 0.3s ease-out;
}
```

### Override Styles

```vue
<style scoped>
.module-list :deep(.module-card) {
  /* Custom styles */
}
</style>
```

## Integration Examples

### With ModuleList Component

```vue
<ModuleList
  :cells="lessonCells"
  :currentModuleIndex="currentIndex"
  :loading="isLoading"
  @item-click="handleModuleChange"
/>
```

### With TeacherControlPanel

```vue
<div class="teaching-modules-floating">
  <ModuleList
    :cells="lessonContentCells"
    :currentModuleIndex="currentModuleIndex"
    @item-click="handleModuleItemClick"
  />
</div>
```

## Future Enhancements

- [ ] Implement preview modal functionality
- [ ] Implement edit functionality
- [ ] Add drag-and-drop reordering
- [ ] Support custom themes and color schemes
- [ ] Add analytics tracking for interactions
- [ ] Support keyboard navigation within grid
- [ ] Add bulk operations (select all, delete selected)
- [ ] Add difficulty filtering
- [ ] Add duration filtering

## Testing

```vue
<script setup lang="ts">
import ModuleCard from './ModuleCard.vue'
import { ref } from 'vue'

const mockCell = {
  id: 1,
  type: 'TEXT',
  title: 'Test Module',
  preview: 'This is a test module',
  difficulty: 'beginner' as const,
  duration: 10,
  progress: 50,
  order: 0
}

function handleClick(cell: Cell, index: number) {
  console.log('Clicked:', cell, index)
}
</script>

<template>
  <ModuleCard
    :cell="mockCell"
    :index="0"
    :isActive="true"
    @click="handleClick"
  />
</template>
```

## Related Components

- **DifficultyBadge**: Displays difficulty level
- **DurationBadge**: Displays duration
- **ProgressRing**: Displays completion percentage
- **CellTypeIcon**: Displays type-specific icon
- **ModuleList**: Container for multiple ModuleCard instances

## Migration Guide

### From Old Module Items

**Before:**
```vue
<div class="module-item" @click="handleClick">
  <div class="module-item-number">{{ index + 1 }}</div>
  <div class="module-item-icon">...</div>
  <div class="module-item-title">{{ title }}</div>
</div>
```

**After:**
```vue
<ModuleCard
  :cell="{ title, type, preview, difficulty, duration, progress }"
  :index="index"
  @click="handleClick"
/>
```

### Backward Compatibility

All new Cell fields are optional. Existing code continues to work:

```typescript
// Old Cell (still works)
{ id: 1, type: 'TEXT', title: 'Old Module', order: 0 }

// New Cell (enhanced)
{
  id: 1,
  type: 'TEXT',
  title: 'New Module',
  order: 0,
  preview: 'Enhanced with metadata',
  difficulty: 'beginner',
  duration: 5,
  progress: 100
}
```

## Changelog

### v1.0.0 (2026-04-08)
- Initial release
- Basic card layout with metadata badges
- Progress tracking with circular indicator
- Responsive design for all screen sizes
- Accessibility support
- Performance optimizations (v-memo)

## License

Part of the InspireEd Platform project.
