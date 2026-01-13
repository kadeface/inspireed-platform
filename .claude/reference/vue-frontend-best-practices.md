# Vue Frontend Best Practices Reference

A concise reference guide for building modern Vue applications with Vite and Tailwind CSS.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Component Design](#2-component-design)
3. [State Management](#3-state-management)
4. [Data Fetching](#4-data-fetching)
5. [Forms & Validation](#5-forms--validation)
6. [Styling with Tailwind](#6-styling-with-tailwind)
7. [Performance](#7-performance)
8. [Composition API Patterns](#8-composition-api-patterns)
9. [Routing](#9-routing)
10. [Error Handling](#10-error-handling)
11. [Testing](#11-testing)
12. [Accessibility](#12-accessibility)
13. [Anti-Patterns](#13-anti-patterns)

---

## 1. Project Structure

### Feature-Based Structure (Recommended)

```
src/
├── features/
│   ├── habits/
│   │   ├── components/
│   │   │   ├── HabitCard.vue
│   │   │   ├── HabitForm.vue
│   │   │   └── HabitList.vue
│   │   ├── composables/
│   │   │   └── useHabits.js
│   │   ├── api/
│   │   │   └── habits.js
│   │   └── index.js           # Public exports
│   └── calendar/
│       ├── components/
│       ├── composables/
│       └── index.js
├── components/                 # Shared/common components
│   ├── ui/
│   │   ├── Button.vue
│   │   ├── Card.vue
│   │   └── Modal.vue
│   └── layout/
│       ├── Header.vue
│       └── Layout.vue
├── composables/                # Shared composables
│   └── useLocalStorage.js
├── stores/                     # Pinia stores
│   ├── habits.js
│   └── ui.js
├── lib/                        # Utilities
│   ├── api.js                  # API client
│   └── utils.js
├── views/                      # Route views
│   ├── Dashboard.vue
│   └── HabitDetail.vue
├── App.vue
├── main.js
└── style.css
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `HabitCard.vue` |
| Composables | camelCase, `use` prefix | `useHabits.js` |
| Utilities | camelCase | `formatDate.js` |
| Constants | SCREAMING_SNAKE_CASE | `API_BASE_URL` |
| CSS/styles | kebab-case | `habit-card.css` |

### Barrel Exports

```javascript
// features/habits/index.js
export { default as HabitCard } from './components/HabitCard.vue';
export { default as HabitForm } from './components/HabitForm.vue';
export { useHabits } from './composables/useHabits';

// Usage elsewhere
import { HabitCard, useHabits } from '@/features/habits';
```

**Note**: Barrel exports can hurt tree-shaking and build times in large projects. Use judiciously.

---

## 2. Component Design

### Single File Components (SFC)

```vue
<!-- Simple component -->
<script setup>
const props = defineProps({
  habit: {
    type: Object,
    required: true
  },
  showStreak: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['complete']);
</script>

<template>
  <div class="p-4 border rounded">
    <h3>{{ habit.name }}</h3>
    <button @click="emit('complete', habit.id)">Complete</button>
  </div>
</template>
```

### Component Composition

```vue
<!-- Compound components pattern -->
<!-- Card.vue -->
<script setup>
defineProps({
  className: {
    type: String,
    default: ''
  }
});
</script>

<template>
  <div :class="`border rounded ${className}`">
    <slot />
  </div>
</template>

<!-- Usage -->
<Card class="p-4">
  <template #header>
    <div class="p-4 border-b font-bold">Habit Details</div>
  </template>
  <div class="p-4">Content here</div>
</Card>
```

### Props Design

```vue
<!-- Prefer specific props over spreading -->
<!-- Good -->
<script setup>
const props = defineProps({
  onClick: Function,
  disabled: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'primary'
  }
});
</script>

<!-- Accept class for styling flexibility -->
<script setup>
const props = defineProps({
  className: {
    type: String,
    default: ''
  }
});
</script>

<template>
  <div :class="`base-styles ${className}`">
    <slot />
  </div>
</template>
```

### Slots Pattern

```vue
<!-- Named slots for composition -->
<!-- Layout.vue -->
<script setup>
// No props needed
</script>

<template>
  <div class="container mx-auto">
    <Header />
    <main>
      <slot />
    </main>
    <Footer />
  </div>
</template>

<!-- Scoped slots for more control -->
<!-- HabitList.vue -->
<script setup>
const props = defineProps({
  habits: {
    type: Array,
    required: true
  }
});
</script>

<template>
  <ul>
    <li v-for="habit in habits" :key="habit.id">
      <slot name="item" :habit="habit" />
    </li>
  </ul>
</template>

<!-- Usage -->
<HabitList :habits="habits">
  <template #item="{ habit }">
    <HabitCard :habit="habit" />
  </template>
</HabitList>
```

---

## 3. State Management

### When to Use What

| State Type | Solution |
|------------|----------|
| Server/async data | @tanstack/vue-query |
| Form state | VeeValidate or reactive |
| Local UI state | ref/reactive |
| Shared UI state | Pinia stores |
| URL state | Vue Router |

### ref vs reactive

```javascript
import { ref, reactive } from 'vue';

// ref - for primitives and objects that need reactivity wrapper
const name = ref('');
const count = ref(0);
const habit = ref({ name: '', description: '' });

// reactive - for objects, no .value needed
const habit = reactive({
  name: '',
  description: ''
});

// computed - derived state
const fullName = computed(() => `${firstName.value} ${lastName.value}`);
```

### Lifting State Up

```vue
<!-- Parent owns the state, children receive via props -->
<!-- Dashboard.vue -->
<script setup>
import { ref } from 'vue';
import DatePicker from './DatePicker.vue';
import HabitList from './HabitList.vue';
import Stats from './Stats.vue';

const selectedDate = ref(new Date());
</script>

<template>
  <DatePicker v-model="selectedDate" />
  <HabitList :date="selectedDate" />
  <Stats :date="selectedDate" />
</template>
```

### Provide/Inject

```javascript
// Parent - provide values
// HabitsProvider.vue
<script setup>
import { provide, ref } from 'vue';

const habits = ref([]);

function addHabit(habit) {
  habits.value.push(habit);
}

function removeHabit(id) {
  habits.value = habits.value.filter(h => h.id !== id);
}

provide('habits', {
  habits,
  addHabit,
  removeHabit
});
</script>

<template>
  <slot />
</template>

// Child - inject values
// HabitList.vue
<script setup>
import { inject } from 'vue';

const { habits, removeHabit } = inject('habits');
</script>

<template>
  <div v-for="habit in habits" :key="habit.id">
    {{ habit.name }}
    <button @click="removeHabit(habit.id)">Delete</button>
  </div>
</template>
```

### Pinia (Recommended for State)

```javascript
// stores/habits.js
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useHabitStore = defineStore('habits', () => {
  const selectedHabitId = ref(null);
  const filterStatus = ref('all');

  function setSelectedHabit(id) {
    selectedHabitId.value = id;
  }

  function setFilter(status) {
    filterStatus.value = status;
  }

  return {
    selectedHabitId,
    filterStatus,
    setSelectedHabit,
    setFilter
  };
});

// Usage in component
<script setup>
import { useHabitStore } from '@/stores/habits';

const habitStore = useHabitStore();
</script>

<template>
  <button @click="habitStore.setFilter('all')">
    All Habits
  </button>
</template>
```

---

## 4. Data Fetching

### TanStack Vue Query Setup

```javascript
// main.js
import { createApp } from 'vue';
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

const app = createApp(App);
app.use(VueQueryPlugin, { queryClient });
app.mount('#app');
```

### Basic Query

```javascript
// composables/useHabits.js
import { useQuery } from '@tanstack/vue-query';
import { fetchHabits } from '../api/habits';

export function useHabits() {
  return useQuery({
    queryKey: ['habits'],
    queryFn: fetchHabits,
  });
}

// Usage in component
<script setup>
import { useHabits } from '@/composables/useHabits';

const { data: habits, isLoading, error } = useHabits();
</script>

<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <ul v-else>
    <li v-for="habit in habits" :key="habit.id">
      <HabitCard :habit="habit" />
    </li>
  </ul>
</template>
```

### Query with Parameters

```javascript
export function useHabit(habitId) {
  return useQuery({
    queryKey: ['habits', habitId],
    queryFn: () => fetchHabit(habitId),
    enabled: () => !!habitId.value,
  });
}

export function useCompletions(habitId, month) {
  return useQuery({
    queryKey: ['completions', habitId, month],
    queryFn: () => fetchCompletions(habitId.value, month.value),
    enabled: computed(() => !!habitId.value && !!month.value),
  });
}
```

### Mutations

```javascript
import { useMutation, useQueryClient } from '@tanstack/vue-query';

export function useCreateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}

export function useCompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ habitId, date }) => completeHabit(habitId, date),
    onSuccess: (_, { habitId }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['completions', habitId] });
    },
  });
}

// Usage
<script setup>
const props = defineProps(['habit']);

const { mutate: complete, isPending } = useCompleteHabit();

function handleComplete() {
  complete({ habitId: props.habit.id, date: new Date().toISOString() });
}
</script>

<template>
  <button @click="handleComplete" :disabled="isPending">
    {{ isPending ? 'Saving...' : 'Complete' }}
  </button>
</template>
```

### Optimistic Updates

```javascript
export function useCompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: completeHabit,
    onMutate: async ({ habitId }) => {
      await queryClient.cancelQueries({ queryKey: ['habits'] });

      const previousHabits = queryClient.getQueryData(['habits']);

      queryClient.setQueryData(['habits'], (old) =>
        old.map(h => h.id === habitId
          ? { ...h, completedToday: true, currentStreak: h.currentStreak + 1 }
          : h
        )
      );

      return { previousHabits };
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['habits'], context.previousHabits);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}
```

### API Client

```javascript
// lib/api.js
const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'An error occurred');
  }

  if (response.status === 204) return null;
  return response.json();
}

