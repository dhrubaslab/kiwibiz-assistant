<script setup>
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { useAuthStore } from '@/stores/auth'
import { listCompanyUsers, createStaff, updateUserStatus } from '@/api/users'

const auth = useAuthStore()
const users = ref([])
const loading = ref(true)
const error = ref('')

const email = ref('')
const password = ref('')
const creating = ref(false)
const updatingId = ref(null)

async function loadUsers() {
  loading.value = true
  try {
    users.value = await listCompanyUsers()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  error.value = ''
  creating.value = true
  try {
    await createStaff({ email: email.value, password: password.value })
    email.value = ''
    password.value = ''
    await loadUsers()
  } catch (e) {
    error.value = e.message || 'Could not create staff account.'
  } finally {
    creating.value = false
  }
}

async function toggleStatus(u) {
  updatingId.value = u.id
  try {
    const updated = await updateUserStatus(u.id, !u.is_active)
    const idx = users.value.findIndex((x) => x.id === u.id)
    users.value[idx] = updated
  } catch (e) {
    error.value = e.message
  } finally {
    updatingId.value = null
  }
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-NZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

onMounted(loadUsers)
</script>

<template>
  <AppShell>
    <div class="mb-8">
      <h2 class="font-display text-2xl">Staff</h2>
      <p class="text-sm text-ink/60 mt-1">Manage the people in your organisation.</p>
    </div>

    <div class="border border-sand rounded p-5 mb-8 max-w-lg">
      <h3 class="font-medium text-sm mb-3">Add a new staff account</h3>
      <form @submit.prevent="handleCreate" class="space-y-3">
        <input
          v-model="email"
          type="email"
          placeholder="staff@company.co.nz"
          required
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Temporary password"
          required
          minlength="8"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour"
        />
        <button
          type="submit"
          :disabled="creating"
          class="bg-harbour hover:bg-harbour-dark text-white text-sm font-medium px-4 py-2 rounded transition-colors disabled:opacity-60"
        >
          {{ creating ? 'Creating…' : 'Create staff account' }}
        </button>
      </form>
    </div>

    <p v-if="error" class="text-sm text-danger mb-4">{{ error }}</p>
    <div v-if="loading" class="text-sm text-ink/50">Loading…</div>

    <table v-else class="w-full text-sm">
      <thead>
        <tr class="border-b border-sand text-left text-ink/50">
          <th class="py-2 font-medium">Email</th>
          <th class="py-2 font-medium">Role</th>
          <th class="py-2 font-medium">Status</th>
          <th class="py-2 font-medium">Joined</th>
          <th class="py-2 font-medium"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-b border-sand/60">
          <td class="py-3">{{ u.email }}</td>
          <td class="py-3 text-ink/60 font-mono text-xs uppercase">{{ u.role }}</td>
          <td class="py-3">
            <span
              class="text-xs font-mono px-2 py-0.5 rounded-full"
              :class="u.is_active ? 'bg-harbour/10 text-harbour' : 'bg-danger/10 text-danger'"
            >
              {{ u.is_active ? 'Active' : 'Disabled' }}
            </span>
          </td>
          <td class="py-3 text-ink/60">{{ formatDate(u.created_at) }}</td>
          <td class="py-3 text-right">
            <button
              v-if="u.id !== auth.user?.id"
              @click="toggleStatus(u)"
              :disabled="updatingId === u.id"
              class="text-sm font-medium hover:underline disabled:opacity-50"
              :class="u.is_active ? 'text-danger' : 'text-harbour'"
            >
              {{ updatingId === u.id ? 'Updating…' : u.is_active ? 'Disable' : 'Enable' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>