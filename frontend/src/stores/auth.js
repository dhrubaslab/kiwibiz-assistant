import { defineStore } from 'pinia'
import request from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('kiwibiz_token') || null,
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
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
      localStorage.removeItem('kiwibiz_token')
    },
  },
})