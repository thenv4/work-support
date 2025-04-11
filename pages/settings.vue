<template>
    <div>
        <h1 class="text-2xl font-bold mb-6">Settings</h1>
        <div class="bg-white shadow rounded-lg p-6">
            <h2 class="text-lg font-medium mb-4">Jenkins Configuration</h2>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Jenkins URL</label>
                    <input type="text" v-model="jenkinsUrl"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Username</label>
                    <input type="text" v-model="jenkinsUsername"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700">Token</label>
                    <input type="password" v-model="jenkinsToken"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                </div>
                <div>
                    <button @click="saveSettings"
                        class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Save Settings
                    </button>
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

const jenkinsUrl = ref('')
const jenkinsUsername = ref('')
const jenkinsToken = ref('')

const saveSettings = async () => {
    try {
        const response = await fetch(`${apiBase}/api/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                jenkinsUrl: jenkinsUrl.value,
                jenkinsUsername: jenkinsUsername.value,
                jenkinsToken: jenkinsToken.value
            })
        })

        if (response.ok) {
            alert('Settings saved successfully')
        } else {
            alert('Failed to save settings')
        }
    } catch (error) {
        console.error('Error saving settings:', error)
        alert('Error saving settings')
    }
}

onMounted(async () => {
    try {
        const response = await fetch(`${apiBase}/api/settings`)
        if (response.ok) {
            const data = await response.json()
            jenkinsUrl.value = data.jenkinsUrl
            jenkinsUsername.value = data.jenkinsUsername
            jenkinsToken.value = data.jenkinsToken
        }
    } catch (error) {
        console.error('Error loading settings:', error)
    }
})
</script>