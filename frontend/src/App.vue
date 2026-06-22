<script setup>
import { ref, watch, onMounted } from 'vue'
import { NConfigProvider, NDialogProvider, NMessageProvider } from 'naive-ui'
import RecordsView from './components/RecordsView.vue'
import ToolsView from './components/ToolsView.vue'

const currentPage = ref('records')

const pageTitles = {
  records: '家庭 DIY 维修小记',
  tools: '常用工具清单',
}

function updateTitle(page) {
  document.title = pageTitles[page] || '家庭 DIY 维修小记'
}

function handleNavigate(page) {
  currentPage.value = page
}

watch(currentPage, (newPage) => {
  updateTitle(newPage)
})

onMounted(() => {
  updateTitle(currentPage.value)
})
</script>

<template>
  <n-config-provider>
    <n-message-provider>
      <n-dialog-provider>
        <RecordsView
          v-show="currentPage === 'records'"
          @navigate="handleNavigate"
        />
        <ToolsView
          v-show="currentPage === 'tools'"
          @navigate="handleNavigate"
        />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #f5f7fa;
  color: #1f2937;
}
</style>
