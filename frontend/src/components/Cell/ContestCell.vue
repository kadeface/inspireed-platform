<template>
  <div class="contest-cell cell-container p-4">
    <h3 class="text-2xl font-bold mb-2">{{ cell.content.title }}</h3>
    <p class="text-gray-600 mb-4">{{ cell.content.description }}</p>

    <div v-if="cell.content.leaderboard" class="leaderboard">
      <h4 class="text-lg font-semibold mb-3">排行榜</h4>
      <div class="overflow-x-auto">
        <table class="min-w-full border">
          <thead class="bg-gray-100">
            <tr>
              <th class="px-4 py-2 text-left">排名</th>
              <th class="px-4 py-2 text-left">用户ID</th>
              <th class="px-4 py-2 text-right">分数</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in cell.content.leaderboard"
              :key="entry.userId"
              class="border-t"
            >
              <td class="px-4 py-2">
                <span
                  class="inline-flex items-center justify-center w-8 h-8 rounded-full"
                  :class="{
                    'bg-yellow-400 text-white': entry.rank === 1,
                    'bg-gray-400 text-white': entry.rank === 2,
                    'bg-orange-400 text-white': entry.rank === 3,
                  }"
                >
                  {{ entry.rank }}
                </span>
              </td>
              <td class="px-4 py-2">User {{ entry.userId }}</td>
              <td class="px-4 py-2 text-right font-semibold">{{ entry.score }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <p class="text-sm text-gray-500 mt-4">竞技任务功能开发中...</p>
  </div>
</template>

<script setup lang="ts">
import type { ContestCell as ContestCellType } from '../../types/cell'

interface Props {
  cell: ContestCellType
  editable?: boolean
}

defineProps<Props>()
</script>

