<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message || 'Could not sign in.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-paper px-4">
    <div class="w-full max-w-sm">
      <h1 class="font-display text-3xl mb-1">Welcome to KiwiBiz Assistant</h1>
      <p class="text-ink/60 text-sm mb-8">I am your personal assistant.</p>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full border border-sand rounded px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-harbour"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full border border-sand rounded px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-harbour"
          />
        </div>

        <p v-if="error" class="text-sm text-danger">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-harbour hover:bg-harbour-dark text-white font-medium py-2 rounded transition-colors disabled:opacity-60"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="text-sm text-ink/60 mt-6">
        No account yet?
        <RouterLink to="/register" class="text-harbour font-medium hover:underline">Create one</RouterLink>
      </p>
    </div>
  </div>
</template>