// api/habits.js
export const fetchHabits = () => request('/habits');
export const fetchHabit = (id) => request(`/habits/${id}`);
export const createHabit = (data) => request('/habits', { method: 'POST', body: JSON.stringify(data) });
export const completeHabit = (id, date) => request(`/habits/${id}/complete`, { method: 'POST', body: JSON.stringify({ date }) });
```

---

## 5. Forms & Validation

### VeeValidate + Zod

```vue
<script setup>
import { useForm, Field } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { z } from 'zod';

const habitSchema = toTypedSchema(z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid color').default('#10B981'),
}));

const { handleSubmit, isSubmitting, resetForm } = useForm({
  validationSchema: habitSchema,
});

const onSubmit = handleSubmit(async (values) => {
  await createHabit(values);
  resetForm();
});
</script>

<template>
  <form @submit="onSubmit">
    <div>
      <label for="name">Name</label>
      <Field name="name" as="input" id="name" class="border rounded" />
      <ErrorMessage name="name" class="text-red-500" />
    </div>

    <div>
      <label for="description">Description</label>
      <Field name="description" as="textarea" id="description" />
      <ErrorMessage name="description" class="text-red-500" />
    </div>

    <button type="submit" :disabled="isSubmitting">
      {{ isSubmitting ? 'Saving...' : 'Save' }}
    </button>
  </form>
