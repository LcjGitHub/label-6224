<script setup>
import { ref } from 'vue'
import { NConfigProvider, NDialogProvider, NMessageProvider } from 'naive-ui'
import RecordsView from './components/RecordsView.vue'
import ToolsView from './components/ToolsView.vue'

const currentPage = ref('records')

function handleNavigate(page) {
  currentPage.value = page
}
</script>

<template>
  <n-config-provider>
    <n-message-provider>
      <n-dialog-provider>
        <RecordsView
          v-if="currentPage === 'records'"
          @navigate="handleNavigate"
        />
        <ToolsView
          v-else-if="currentPage === 'tools'"
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
