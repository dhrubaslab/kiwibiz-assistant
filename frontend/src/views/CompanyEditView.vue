<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { getCompany, updateCompany } from '@/api/companies'

const route = useRoute()
const router = useRouter()
const companyId = route.params.id

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
    const company = await getCompany(companyId)
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
    await updateCompany(companyId, form.value)
    success.value = true
  } catch (e) {
    error.value = e.message || 'Could not update company.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppShell>
    <div class="mb-8 max-w-lg">
      <RouterLink to="/companies" class="text-sm text-harbour hover:underline">← Back to companies</RouterLink>
      <h2 class="font-display text-2xl mt-3">Edit Company</h2>
    </div>

    <div v-if="loading" class="text-sm text-ink/50">Loading…</div>

    <form v-else @submit.prevent="handleSubmit" class="space-y-4 max-w-lg">
      <div>
        <label class="block text-sm font-medium mb-1" for="name">Company name</label>
        <input id="name" v-model="form.name" type="text" required
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1" for="contact_email">Contact email</label>
        <input id="contact_email" v-model="form.contact_email" type="email"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1" for="industry">Industry</label>
        <input id="industry" v-model="form.industry" type="text" placeholder="e.g. Hospitality, Retail, Trades"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1" for="phone">Phone</label>
        <input id="phone" v-model="form.phone" type="text"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1" for="address">Address</label>
        <textarea id="address" v-model="form.address" rows="2"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1" for="website">Website</label>
        <input id="website" v-model="form.website" type="text" placeholder="https://…"
          class="w-full border border-sand rounded px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-harbour" />
      </div>

      <p v-if="error" class="text-sm text-danger">{{ error }}</p>
      <p v-if="success" class="text-sm text-harbour">Company updated.</p>

      <button type="submit" :disabled="saving"
        class="bg-harbour hover:bg-harbour-dark text-white text-sm font-medium px-4 py-2 rounded transition-colors disabled:opacity-60">
        {{ saving ? 'Saving…' : 'Save changes' }}
      </button>
    </form>
  </AppShell>
</template>