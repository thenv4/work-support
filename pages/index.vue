<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-2xl font-bold">Cấu hình Merge tự động</h1>
      <div class="flex items-center space-x-4">
        <div v-if="autoMergeEnabled" class="text-sm text-gray-600">
          Lần merge tiếp theo sau: {{ timeUntilNextMerge }}
        </div>
        <div class="flex items-center space-x-2">
          <input v-model="mergeInterval" type="number" min="1" class="w-20 px-2 py-1 border rounded-md"
            :disabled="autoMergeEnabled" />
          <span class="text-sm text-gray-600">phút</span>
        </div>
        <button @click="toggleAutoMerge" :class="[
          'px-4 py-2 rounded-md text-white font-medium',
          autoMergeEnabled ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
        ]">
          {{ autoMergeEnabled ? 'Dừng tự động chạy' : 'Tự động chạy' }}
        </button>
        <button @click="triggerJenkins"
          class="px-4 py-2 rounded-md text-white font-medium bg-blue-600 hover:bg-blue-700">
          Trigger Jenkins
        </button>
      </div>
    </div>

    <!-- Thông báo -->
    <div v-if="notification.show" :class="[
      'mb-4 p-4 rounded-md',
      notification.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
    ]">
      {{ notification.message }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <!-- Danh sách nhánh -->
      <div class="space-y-8">
        <BranchList title="Nhánh Local" :branches="localBranches" :show-select="true" @select="selectBranch" />
        <BranchList title="Nhánh Remote" :branches="remoteBranches" :show-select="true" @select="selectBranch" />
      </div>

      <!-- Form thêm cấu hình -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">Thêm cấu hình mới</h2>
        <MergeForm :branches="allBranches" @config-added="fetchConfigs" />
      </div>

      <!-- Danh sách cấu hình -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h2 class="text-xl font-semibold mb-4">Danh sách cấu hình</h2>
        <ConfigTable :configs="configs" @config-deleted="fetchConfigs" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const localBranches = ref([])
const remoteBranches = ref([])
const configs = ref([])
const autoMergeEnabled = ref(false)
const mergeInterval = ref(20)
const lastMergeTime = ref<Date | null>(null)
const notification = ref({ show: false, message: '', type: 'success' })

let timer: number | null = null

const allBranches = computed(() => [...localBranches.value, ...remoteBranches.value])

const showNotification = (message: string, type: 'success' | 'error' = 'success') => {
  notification.value = { show: true, message, type }
  setTimeout(() => {
    notification.value.show = false
  }, 3000)
}

const timeUntilNextMerge = computed(() => {
  if (!lastMergeTime.value || !autoMergeEnabled.value) return '--:--'

  const now = new Date()
  const nextMerge = new Date(lastMergeTime.value.getTime() + mergeInterval.value * 60000)
  const diff = nextMerge.getTime() - now.getTime()

  if (diff <= 0) return 'Đang merge...'

  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const fetchAutoMergeStatus = async () => {
  try {
    const response = await fetch(`${apiBase}/api/auto-merge/status`)
    if (response.ok) {
      const data = await response.json()
      autoMergeEnabled.value = data.enabled
      mergeInterval.value = data.interval
      lastMergeTime.value = data.last_merge_time ? new Date(data.last_merge_time) : null
    }
  } catch (error) {
    console.error('Error fetching auto merge status:', error)
  }
}

const setMergeInterval = async () => {
  try {
    const response = await fetch(`${apiBase}/api/auto-merge/interval`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        interval: mergeInterval.value
      })
    })

    if (response.ok) {
      showNotification('Đã cập nhật khoảng thời gian merge')
    } else {
      const error = await response.json()
      showNotification(error.error || 'Lỗi khi cập nhật khoảng thời gian', 'error')
    }
  } catch (error) {
    showNotification('Lỗi khi cập nhật khoảng thời gian', 'error')
  }
}

const toggleAutoMerge = async () => {
  try {
    const response = await fetch(`${apiBase}/api/auto-merge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        enabled: !autoMergeEnabled.value
      })
    })

    if (response.ok) {
      autoMergeEnabled.value = !autoMergeEnabled.value
      showNotification(
        autoMergeEnabled.value ? 'Đã bật tự động merge' : 'Đã tắt tự động merge'
      )
      if (autoMergeEnabled.value) {
        lastMergeTime.value = new Date()
      }
    }
  } catch (error) {
    showNotification('Lỗi khi thay đổi trạng thái tự động merge', 'error')
  }
}

const fetchLocalBranches = async () => {
  try {
    const response = await fetch(`${apiBase}/api/branches/local`)
    if (response.ok) {
      localBranches.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching local branches:', error)
  }
}

const fetchRemoteBranches = async () => {
  try {
    const response = await fetch(`${apiBase}/api/branches/remote`)
    if (response.ok) {
      remoteBranches.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching remote branches:', error)
  }
}

const fetchConfigs = async () => {
  try {
    const response = await fetch(`${apiBase}/api/configs`)
    if (response.ok) {
      configs.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching configs:', error)
  }
}

const selectBranch = (branch: string) => {
  // TODO: Implement branch selection logic
  console.log('Selected branch:', branch)
}

const triggerJenkins = async () => {
  try {
    const response = await fetch(`${apiBase}/api/trigger-jenkins`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.ok) {
      showNotification('Đã trigger Jenkins job thành công')
    } else {
      const error = await response.json()
      showNotification(error.message || 'Lỗi khi trigger Jenkins job', 'error')
    }
  } catch (error) {
    showNotification('Lỗi khi trigger Jenkins job', 'error')
  }
}

onMounted(() => {
  fetchLocalBranches()
  fetchRemoteBranches()
  fetchConfigs()
  fetchAutoMergeStatus()
  timer = setInterval(fetchAutoMergeStatus, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>