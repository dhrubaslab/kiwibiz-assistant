import { defineStore } from 'pinia'
import request from '@/api/client'
import { loginAsCompany } from '@/api/companies'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('kiwibiz_token') || null,
    originalToken: localStorage.getItem('kiwibiz_original_token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isImpersonating: (state) => !!state.originalToken,
  },
  actions: {
    async login(email, password) {
      const form = new URLSearchParams()
      form.append('username', email)
      form.append('password', password)
      const data = await request('/api/auth/login', {
        method: 'POST',
        body: form,
        isForm: true,
        auth: false,
      })
      this.token = data.access_token
      localStorage.setItem('kiwibiz_token', this.token)
      await this.fetchMe()
    },
    async register(payload) {
      await request('/api/auth/register', {
        method: 'POST',
        body: payload,
        auth: false,
      })
      await this.login(payload.email, payload.password)
    },
    async fetchMe() {
      this.user = await request('/api/auth/me')
    },
    logout() {
      this.token = null
      this.user = null
      this.originalToken = null
      localStorage.removeItem('kiwibiz_token')
      localStorage.removeItem('kiwibiz_original_token')
    },

    /**
     * Super Admin "Login-As": swaps the current session for a short-lived
     * token belonging to the target company's admin, while preserving the
     * Super Admin's own token so exitImpersonation() can restore it later.
     */
    async loginAs(companyId) {
      // Don't overwrite a saved original token if already impersonating —
      // that would lose the real Super Admin session on a second Login-As.
      if (!this.originalToken) {
        this.originalToken = this.token
        localStorage.setItem('kiwibiz_original_token', this.originalToken)
      }

      const data = await loginAsCompany(companyId)
      this.token = data.access_token
      localStorage.setItem('kiwibiz_token', this.token)
      await this.fetchMe()
    },

    async exitImpersonation() {
      if (!this.originalToken) return
      this.token = this.originalToken
      this.originalToken = null
      localStorage.setItem('kiwibiz_token', this.token)
      localStorage.removeItem('kiwibiz_original_token')
      await this.fetchMe()
    },
  },
})