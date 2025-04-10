<template>
  <form @submit.prevent="addConfig" class="space-y-6">
    <div class="grid grid-cols-6 gap-6">
      <div class="col-span-6 sm:col-span-3">
        <label for="source_branch" class="block text-sm font-medium text-gray-700">Nhánh nguồn</label>
        <select
          id="source_branch"
          v-model="form.source_branch"
          class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        >
          <option value="">Chọn nhánh nguồn</option>
          <option v-for="branch in branches" :key="branch" :value="branch">
            {{ branch }}
          </option>
        </select>
      </div>

      <div class="col-span-6 sm:col-span-3">
        <label for="target_branch" class="block text-sm font-medium text-gray-700">Nhánh đích</label>
        <select
          id="target_branch"
          v-model="form.target_branch"
          class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          required
        >
          <option value="">Chọn nhánh đích</option>
          <option v-for="branch in branches" :key="branch" :value="branch">
            {{ branch }}
          </option>
        </select>
      </div>

      <div class="col-span-6 sm:col-span-3">
        <label for="time" class="block text-sm font-medium text-gray-700">Thời gian merge</label>
        <input
          type="time"
          id="time"
          v-model="form.time"
          class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
          required
        />
      </div>
    </div>

    <div class="mt-6">
      <button
        type="submit"
        class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        :disabled="isSubmitting"
      >
        {{ isSubmitting ? 'Đang thêm...' : 'Thêm cấu hình' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const props = defineProps<{
  branches: string[]
}>()

const emit = defineEmits<{
  (e: 'config-added'): void
}>()

const form = ref({
  source_branch: '',
  target_branch: '',
  time: ''
})

const isSubmitting = ref(false)

const addConfig = async () => {
  if (!form.value.source_branch || !form.value.target_branch || !form.value.time) {
    return
  }

  isSubmitting.value = true
  try {
    const response = await fetch(`${apiBase}/api/configs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    if (response.ok) {
      form.value = {
        source_branch: '',
        target_branch: '',
        time: ''
      }
      emit('config-added')
    }
  } catch (error) {
    console.error('Error adding config:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script> 