</template>
```

### Simple Reactive Form

```vue
<script setup>
import { ref } from 'vue';

const name = ref('');
const error = ref('');

function handleSubmit() {
  if (!name.value.trim()) {
    error.value = 'Name is required';
    return;
  }
  emit('submit', { name: name.value });
  name.value = '';
  error.value = '';
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <input
      v-model="name"
      placeholder="Habit name"
      class="border rounded"
    />
    <span v-if="error" class="text-red-500">{{ error }}</span>
    <button type="submit">Add</button>
  </form>
</template>
```

---

## 6. Styling with Tailwind

### Vite Configuration

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
});

// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: '#10B981',
      },
    },
  },
  plugins: [],
};

// src/style.css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Component Styling Patterns

```vue
<!-- Using dynamic classes -->
<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'primary'
  }
});

const baseClasses = 'px-4 py-2 rounded font-medium transition-colors';
const variantClasses = {
  primary: 'bg-primary text-white hover:bg-primary/90',
  secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
  danger: 'bg-red-500 text-white hover:bg-red-600',
};
</script>

<template>
  <button :class="`${baseClasses} ${variantClasses[variant]}`">
    <slot />
  </button>
</template>

<!-- Using computed classes -->
<script setup>
import { computed } from 'vue';

const props = defineProps({
  habit: Object,
  isCompleted: Boolean
});

