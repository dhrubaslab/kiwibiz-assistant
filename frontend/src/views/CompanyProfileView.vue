<script setup>
import { ref, onMounted, computed } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { useAuthStore } from '@/stores/auth'
import { getMyCompany, updateMyCompany } from '@/api/companies'

const auth = useAuthStore()
const isAdmin = computed(() => auth.user?.role === 'admin')

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref(false)

const form = ref({
  name: '',
  contact_email: '',
  industry: '',
  phone: '',
  address: '',
  website: '',
})

async function load() {
  loading.value = true
  try {
    const company = await getMyCompany()
    form.value = {
      name: company.name || '',
      contact_email: company.contact_email || '',
      industry: company.industry || '',
      phone: company.phone || '',
      address: company.address || '',
      website: company.website || '',
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  error.value = ''
  success.value = false
  saving.value = true
  try {
    await updateMyCompany(form.value)
    success.value = true
  } catch (e) {
    error.value = e.message || 'Could not update company profile.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppShell>
    <div class="mb-8 max-w-lg">
      <h2 class="font-display text-2xl">Company Profile</h2>
      <p class="text-sm text-ink/60 mt-1">
        {{ isAdmin ? 'Update your organisation\'s details.' : 'Your organisation\'s details.' }}
      </p>
    </div>

    <div v-if="loading" class="text-sm text-ink/50">Loading…</div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-4 max-w-lg">
      <div>
        <label class="block text-sm font-medium mb-1" for="name">Company name</label>
        <input
          id="name"
          v-model="form.name"
          type="text"
          required
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" for="contact_email">Contact email</label>
        <input
          id="contact_email"
          v-model="form.contact_email"
          type="email"
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" for="industry">Industry</label>
        <input
          id="industry"
          v-model="form.industry"
          type="text"
          placeholder="e.g. Hospitality, Retail, Trades"
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" for="phone">Phone</label>
        <input
          id="phone"
          v-model="form.phone"
          type="text"
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" for="address">Address</label>
        <textarea
          id="address"
          v-model="form.address"
          rows="2"
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" for="website">Website</label>
        <input
          id="website"
          v-model="form.website"
          type="text"
          placeholder="https://…"
          :disabled="!isAdmin"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour disabled:bg-sand/30 disabled:text-ink/60"
        />
      </div>

      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
      <p v-if="success" class="text-sm text-harbour">Company profile updated.</p>

      <button
        v-if="isAdmin"
        type="submit"
        :disabled="saving"
        class="bg-harbour hover:bg-harbour-dark text-white text-sm font-medium px-4 py-2 rounded transition-colors disabled:opacity-60"
      >
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>
  </AppShell>
</template>