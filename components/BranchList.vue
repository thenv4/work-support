<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <h2 class="text-xl font-semibold mb-4">{{ title }}</h2>
    <div class="max-h-60 overflow-y-auto">
      <ul class="divide-y divide-gray-200">
        <li v-for="branch in branches" :key="branch" class="py-2">
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-900">{{ branch }}</span>
            <button v-if="showSelect" @click="$emit('select', branch)"
              class="text-indigo-600 hover:text-indigo-900 text-sm font-medium">
              Chọn
            </button>
          </div>
        </li>
        <li v-if="branches.length === 0" class="py-2 text-sm text-gray-500">
          Không có nhánh nào
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  branches: string[]
  showSelect?: boolean
}>()

defineEmits<{
  (e: 'select', branch: string): void
}>()
</script>