const cardClasses = computed(() => [
  'p-4 border rounded',
  props.isCompleted ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
]);
</script>

<template>
  <div :class="cardClasses">
    {{ habit.name }}
  </div>
</template>
```

### Responsive Design

```vue
<!-- Mobile-first approach -->
<template>
  <div class="
    p-2 md:p-4 lg:p-6
    grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4
    text-sm md:text-base
  ">
    <!-- Content -->
  </div>
</template>

<!-- Breakpoints: sm(640px) md(768px) lg(1024px) xl(1280px) 2xl(1536px) -->
```

### Common Patterns

```vue
<!-- Card -->
<div class="bg-white rounded-lg shadow-md p-4">

<!-- Flex centering -->
<div class="flex items-center justify-center">

<!-- Grid layout -->
<div class="grid grid-cols-7 gap-1">

<!-- Truncate text -->
<p class="truncate">Long text...</p>

<!-- Focus ring -->
<button class="focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">

<!-- Disabled state -->
<button class="disabled:opacity-50 disabled:cursor-not-allowed" :disabled="isPending">
```

---

## 7. Performance

### Computed Properties

```vue
<script setup>
import { computed } from 'vue';

const props = defineProps({
  items: Array
});

// Computed for derived state - cached until dependencies change
const expensiveValue = computed(() => {
  return calculateExpensiveValue(props.items);
});

const filteredItems = computed(() => {
  return props.items.filter(item => item.active);
});
</script>
```

### watch vs watchEffect

```javascript
import { ref, watch, watchEffect } from 'vue';

// watch - specific dependencies, access previous value
const count = ref(0);

watch(count, (newValue, oldValue) => {
  console.log(`Count changed from ${oldValue} to ${newValue}`);
});

// watchEffect - auto-track dependencies
watchEffect(() => {
  console.log(`Count is: ${count.value}`);
});
```

### Async Components

```vue
<!-- Lazy load components -->
<script setup>
import { defineAsyncComponent } from 'vue';

const Settings = defineAsyncComponent(() => import('./views/Settings.vue'));
const Analytics = defineAsyncComponent(() => import('./views/Analytics.vue'));
</script>

<template>
  <Suspense>
    <template #default>
      <Settings v-if="currentView === 'settings'" />
      <Analytics v-else-if="currentView === 'analytics'" />
    </template>
    <template #fallback>
      <div>Loading...</div>
    </template>
  </Suspense>
</template>
```

### v-memo

```vue
<script setup>
const props = defineProps({
  item: Object
});
</script>

<template>
  <!-- Only re-renders if item.id or item.status changes -->
  <div v-memo="[item.id, item.status]">
    {{ item.name }}
  </div>
