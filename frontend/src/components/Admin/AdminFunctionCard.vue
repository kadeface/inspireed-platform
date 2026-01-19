<template>
  <el-card
    class="admin-function-card"
    :class="[
      { 'is-active': active },
      { 'is-business': isBusiness },
      customClass
    ]"
    shadow="hover"
    @click="$emit('click')"
  >
    <div class="card-body">
      <div 
        class="card-icon" 
        :style="{ backgroundColor: iconBgColor }"
      >
        <el-icon :size="iconSize" :color="iconColor">
          <component :is="icon" />
        </el-icon>
      </div>
      
      <div class="card-content">
        <h3 class="card-title">{{ title }}</h3>
        <p class="card-description">{{ description }}</p>
        
        <div v-if="$slots.footer || stats" class="card-footer mt-2">
          <slot name="footer">
            <el-tag v-if="stats" size="small" type="info" class="stats-tag">
              {{ stats }}
            </el-tag>
          </slot>
        </div>
      </div>

      <el-icon v-if="isBusiness" class="arrow-icon">
        <ArrowRight />
      </el-icon>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'

interface Props {
  title: string
  description: string
  icon: any
  iconColor?: string
  iconBgColor?: string
  iconSize?: number
  active?: boolean
  isBusiness?: boolean
  stats?: string | number
  customClass?: string
}

withDefaults(defineProps<Props>(), {
  iconColor: '#409eff',
  iconBgColor: '#eff6ff',
  iconSize: 32,
  active: false,
  isBusiness: false
})

defineEmits(['click'])
</script>

<style scoped>
.admin-function-card {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  position: relative;
  height: 100%;
}

.admin-function-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #bfdbfe;
}

.admin-function-card.is-active {
  border: 2px solid #3b82f6;
  background-color: #f8faff;
}

.admin-function-card.is-business {
  border-left-width: 4px;
}

.card-body {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 4px 0;
  font-size: 17px;
  font-weight: 600;
  color: #1e293b;
}

.card-description {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
}

.stats-tag {
  background-color: #f1f5f9;
  border-color: #e2e8f0;
  color: #64748b;
}

.arrow-icon {
  color: #94a3b8;
  font-size: 18px;
  opacity: 0;
  transition: all 0.3s;
  transform: translateX(-10px);
}

.admin-function-card:hover .arrow-icon {
  opacity: 1;
  transform: translateX(0);
}

@media (max-width: 768px) {
  .card-icon {
    width: 48px;
    height: 48px;
  }
}
</style>
