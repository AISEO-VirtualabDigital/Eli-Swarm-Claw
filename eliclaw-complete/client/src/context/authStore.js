import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,

      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),

      login: async (email, password) => {
        set({ isLoading: true })
        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          })
          const data = await res.json()
          if (data.success) {
            set({ user: data.user, token: data.token, isLoading: false })
            return { success: true }
          }
          set({ isLoading: false })
          return { success: false, error: data.error }
        } catch (err) {
          set({ isLoading: false })
          return { success: false, error: 'Network error' }
        }
      },

      register: async (name, email, password) => {
        set({ isLoading: true })
        try {
          const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
          })
          const data = await res.json()
          if (data.success) {
            set({ user: data.user, token: data.token, isLoading: false })
            return { success: true }
          }
          set({ isLoading: false })
          return { success: false, error: data.error }
        } catch (err) {
          set({ isLoading: false })
          return { success: false, error: 'Network error' }
        }
      },

      logout: () => {
        set({ user: null, token: null })
        localStorage.removeItem('auth-storage')
      },

      updateProfile: (updates) => {
        set((state) => ({ user: { ...state.user, ...updates } }))
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, token: state.token })
    }
  )
)