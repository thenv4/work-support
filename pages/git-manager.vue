<template>
    <div class="min-h-screen bg-gray-100">
        <div class="flex h-screen">
            <!-- Sidebar -->
            <div class="w-64 bg-gray-800 text-white p-4">
                <div class="mb-6">
                    <h2 class="text-xl font-bold mb-4">Git Manager</h2>
                    <div class="space-y-2">
                        <button @click="activeTab = 'branches'" :class="{ 'bg-gray-700': activeTab === 'branches' }"
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-700">
                            Branches
                        </button>
                        <button @click="activeTab = 'commits'" :class="{ 'bg-gray-700': activeTab === 'commits' }"
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-700">
                            Commits
                        </button>
                        <button @click="activeTab = 'stash'" :class="{ 'bg-gray-700': activeTab === 'stash' }"
                            class="w-full text-left px-4 py-2 rounded hover:bg-gray-700">
                            Stash
                        </button>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="flex-1 p-6">
                <!-- Branches Tab -->
                <div v-if="activeTab === 'branches'" class="space-y-4">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xl font-bold">Branches</h3>
                        <button @click="showCreateBranchModal = true"
                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Create Branch
                        </button>
                    </div>

                    <!-- Local Branches -->
                    <div class="bg-white rounded-lg shadow p-4">
                        <h4 class="font-semibold mb-2">Local Branches</h4>
                        <div class="space-y-2">
                            <div v-for="branch in localBranches" :key="branch"
                                class="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                                <div class="flex items-center">
                                    <span class="w-3 h-3 rounded-full bg-green-500 mr-2"></span>
                                    <span>{{ branch }}</span>
                                </div>
                                <div class="space-x-2">
                                    <button @click="checkoutBranch(branch)" class="text-blue-500 hover:text-blue-700">
                                        Checkout
                                    </button>
                                    <button @click="deleteBranch(branch)" class="text-red-500 hover:text-red-700">
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Remote Branches -->
                    <div class="bg-white rounded-lg shadow p-4">
                        <h4 class="font-semibold mb-2">Remote Branches</h4>
                        <div class="space-y-2">
                            <div v-for="branch in remoteBranches" :key="branch"
                                class="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                                <div class="flex items-center">
                                    <span class="w-3 h-3 rounded-full bg-blue-500 mr-2"></span>
                                    <span>{{ branch }}</span>
                                </div>
                                <div class="space-x-2">
                                    <button @click="checkoutRemoteBranch(branch)"
                                        class="text-blue-500 hover:text-blue-700">
                                        Checkout
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Commits Tab -->
                <div v-if="activeTab === 'commits'" class="space-y-4">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xl font-bold">Commits</h3>
                        <div class="flex space-x-2">
                            <button @click="fetchCommits"
                                class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">
                                Fetch
                            </button>
                            <button @click="pullChanges"
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                                Pull
                            </button>
                            <button @click="pushChanges"
                                class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                                Push
                            </button>
                        </div>
                    </div>

                    <!-- Commit Graph -->
                    <div class="bg-white rounded-lg shadow p-4">
                        <div class="space-y-4">
                            <div v-for="commit in commits" :key="commit.hash"
                                class="flex items-start space-x-4 p-2 hover:bg-gray-50 rounded">
                                <div class="flex flex-col items-center">
                                    <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                                    <div class="w-0.5 h-8 bg-gray-300"></div>
                                </div>
                                <div class="flex-1">
                                    <div class="font-semibold">{{ commit.message }}</div>
                                    <div class="text-sm text-gray-500">
                                        {{ commit.author }} - {{ commit.date }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Stash Tab -->
                <div v-if="activeTab === 'stash'" class="space-y-4">
                    <div class="flex justify-between items-center">
                        <h3 class="text-xl font-bold">Stash</h3>
                        <button @click="showStashModal = true"
                            class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                            Stash Changes
                        </button>
                    </div>

                    <!-- Stash List -->
                    <div class="bg-white rounded-lg shadow p-4">
                        <div class="space-y-2">
                            <div v-for="stash in stashes" :key="stash.id"
                                class="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                                <div>{{ stash.message }}</div>
                                <div class="space-x-2">
                                    <button @click="applyStash(stash.id)" class="text-blue-500 hover:text-blue-700">
                                        Apply
                                    </button>
                                    <button @click="dropStash(stash.id)" class="text-red-500 hover:text-red-700">
                                        Drop
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Create Branch Modal -->
        <div v-if="showCreateBranchModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-white rounded-lg p-6 w-96">
                <h3 class="text-xl font-bold mb-4">Create New Branch</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Branch Name</label>
                        <input v-model="newBranchName" type="text"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">From Branch</label>
                        <select v-model="fromBranch"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            <option v-for="branch in localBranches" :key="branch" :value="branch">
                                {{ branch }}
                            </option>
                        </select>
                    </div>
                    <div class="flex justify-end space-x-2">
                        <button @click="showCreateBranchModal = false"
                            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded">
                            Cancel
                        </button>
                        <button @click="createBranch"
                            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                            Create
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Stash Modal -->
        <div v-if="showStashModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-white rounded-lg p-6 w-96">
                <h3 class="text-xl font-bold mb-4">Stash Changes</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Message</label>
                        <input v-model="stashMessage" type="text"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div class="flex justify-end space-x-2">
                        <button @click="showStashModal = false"
                            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded">
                            Cancel
                        </button>
                        <button @click="createStash" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                            Stash
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const activeTab = ref('branches')
const localBranches = ref([])
const remoteBranches = ref([])
const commits = ref([])
const stashes = ref([])
const showCreateBranchModal = ref(false)
const showStashModal = ref(false)
const newBranchName = ref('')
const fromBranch = ref('')
const stashMessage = ref('')

// Fetch branches
const fetchBranches = async () => {
    try {
        const response = await fetch('/api/branches/local')
        localBranches.value = await response.json()

        const remoteResponse = await fetch('/api/branches/remote')
        remoteBranches.value = await remoteResponse.json()
    } catch (error) {
        console.error('Error fetching branches:', error)
    }
}

// Fetch commits
const fetchCommits = async () => {
    try {
        const response = await fetch('/api/commits')
        commits.value = await response.json()
    } catch (error) {
        console.error('Error fetching commits:', error)
    }
}

// Fetch stashes
const fetchStashes = async () => {
    try {
        const response = await fetch('/api/stashes')
        stashes.value = await response.json()
    } catch (error) {
        console.error('Error fetching stashes:', error)
    }
}

// Checkout branch
const checkoutBranch = async (branch) => {
    try {
        await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ branch })
        })
        await fetchBranches()
    } catch (error) {
        console.error('Error checking out branch:', error)
    }
}