</template>
```

### Virtual Scrolling

```vue
<!-- For very long lists, use vue-virtual-scroller -->
<script setup>
import { RecycleScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';

const props = defineProps({
  items: Array
});
</script>

<template>
  <RecycleScroller
    class="scroller"
    :items="items"
    :item-size="50"
    key-field="id"
  >
    <template #default="{ item }">
      <div class="item">{{ item.name }}</div>
    </template>
  </RecycleScroller>
</template>

<style>
.scroller {
  height: 400px;
}
</style>
```

---

## 8. Composition API Patterns

### Composables (Custom Hooks)

```javascript
// composables/useLocalStorage.js
import { ref, watch } from 'vue';

export function useLocalStorage(key, initialValue) {
  const value = ref(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  watch(value, (newValue) => {
    localStorage.setItem(key, JSON.stringify(newValue));
  }, { deep: true });

  return value;
}

// composables/useDebounce.js
import { ref, watch } from 'vue';

export function useDebounce(value, delay) {
  const debouncedValue = ref(value.value);

  watch(value, (newValue) => {
    const timer = setTimeout(() => {
      debouncedValue.value = newValue;
    }, delay);

    return () => clearTimeout(timer);
  }, { immediate: true });

  return debouncedValue;
}

// composables/useToggle.js
import { ref } from 'vue';

export function useToggle(initialValue = false) {
  const value = ref(initialValue);
  const toggle = () => value.value = !value.value;
  return { value, toggle };
}
```

### Lifecycle Hooks

```vue
<script setup>
import { onMounted, onUnmounted, onUpdated } from 'vue';

onMounted(() => {
  console.log('Component mounted');
  fetchInitialData();
});

onUnmounted(() => {
  console.log('Component unmounted');
  cleanup();
});

onUpdated(() => {
  console.log('Component updated');
});
</script>
```

### Watch Patterns

```javascript
// Cleanup function
watch(source, async (newVal) => {
  const controller = new AbortController();

  try {
    const data = await fetch('/api/data', { signal: controller.signal });
  } catch (err) {
    if (err.name !== 'AbortError') {
      console.error(err);
    }
  }

  return () => controller.abort();
});

// Event listeners
watch(() => someCondition, (isActive) => {
  if (isActive) {
    window.addEventListener('resize', handleResize);
  } else {
    window.removeEventListener('resize', handleResize);
  }
});

// Sync with external system
watchEffect((onCleanup) => {
  const subscription = externalStore.subscribe(setData);
  onCleanup(() => subscription.unsubscribe());
});
```

### Common Pitfalls

```javascript
// BAD: Losing reactivity by destructuring reactive objects
const state = reactive({ count: 0 });
const { count } = state; // count is NOT reactive

// GOOD: Use toRefs or access directly
const { count } = toRefs(state); // count is reactive

// BAD: Replacing reactive object entirely
const state = reactive({ items: [] });
state = { items: [] }; // Loses reactivity

// GOOD: Modify properties
state.items = [];

// BAD: Modifying props directly
const props = defineProps(['habit']);
props.habit.name = 'new name'; // Avoid this

// GOOD: Emit event to parent
const emit = defineEmits(['update']);
emit('update', { ...props.habit, name: 'new name' });
```

---

## 9. Routing

### Vue Router Setup

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Layout from '@/components/layout/Layout.vue';
import Dashboard from '@/views/Dashboard.vue';
import HabitDetail from '@/views/HabitDetail.vue';
import Settings from '@/views/Settings.vue';
import NotFound from '@/views/NotFound.vue';

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', component: Dashboard },
      { path: 'habits/:habitId', component: HabitDetail },
      { path: 'settings', component: Settings },
    ],
  },
  { path: '/:pathMatch(.*)*', component: NotFound },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

// main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);
app.mount('#app');
```

### Layout Route

```vue
<!-- Layout.vue -->
<script setup>
import { RouterView, RouterLink } from 'vue-router';
</script>

<template>
  <div class="min-h-screen">
    <nav class="bg-white shadow">
      <RouterLink to="/">Dashboard</RouterLink>
      <RouterLink to="/settings">Settings</RouterLink>
    </nav>
    <main class="container mx-auto p-4">
      <RouterView />
    </main>
  </div>
</template>
```

### Route Parameters

```vue
<!-- HabitDetail.vue -->
<script setup>
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();
const router = useRouter();

const habitId = computed(() => route.params.habitId);

const month = computed(() => route.query.month || getCurrentMonth());

function goBack() {
  router.back();
}

function nextMonth() {
  router.push({ query: { month: 'next' } });
}
</script>

<template>
  <div>
    <button @click="goBack">Back</button>
    <button @click="nextMonth">Next Month</button>
  </div>
</template>
```

### Navigation

```vue
<script setup>
import { useRouter, RouterLink, RouterLinkActive } from 'vue-router';

const router = useRouter();

function goToSettings() {
  router.push('/settings');
}

function goBack() {
  router.back();
}

function replaceHome() {
  router.replace('/');
}
</script>

<template>
  <!-- Simple link -->
  <RouterLink to="/settings">Settings</RouterLink>

  <!-- Active styling -->
  <RouterLink
    to="/"
    custom
    v-slot="{ href, navigate, isActive }"
  >
    <a
      :href="href"
      @click="navigate"
      :class="isActive ? 'text-primary' : 'text-gray-600'"
    >
      Dashboard
    </a>
  </RouterLink>

  <!-- Programmatic navigation -->
  <button @click="goToSettings">Settings</button>
</template>
```

---

## 10. Error Handling

### Error Boundary Component

```vue
<!-- ErrorBoundary.vue -->
<script setup>
import { ref, onErrorCaptured } from 'vue';

const error = ref(null);

onErrorCaptured((err) => {
  error.value = err;
  console.error('Error caught:', err);
  // Send to error tracking service
  return false; // Prevent error from propagating
});

function reset() {
  error.value = null;
}
</script>

<template>
  <div v-if="error" class="p-4 text-red-500">
    <h2>Something went wrong</h2>
    <p>{{ error.message }}</p>
    <button @click="reset">Try again</button>
  </div>
  <slot v-else />
</template>

<!-- Usage -->
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### Async Error Handling

```vue
<script setup>
import { useHabits } from '@/composables/useHabits';

const { data: habits, error, isError, refetch } = useHabits();
</script>

<template>
  <div v-if="isError" class="p-4 bg-red-50 text-red-700 rounded">
    <p>Failed to load habits: {{ error.message }}</p>
    <button @click="refetch">Retry</button>
  </div>
  <ul v-else-if="habits">
    <li v-for="habit in habits" :key="habit.id">
      {{ habit.name }}
    </li>
  </ul>
</template>
```

### Toast Notifications

```vue
<!-- Using vue-toastification -->
<script setup>
import { useToast } from 'vue-toastification';

const toast = useToast();

function useCreateHabit() {
  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      toast.success('Habit created!');
    },
    onError: (error) => {
      toast.error(`Failed: ${error.message}`);
    },
  });
}
</script>
```

---

## 11. Testing

### Setup with Vitest

```javascript
// vite.config.js
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
});

