<script setup>
import { h, onMounted, ref } from 'vue'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NCard,
  NDataTable,
  NDatePicker,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NModal,
  NSpace,
  NSwitch,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import {
  createRecord,
  deleteRecord,
  fetchRecords,
  updateRecord,
} from '../api/records'

const message = useMessage()
const dialog = useDialog()

const records = ref([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref(null)

const emptyForm = () => ({
  description: '',
  repair_date: Date.now(),
  tools: '',
  duration_minutes: 30,
  recurred: false,
})

const form = ref(emptyForm())

/**
 * 将时间戳格式化为 YYYY-MM-DD
 * @param {number} timestamp
 * @returns {string}
 */
function toDateString(timestamp) {
  return format(timestamp, 'yyyy-MM-dd')
}

/**
 * 格式化表格中的日期显示
 * @param {string} dateStr
 * @returns {string}
 */
function formatDisplayDate(dateStr) {
  try {
    return format(parseISO(dateStr), 'yyyy-MM-dd')
  } catch {
    return dateStr
  }
}

/**
 * 加载维修记录列表
 */
async function loadRecords() {
  loading.value = true
  try {
    const { data } = await fetchRecords()
    records.value = data
  } catch {
    message.error('加载记录失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}

/**
 * 打开新建表单
 */
function openCreate() {
  editingId.value = null
  form.value = emptyForm()
  showModal.value = true
}

/**
 * 打开编辑表单
 * @param {object} row
 */
function openEdit(row) {
  editingId.value = row.id
  form.value = {
    description: row.description,
    repair_date: parseISO(row.repair_date).getTime(),
    tools: row.tools,
    duration_minutes: row.duration_minutes,
    recurred: row.recurred,
  }
  showModal.value = true
}

/**
 * 提交表单（新建或更新）
 */
async function handleSubmit() {
  if (!form.value.description.trim()) {
    message.warning('请填写问题描述')
    return
  }

  const payload = {
    description: form.value.description.trim(),
    repair_date: toDateString(form.value.repair_date),
    tools: form.value.tools.trim(),
    duration_minutes: form.value.duration_minutes ?? 0,
    recurred: form.value.recurred,
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateRecord(editingId.value, payload)
      message.success('已更新记录')
    } else {
      await createRecord(payload)
      message.success('已添加记录')
    }
    showModal.value = false
    await loadRecords()
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 确认删除记录
 * @param {object} row
 */
function confirmDelete(row) {
  dialog.warning({
    title: '删除确认',
    content: `确定删除「${row.description.slice(0, 30)}${row.description.length > 30 ? '…' : ''}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteRecord(row.id)
        message.success('已删除')
        await loadRecords()
      } catch {
        message.error('删除失败')
      }
    },
  })
}

const columns = [
  {
    title: '日期',
    key: 'repair_date',
    width: 120,
    render: (row) => formatDisplayDate(row.repair_date),
  },
  {
    title: '问题描述',
    key: 'description',
    ellipsis: { tooltip: true },
  },
  {
    title: '工具',
    key: 'tools',
    width: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: '耗时',
    key: 'duration_minutes',
    width: 90,
    render: (row) => `${row.duration_minutes} 分钟`,
  },
  {
    title: '复发',
    key: 'recurred',
    width: 80,
    render: (row) =>
      h(
        NTag,
        { type: row.recurred ? 'warning' : 'success', size: 'small', bordered: false },
        { default: () => (row.recurred ? '是' : '否') },
      ),
  },
  {
    title: '操作',
    key: 'actions',
    width: 140,
    render: (row) =>
      h(NSpace, { size: 'small' }, {
        default: () => [
          h(
            NButton,
            { size: 'small', onClick: () => openEdit(row) },
            { default: () => '编辑' },
          ),
          h(
            NButton,
            { size: 'small', type: 'error', ghost: true, onClick: () => confirmDelete(row) },
            { default: () => '删除' },
          ),
        ],
      }),
  },
]

onMounted(loadRecords)
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>家庭 DIY 维修小记</h1>
        <p class="subtitle">记录每一次动手维修，方便回顾与追踪复发问题</p>
      </div>
      <n-button type="primary" @click="openCreate">新增记录</n-button>
    </header>

    <n-card title="维修记录" :bordered="false" class="table-card">
      <n-data-table
        :columns="columns"
        :data="records"
        :loading="loading"
        :bordered="false"
        striped
        size="small"
      />
    </n-card>

    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="editingId ? '编辑维修记录' : '新增维修记录'"
      style="width: 520px"
      :mask-closable="false"
    >
      <n-form label-placement="top">
        <n-form-item label="问题描述" required>
          <n-input
            v-model:value="form.description"
            type="textarea"
            placeholder="例如：厨房水龙头滴水，更换阀芯"
            :rows="3"
          />
        </n-form-item>
        <n-form-item label="维修日期" required>
          <n-date-picker
            v-model:value="form.repair_date"
            type="date"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="使用工具">
          <n-input
            v-model:value="form.tools"
            placeholder="活动扳手、螺丝刀…"
          />
        </n-form-item>
        <n-form-item label="耗时（分钟）">
          <n-input-number
            v-model:value="form.duration_minutes"
            :min="0"
            :step="5"
            style="width: 100%"
          />
        </n-form-item>
        <n-form-item label="是否复发">
          <n-switch v-model:value="form.recurred" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleSubmit">
            保存
          </n-button>
        </n-space>
      </template>
    </n-modal>
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

.table-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
</style>
