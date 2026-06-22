<script setup>
import { computed, ref, watch } from 'vue'
import { format, parseISO } from 'date-fns'
import {
  NButton,
  NDatePicker,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NInput,
  NInputNumber,
  NList,
  NListItem,
  NThing,
  NSpace,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import { createExpense, deleteExpense, fetchExpenses } from '../api/expenses'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  recordId: {
    type: Number,
    default: null,
  },
  recordDescription: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:show'])

const message = useMessage()
const dialog = useDialog()

const expenses = ref([])
const loading = ref(false)
const saving = ref(false)
const showForm = ref(false)

const emptyForm = () => ({
  material_name: '',
  amount: 0,
  purchase_date: Date.now(),
})

const form = ref(emptyForm())

const totalAmount = computed(() => {
  return expenses.value.reduce((sum, item) => sum + item.amount, 0).toFixed(2)
})

/**
 * 将时间戳格式化为 YYYY-MM-DD
 * @param {number} timestamp
 * @returns {string}
 */
function toDateString(timestamp) {
  return format(timestamp, 'yyyy-MM-dd')
}

/**
 * 格式化显示日期
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
 * 加载花费列表
 */
async function loadExpenses() {
  if (!props.recordId) return
  loading.value = true
  try {
    const { data } = await fetchExpenses(props.recordId)
    expenses.value = data
  } catch {
    message.error('加载花费失败')
  } finally {
    loading.value = false
  }
}

/**
 * 打开新增表单
 */
function openAddForm() {
  form.value = emptyForm()
  showForm.value = true
}

/**
 * 提交新增花费
 */
async function handleSubmit() {
  if (!form.value.material_name.trim()) {
    message.warning('请填写材料名称')
    return
  }

  const payload = {
    record_id: props.recordId,
    material_name: form.value.material_name.trim(),
    amount: form.value.amount ?? 0,
    purchase_date: toDateString(form.value.purchase_date),
  }

  saving.value = true
  try {
    await createExpense(payload)
    message.success('已添加花费')
    showForm.value = false
    await loadExpenses()
  } catch {
    message.error('添加失败')
  } finally {
    saving.value = false
  }
}

/**
 * 确认删除花费
 * @param {object} item
 */
function confirmDelete(item) {
  dialog.warning({
    title: '删除确认',
    content: `确定删除「${item.material_name}」吗？`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteExpense(item.id)
        message.success('已删除')
        await loadExpenses()
      } catch {
        message.error('删除失败')
      }
    },
  })
}

function handleClose() {
  emit('update:show', false)
}

watch(
  () => props.show,
  (newVal) => {
    if (newVal && props.recordId) {
      loadExpenses()
    }
  },
)
</script>

<template>
  <n-drawer :show="show" @update:show="emit('update:show', $event)" placement="right" :width="420">
    <n-drawer-content title="花费明细" :closable="true">
      <template #header-extra>
        <n-button size="small" type="primary" @click="openAddForm">新增花费</n-button>
      </template>

      <div class="record-info">
        <n-thing :title="recordDescription" />
        <div class="total">
          <span>合计：</span>
          <n-tag type="primary" size="large" round>¥ {{ totalAmount }}</n-tag>
        </div>
      </div>

      <n-list bordered :loading="loading" class="expense-list">
        <n-list-item v-for="item in expenses" :key="item.id" class="expense-item">
          <n-thing :title="item.material_name">
            <template #description>
              <n-space>
                <span>购买日期：{{ formatDisplayDate(item.purchase_date) }}</span>
                <n-tag type="success" size="small">¥ {{ item.amount.toFixed(2) }}</n-tag>
              </n-space>
            </template>
            <template #action>
              <n-button size="small" type="error" text @click="confirmDelete(item)">删除</n-button>
            </template>
          </n-thing>
        </n-list-item>
        <n-list-item v-if="!loading && expenses.length === 0" class="empty-item">
          <div class="empty-text">暂无花费记录</div>
        </n-list-item>
      </n-list>

      <n-drawer v-model:show="showForm" placement="right" :width="360">
        <n-drawer-content title="新增花费" :closable="true">
          <n-form label-placement="top" class="form">
            <n-form-item label="材料名称" required>
              <n-input
                v-model:value="form.material_name"
                placeholder="例如：水龙头阀芯"
              />
            </n-form-item>
            <n-form-item label="金额（元）" required>
              <n-input-number
                v-model:value="form.amount"
                :min="0"
                :step="1"
                :precision="2"
                style="width: 100%"
              />
            </n-form-item>
            <n-form-item label="购买日期" required>
              <n-date-picker
                v-model:value="form.purchase_date"
                type="date"
                style="width: 100%"
              />
            </n-form-item>
          </n-form>
          <template #footer>
            <n-space justify="end">
              <n-button @click="showForm = false">取消</n-button>
              <n-button type="primary" :loading="saving" @click="handleSubmit">
                保存
              </n-button>
            </n-space>
          </template>
        </n-drawer-content>
      </n-drawer>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.record-info {
  padding: 16px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 16px;
}

.total {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
  color: #6b7280;
}

.expense-list {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.expense-item {
  padding: 12px 16px;
}

.empty-item {
  padding: 40px 16px;
}

.empty-text {
  text-align: center;
  color: #9ca3af;
  font-size: 0.9rem;
}

.form {
  padding-top: 8px;
}
</style>