// src/test/setup.js
import '@testing-library/jest-dom';
```

### Component Testing

```javascript
// HabitCard.test.js
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import HabitCard from '@/components/HabitCard.vue';

describe('HabitCard', () => {
  it('renders habit name', () => {
    const wrapper = mount(HabitCard, {
      props: {
        habit: { id: 1, name: 'Exercise' }
      }
    });

    expect(wrapper.text()).toContain('Exercise');
  });

  it('emits complete event when button clicked', async () => {
    const wrapper = mount(HabitCard, {
      props: {
        habit: { id: 1, name: 'Exercise' }
      }
    });

    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('complete')).toBeTruthy();
    expect(wrapper.emitted('complete')[0]).toEqual([1]);
  });
});
```

### Testing with Composables

```javascript
import { describe, it, expect } from 'vitest';
import { useHabits } from '@/composables/useHabits';
import { setActivePinia, createPinia } from 'pinia';
import { useQueryClient } from '@tanstack/vue-query';

describe('useHabits', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('loads and displays habits', async () => {
    const queryClient = useQueryClient();
    queryClient.setQueryData(['habits'], [
      { id: 1, name: 'Exercise' },
    ]);

    const { data } = useHabits();

    expect(data.value).toHaveLength(1);
    expect(data.value[0].name).toBe('Exercise');
  });
});
```

### Mocking API Calls

```javascript
import { describe, it, expect, vi } from 'vitest';
import * as api from '@/api/habits';

vi.mock('@/api/habits');

it('loads and displays habits', async () => {
  api.fetchHabits.mockResolvedValue([
    { id: 1, name: 'Exercise' },
  ]);

  const { data } = useHabits();

  await new Promise(resolve => setTimeout(resolve, 0));

  expect(data.value).toHaveLength(1);
  expect(data.value[0].name).toBe('Exercise');
});
```

---

## 12. Accessibility

### Semantic HTML

```vue
<template>
  <!-- Use semantic elements -->
  <header>...</header>
  <nav>...</nav>
  <main>...</main>
  <article>...</article>
  <aside>...</aside>
  <footer>...</footer>

  <!-- Use headings properly (h1 > h2 > h3) -->
  <h1>Dashboard</h1>
  <section>
    <h2>Today's Habits</h2>
  </section>
