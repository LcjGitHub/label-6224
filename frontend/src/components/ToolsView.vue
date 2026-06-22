<script setup>
import { h, onMounted, ref } from 'vue'
import {
  NButton,
  NCard,
  NDataTable,
  NForm,
  NFormItem,
  NInput,
  NModal,
  NSpace,
  useDialog,
  useMessage,
} from 'naive-ui'
import {
  createTool,
  deleteTool,
  fetchTools,
  updateTool,
} from '../api/tools'

const emit = defineEmits(['navigate'])

const message = useMessage()
const dialog = useDialog()

const tools = ref([])
const loading = ref(false)
const showModal = ref(false)
const saving = ref(false)
const editingId = ref(null)

const emptyForm = () => ({
  name: '',
  location: '',
  remark: '',
})

const form = ref(emptyForm())

/**
 * 加载工具列表
 */
async function loadTools() {
  loading.value = true
  try {
    const { data } = await fetchTools()
    tools.value = data
  } catch {
    message.error('加载工具失败，请确认后端已启动')
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
    name: row.name,
    location: row.location,
    remark: row.remark,
  }
  showModal.value = true
}

/**
 * 提交表单（新建或更新）
 */
async function handleSubmit() {
  if (!form.value.name.trim()) {
    message.warning('请填写工具名称')
    return
  }

  const payload = {
    name: form.value.name.trim(),
    location: form.value.location.trim(),
    remark: form.value.remark.trim(),
  }

  saving.value = true
  try {
    if (editingId.value) {
      await updateTool(editingId.value, payload)
      message.success('已更新工具')
    } else {
      await createTool(payload)
      message.success('已添加工具')
    }
    showModal.value = false
    await loadTools()
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

/**
 * 确认删除工具
 * @param {object} row
 */
function confirmDelete(row) {
  dialog.warning({
    title: '删除确认',
    content: `确定删除「${row.name.slice(0, 30)}${row.name.length > 30 ? '…' : ''}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteTool(row.id)
        message.success('已删除')
        await loadTools()
      } catch {
        message.error('删除失败')
      }
    },
  })
}

const columns = [
  {
    title: '工具名称',
    key: 'name',
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: '存放位置',
    key: 'location',
    width: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: '备注说明',
    key: 'remark',
    minWidth: 280,
    ellipsis: { tooltip: true },
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

onMounted(loadTools)
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>常用工具清单</h1>
        <p class="subtitle">管理家中常用工具，方便快速找到存放位置</p>
      </div>
      <n-space>
        <n-button @click="emit('navigate', 'stats')">统计概览</n-button>
        <n-button @click="emit('navigate', 'records')">返回维修记录</n-button>
        <n-button type="primary" @click="openCreate">新增工具</n-button>
      </n-space>
    </header>

    <n-card title="工具列表" :bordered="false" class="table-card">
      <n-data-table
        :columns="columns"
        :data="tools"
        :loading="loading"
        :bordered="false"
        striped
        size="small"
      />
    </n-card>

    <n-modal
      v-model:show="showModal"
      preset="card"
      :title="editingId ? '编辑工具' : '新增工具'"
      style="width: 520px"
      :mask-closable="false"
    >
      <n-form label-placement="top">
        <n-form-item label="工具名称" required>
          <n-input
            v-model:value="form.name"
            placeholder="例如：活动扳手"
          />
        </n-form-item>
        <n-form-item label="存放位置">
          <n-input
            v-model:value="form.location"
            placeholder="例如：工具箱第一层"
          />
        </n-form-item>
        <n-form-item label="备注说明">
          <n-input
            v-model:value="form.remark"
            type="textarea"
            placeholder="规格、使用注意事项等"
            :rows="3"
          />
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
