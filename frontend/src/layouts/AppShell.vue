<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen flex bg-paper text-ink">
    <aside class="w-60 shrink-0 border-r border-sand flex flex-col justify-between py-8 px-5">
      <div>
        <h1 class="font-display text-xl tracking-tight mb-10">Kiwi-Biz <span class="text-harbour">Assistant</span></h1>
        <nav class="space-y-1">
          <RouterLink
            to="/dashboard"
            class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
            active-class="text-ink"
            exact-active-class="text-ink"
            v-slot="{ isActive }"
          >
            <span
              class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
              :class="isActive ? 'bg-amber' : 'bg-transparent'"
            />
            <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Documents</span>
          </RouterLink>
        </nav>
      </div>

      <div class="border-t border-sand pt-4">
        <p class="text-xs text-ink/50 mb-2 truncate">{{ auth.user?.email }}</p>
        <button
          @click="handleLogout"
          class="text-sm font-medium text-ink/60 hover:text-danger transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>

    <main class="flex-1 px-10 py-8">
      <slot />
    </main>
  </div>
</template>