// Delete branch
const deleteBranch = async (branch) => {
    if (!confirm(`Are you sure you want to delete branch ${branch}?`)) return

    try {
        await fetch('/api/branches/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ branch })
        })
        await fetchBranches()
    } catch (error) {
        console.error('Error deleting branch:', error)
    }
}

// Create branch
const createBranch = async () => {
    try {
        await fetch('/api/branches/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: newBranchName.value,
                from: fromBranch.value
            })
        })
        showCreateBranchModal.value = false
        newBranchName.value = ''
        fromBranch.value = ''
        await fetchBranches()
    } catch (error) {
        console.error('Error creating branch:', error)
    }
}

// Create stash
const createStash = async () => {
    try {
        await fetch('/api/stashes/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: stashMessage.value
            })
        })
        showStashModal.value = false
        stashMessage.value = ''
        await fetchStashes()
    } catch (error) {
        console.error('Error creating stash:', error)
    }
}

// Apply stash
const applyStash = async (stashId) => {
    try {
        await fetch('/api/stashes/apply', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stashId })
        })
        await fetchStashes()
    } catch (error) {
        console.error('Error applying stash:', error)
    }
}

// Drop stash
const dropStash = async (stashId) => {
    if (!confirm('Are you sure you want to drop this stash?')) return

    try {
        await fetch('/api/stashes/drop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ stashId })
        })
        await fetchStashes()
    } catch (error) {
        console.error('Error dropping stash:', error)
    }
}

// Pull changes
const pullChanges = async () => {
    try {
        await fetch('/api/pull', { method: 'POST' })
        await fetchCommits()
    } catch (error) {
        console.error('Error pulling changes:', error)
    }
}

// Push changes
const pushChanges = async () => {
    try {
        await fetch('/api/push', { method: 'POST' })
        await fetchCommits()
    } catch (error) {
        console.error('Error pushing changes:', error)
    }
}

onMounted(() => {
    fetchBranches()
    fetchCommits()
    fetchStashes()
})
</script>