</template>
```

### ARIA Attributes

```vue
<template>
  <!-- Labels -->
  <button aria-label="Close modal">×</button>

  <!-- Live regions (for dynamic content) -->
  <div aria-live="polite" aria-atomic="true">
    {{ statusMessage }}
  </div>

  <!-- States -->
  <button :aria-pressed="isCompleted">Complete</button>
  <button :aria-expanded="isOpen">Menu</button>

  <!-- Roles -->
  <div role="alert">{{ errorMessage }}</div>
</template>
```

### Focus Management

```vue
<script setup>
import { ref, watch } from 'vue';

const props = defineProps(['isOpen']);
const modalRef = ref(null);

watch(() => props.isOpen, (isOpen) => {
  if (isOpen && modalRef.value) {
    modalRef.value.focus();
  }
});

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    emit('close');
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    ref="modalRef"
    tabindex="-1"
    role="dialog"
    aria-modal="true"
    @keydown="handleKeyDown"
  >
    <slot />
  </div>
</template>
```

### Keyboard Navigation

```vue
<script setup>
const props = defineProps(['item']);
const emit = defineEmits(['select']);

function handleKeyDown(event) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    emit('select');
  }
}
</script>

<template>
  <div
    role="button"
    tabindex="0"
    @click="emit('select')"
    @keydown="handleKeyDown"
  >
    {{ item.name }}
  </div>
</template>
```

---

## 13. Anti-Patterns

### Common Mistakes

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Prop drilling | Hard to maintain | Provide/inject or Pinia |
| Huge components | Hard to test/maintain | Split into smaller components |
| watch for derived state | Unnecessary complexity | Use computed |
| Index as key | Bugs with reordering | Use stable unique IDs |
| Direct DOM manipulation | Conflicts with Vue | Use refs sparingly |

### Code Examples

```vue
<!-- BAD: Derived state in watch -->
<script setup>
import { ref, watch } from 'vue';

const firstName = ref('');
const lastName = ref('');
const fullName = ref('');

watch([firstName, lastName], () => {
  fullName.value = `${firstName.value} ${lastName.value}`;
});
</script>

<!-- GOOD: Use computed -->
<script setup>
import { ref, computed } from 'vue';

const firstName = ref('');
const lastName = ref('');

const fullName = computed(() => `${firstName.value} ${lastName.value}`);
</script>

<!-- BAD: Index as key (causes bugs when list changes) -->
<template>
  <div v-for="(item, index) in items" :key="index">
    {{ item.name }}
  </div>
</template>

<!-- GOOD: Stable unique ID -->
<template>
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</template>

<!-- BAD: Fetching in onMounted without cleanup -->
<script setup>
import { onMounted, ref } from 'vue';

const data = ref(null);

onMounted(() => {
  fetch('/api/data').then(res => res.json()).then(d => data.value = d);
});
</script>

<!-- GOOD: Use Vue Query or add cleanup -->
<script setup>
import { onMounted, onUnmounted, ref } from 'vue';

let cancelled = false;

onMounted(() => {
  fetch('/api/data')
    .then(res => res.json())
    .then(d => { if (!cancelled) data.value = d; });
});

onUnmounted(() => {
  cancelled = true;
});
</script>
```

---

## Quick Reference

### Common Imports

```javascript
// Vue
import { ref, reactive, computed, watch, watchEffect, onMounted, onUnmounted, onUpdated, nextTick, provide, inject, toRefs } from 'vue';

// Vue Router
import { RouterView, RouterLink, useRoute, useRouter, createRouter, createWebHistory } from 'vue-router';

// Pinia
import { defineStore } from 'pinia';
import { createPinia } from 'pinia';

// TanStack Vue Query
import { useQuery, useMutation, useQueryClient, VueQueryPlugin } from '@tanstack/vue-query';

// Form validation
import { useForm, Field, ErrorMessage } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { z } from 'zod';
```

---

## Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)
- [TanStack Vue Query](https://tanstack.com/query/latest/docs/vue/overview)
- [Vite](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [VeeValidate](https://vee-validate.logaretm.com/)
- [Zod](https://zod.dev/)
