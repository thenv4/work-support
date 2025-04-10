<template>
  <div class="space-y-6">
    <div class="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
      <div class="md:grid md:grid-cols-3 md:gap-6">
        <div class="md:col-span-1">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Cấu hình Merge</h3>
          <p class="mt-1 text-sm text-gray-500">
            Cấu hình tự động merge code giữa các nhánh
          </p>
        </div>
        <div class="mt-5 md:mt-0 md:col-span-2">
          <form @submit.prevent="addConfig">
            <div class="grid grid-cols-6 gap-6">
              <div class="col-span-6 sm:col-span-3">
                <label for="source_branch" class="block text-sm font-medium text-gray-700">Nhánh nguồn</label>
                <select
                  id="source_branch"
                  v-model="form.source_branch"
                  class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
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
                >
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
                />
              </div>
            </div>

            <div class="mt-6">
              <button
                type="submit"
                class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Thêm cấu hình
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Danh sách cấu hình -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Danh sách cấu hình</h3>
        <div class="mt-5">
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
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const branches = ref([])
const configs = ref([])
const form = ref({
  source_branch: '',
  target_branch: '',
  time: ''
})

// Fetch branches
const fetchBranches = async () => {
  try {
    const response = await fetch(`${apiBase}/api/branches`)
    branches.value = await response.json()
  } catch (error) {
    console.error('Error fetching branches:', error)
  }
}

// Fetch configs
const fetchConfigs = async () => {
  try {
    const response = await fetch(`${apiBase}/api/configs`)
    configs.value = await response.json()
  } catch (error) {
    console.error('Error fetching configs:', error)
  }
}

// Add new config
const addConfig = async () => {
  try {
    const response = await fetch(`${apiBase}/api/configs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    if (response.ok) {
      await fetchConfigs()
      form.value = {
        source_branch: '',
        target_branch: '',
        time: ''
      }
    }
  } catch (error) {
    console.error('Error adding config:', error)
  }
}

onMounted(() => {
  fetchBranches()
  fetchConfigs()
})
</script> 