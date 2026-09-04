<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { listCompanies, createCompany, updateSubscription } from '@/api/companies'
import { RouterLink } from 'vue-router'
const SUBSCRIPTION_TYPES = [
  { value: 'free', label: 'Free' },
  { value: 'premium_monthly', label: 'Premium (monthly)' },
  { value: 'elite_yearly', label: 'Elite (yearly)' },
]

const companies = ref([])
const loading = ref(true)
const error = ref('')
const updatingId = ref(null)
const expiryDrafts = ref({})

const router = useRouter()
const auth = useAuthStore()

// --- create company form ---
const showCreateForm = ref(false)
const creating = ref(false)
const newCompany = ref({ name: '', contact_email: '', phone: '' })

async function handleLoginAs(c) {
  error.value = ''
  try {
    await auth.loginAs(c.id)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.message || 'Could not log in as this company\'s admin.'
  }
}

async function loadCompanies() {
  loading.value = true
  try {
    companies.value = await listCompanies()
    for (const c of companies.value) {
      expiryDrafts.value[c.id] = c.subscription_expires_at ? c.subscription_expires_at.slice(0, 10) : ''
    }
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
    await createCompany(newCompany.value)
    newCompany.value = { name: '', contact_email: '', phone: '' }
    showCreateForm.value = false
    await loadCompanies()
  } catch (e) {
    error.value = e.message || 'Could not create company.'
  } finally {
    creating.value = false
  }
}

async function toggleActive(c) {
  await patchSubscription(c, { is_active: !c.is_active })
}

async function saveExpiry(c) {
  const draft = expiryDrafts.value[c.id]
  await patchSubscription(c, {
    subscription_expires_at: draft ? new Date(draft).toISOString() : null,
  })
}

async function changeSubscriptionType(c, newType) {
  await patchSubscription(c, { subscription_type: newType })
}

async function patchSubscription(c, overrides) {
  updatingId.value = c.id
  try {
    const updated = await updateSubscription(c.id, {
      is_active: c.is_active,
      subscription_type: c.subscription_type,
      subscription_expires_at: c.subscription_expires_at,
      ...overrides,
    })
    applyUpdate(updated)
  } catch (e) {
    error.value = e.message
  } finally {
    updatingId.value = null
  }
}

function applyUpdate(updated) {
  const idx = companies.value.findIndex((x) => x.id === updated.id)
  companies.value[idx] = updated
  expiryDrafts.value[updated.id] = updated.subscription_expires_at ? updated.subscription_expires_at.slice(0, 10) : ''
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('en-NZ', { day: 'numeric', month: 'short', year: 'numeric' })
}

function subscriptionLabel(value) {
  return SUBSCRIPTION_TYPES.find((t) => t.value === value)?.label || value
}

onMounted(loadCompanies)
</script>

<template>
  <AppShell>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="font-display text-2xl">Companies</h2>
        <p class="text-sm text-ink/60 mt-1">All registered organisations on the platform.</p>
      </div>
      <button
        @click="showCreateForm = !showCreateForm"
        class="bg-amber hover:bg-amber/90 text-ink font-medium text-sm px-4 py-2 rounded transition-colors"
      >
        {{ showCreateForm ? 'Cancel' : '+ Add company' }}
      </button>
    </div>

    <div v-if="showCreateForm" class="border border-sand rounded p-5 mb-8 max-w-lg">
      <h3 class="font-medium text-sm mb-3">New company profile</h3>
      <form @submit.prevent="handleCreate" class="space-y-3">
        <input
          v-model="newCompany.name"
          type="text"
          placeholder="Company name"
          required
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour"
        />
        <input
          v-model="newCompany.contact_email"
          type="email"
          placeholder="Contact email"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour"
        />
        <input
          v-model="newCompany.phone"
          type="text"
          placeholder="Phone number"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour"
        />
        <button
          type="submit"
          :disabled="creating"
          class="bg-harbour hover:bg-harbour-dark text-white text-sm font-medium px-4 py-2 rounded transition-colors disabled:opacity-60"
        >
          {{ creating ? 'Creating…' : 'Create company' }}
        </button>
      </form>
    </div>

    <p v-if="error" class="text-sm text-danger mb-4">{{ error }}</p>
    <div v-if="loading" class="text-sm text-ink/50">Loading…</div>

    <div v-else-if="companies.length === 0" class="border border-dashed border-sand rounded p-10 text-center">
      <p class="text-ink/60 text-sm">No companies registered yet.</p>
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="c in companies"
        :key="c.id"
        class="border border-sand rounded p-4 flex items-center justify-between gap-4 flex-wrap"
      >
        <div class="min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <h3 class="font-medium">{{ c.name }}</h3>
            <span
              class="text-xs font-mono px-2 py-0.5 rounded-full shrink-0"
              :class="c.is_active ? 'bg-harbour/10 text-harbour' : 'bg-danger/10 text-danger'"
            >
              {{ c.is_active ? 'Active' : 'Disabled' }}
            </span>
            <span class="text-xs font-mono px-2 py-0.5 rounded-full bg-amber/10 text-amber shrink-0">
              {{ subscriptionLabel(c.subscription_type) }}
            </span>
          </div>
          <p class="text-xs text-ink/60 mt-1">
            {{ c.contact_email || 'No contact email' }} · Joined {{ formatDate(c.created_at) }}
          </p>
        </div>

        <div class="flex items-center gap-3 shrink-0 flex-wrap">
        <RouterLink :to="`/companies/${c.id}/edit`" class="text-sm font-medium text-harbour hover:underline">Edit</RouterLink>
        
        <button @click="handleLoginAs(c)"
          class="text-sm font-medium text-teal-700 hover:underline">Login-As
        </button>
        
          <select
            :value="c.subscription_type"
            @change="changeSubscriptionType(c, $event.target.value)"
            :disabled="updatingId === c.id"
            class="border border-sand rounded px-2 py-1 text-xs bg-white"
          >
            <option v-for="t in SUBSCRIPTION_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>

          <div class="flex items-center gap-1.5">
            <label class="text-xs text-ink/50">Expires</label>
            <input
              type="date"
              v-model="expiryDrafts[c.id]"
              class="border border-sand rounded px-2 py-1 text-xs font-mono"
            />
            <button
              @click="saveExpiry(c)"
              :disabled="updatingId === c.id"
              class="text-xs text-harbour hover:underline disabled:opacity-50"
            >
              Save
            </button>
          </div>

          <button
            @click="toggleActive(c)"
            :disabled="updatingId === c.id"
            class="text-sm font-medium hover:underline disabled:opacity-50"
            :class="c.is_active ? 'text-danger' : 'text-harbour'"
          >
            {{ updatingId === c.id ? 'Updating…' : c.is_active ? 'Disable' : 'Enable' }}
          </button>
        </div>
      </div>
    </div>
  </AppShell>
</template>