export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
      '@nuxtjs/tailwindcss',
      '@pinia/nuxt',
  ],

  runtimeConfig: {
      public: {
          apiBase: process.env.API_BASE || 'http://localhost:5000'
      }
  },

  app: {
      head: {
          title: 'Auto Merge Tool',
          meta: [
              { charset: 'utf-8' },
              { name: 'viewport', content: 'width=device-width, initial-scale=1' },
              { hid: 'description', name: 'description', content: 'Tự động merge code giữa các nhánh Git' }
          ]
      }
  },

  compatibilityDate: '2025-04-10'
})