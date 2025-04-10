<template>
  <div class="flex flex-col">
    <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
      <div class="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
        <div class="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nhánh nguồn
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nhánh đích
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Thời gian
                </th>
                <th scope="col" class="relative px-6 py-3">
                  <span class="sr-only">Xóa</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="config in configs" :key="config.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ config.source_branch }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ config.target_branch }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ config.time }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click="confirmDelete(config)"
                    class="text-red-600 hover:text-red-900"
                    :disabled="isDeleting"
                  >
                    Xóa
                  </button>
                </td>
              </tr>
              <tr v-if="configs.length === 0">
                <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500">
                  Chưa có cấu hình nào
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal xác nhận xóa -->
    <div v-if="showDeleteModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Xác nhận xóa
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500">
                    Bạn có chắc chắn muốn xóa cấu hình merge từ nhánh <strong>{{ selectedConfig?.source_branch }}</strong> sang nhánh <strong>{{ selectedConfig?.target_branch }}</strong>?
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
              @click="deleteConfig"
              :disabled="isDeleting"
            >
              {{ isDeleting ? 'Đang xóa...' : 'Xóa' }}
            </button>
            <button
              type="button"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              @click="showDeleteModal = false"
            >
              Hủy
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const props = defineProps<{
  configs: Array<{
    id: string
    source_branch: string
    target_branch: string
    time: string
  }>
}>()

const emit = defineEmits<{
  (e: 'config-deleted'): void
}>()

const isDeleting = ref(false)
const showDeleteModal = ref(false)
const selectedConfig = ref<typeof props.configs[0] | null>(null)

const confirmDelete = (config: typeof props.configs[0]) => {
  selectedConfig.value = config
  showDeleteModal.value = true
}

const deleteConfig = async () => {
  if (!selectedConfig.value || isDeleting.value) return
  
  isDeleting.value = true
  try {
    const response = await fetch(`${apiBase}/api/configs/${selectedConfig.value.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      showDeleteModal.value = false
      selectedConfig.value = null
      emit('config-deleted')
    }
  } catch (error) {
    console.error('Error deleting config:', error)
  } finally {
    isDeleting.value = false
  }
}
</script> 