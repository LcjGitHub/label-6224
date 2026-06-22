<script setup>
import { h, onMounted, ref, computed } from 'vue'
import {
  NButton,
  NCard,
  NDataTable,
  NSpace,
  NStatistic,
  useMessage,
} from 'naive-ui'
import { fetchRepairStats } from '../api/stats'

const emit = defineEmits(['navigate'])

const message = useMessage()

const stats = ref(null)
const loading = ref(false)

const formattedDuration = computed(() => {
  if (!stats.value) return ''
  const total = stats.value.total_duration_minutes
  if (total < 60) return `${total} 分钟`
  const hours = Math.floor(total / 60)
  const minutes = total % 60
  if (minutes === 0) return `${hours} 小时`
  return `${hours} 小时 ${minutes} 分钟`
})

const recurredRatePercent = computed(() => {
  if (!stats.value) return ''
  return (stats.value.recurred_rate * 100).toFixed(1) + '%'
})

const monthlyColumns = [
  {
    title: '月份',
    key: 'month',
    width: 160,
  },
  {
    title: '维修次数',
    key: 'count',
    width: 160,
    render: (row) => `${row.count} 次`,
  },
]

async function loadStats() {
  loading.value = true
  try {
    const { data } = await fetchRepairStats()
    stats.value = data
  } catch {
    message.error('加载统计数据失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>维修统计概览</h1>
        <p class="subtitle">查看维修记录的汇总数据和月度趋势</p>
      </div>
      <n-space>
        <n-button @click="emit('navigate', 'records')">返回维修记录</n-button>
      </n-space>
    </header>

    <div class="stats-cards">
      <n-card :bordered="false" class="stat-card" :loading="loading">
        <n-statistic label="维修总次数" :value="stats?.total_count" />
      </n-card>
      <n-card :bordered="false" class="stat-card" :loading="loading">
        <n-statistic label="累计耗时" :value="formattedDuration" />
      </n-card>
      <n-card :bordered="false" class="stat-card" :loading="loading">
        <n-statistic label="复发次数" :value="stats?.recurred_count" />
      </n-card>
      <n-card :bordered="false" class="stat-card" :loading="loading">
        <n-statistic label="复发占比" :value="recurredRatePercent" />
      </n-card>
    </div>

    <n-card title="月度维修次数" :bordered="false" class="table-card">
      <n-data-table
        :columns="monthlyColumns"
        :data="stats?.monthly_stats ?? []"
        :loading="loading"
        :bordered="false"
        striped
        size="small"
      >
        <template #empty>
          <div class="empty-tip">暂无月度维修数据</div>
        </template>
      </n-data-table>
    </n-card>
  </div>
</template>

<style scoped>
.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 32px 20px 48px;
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0 0 6px;
  font-size: 1.75rem;
  font-weight: 700;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.table-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.empty-tip {
  padding: 32px 0;
  color: #9ca3af;
  text-align: center;
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
