<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
function handleExitImpersonation() {
  auth.exitImpersonation().then(() => router.push('/companies'))
}

</script>

<template>
  <div class="min-h-screen flex bg-paper text-ink" :class="{ 'pt-9': auth.isImpersonating }">
  <div v-if="auth.isImpersonating" class="fixed top-0 left-0 right-0 z-50 bg-amber text-ink text-sm font-medium text-center py-2">
    Viewing as {{ auth.user?.email }} (impersonating) —
    <button @click="handleExitImpersonation" class="underline font-semibold">Exit impersonation</button>
  </div>
    <aside class="w-60 shrink-0 border-r border-sand flex flex-col justify-between py-8 px-5">
      <div>
        <h1 class="font-display text-xl tracking-tight mb-10">Kiwi-Biz <span class="text-harbour">Assistant</span></h1>
        <nav class="space-y-1">
          <RouterLink
            v-if="auth.user?.role === 'super_admin'"
            to="/companies"
            class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
            v-slot="{ isActive }"
          >
            <span
              class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
              :class="isActive ? 'bg-amber' : 'bg-transparent'"
            />
            <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Companies</span>
          </RouterLink>

          <template v-else>
            <RouterLink
              to="/dashboard"
              class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
              v-slot="{ isActive }"
            >
              <span
                class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
                :class="isActive ? 'bg-amber' : 'bg-transparent'"
              />
              <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Documents</span>
            </RouterLink>

            <RouterLink
              to="/company-profile"
              class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
              v-slot="{ isActive }"
            >
              <span
                class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
                :class="isActive ? 'bg-amber' : 'bg-transparent'"
              />
              <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Company Profile</span>
            </RouterLink>
            
            <RouterLink
              v-if="auth.user?.role === 'admin'"
              to="/staff"
              class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
              v-slot="{ isActive }"
            >
              <span
                class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
                :class="isActive ? 'bg-amber' : 'bg-transparent'"
              />
              <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Staff</span>
            </RouterLink>
            <RouterLink
              to="/chat"
              class="relative block pl-4 py-2 text-sm font-medium rounded-r transition-colors"
              v-slot="{ isActive }"
            >
              <span
                class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full transition-colors"
                :class="isActive ? 'bg-amber' : 'bg-transparent'"
              />
              <span :class="isActive ? 'text-ink' : 'text-ink/60 hover:text-ink'">Ask Documents</span>
            </RouterLink>
          </template>
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