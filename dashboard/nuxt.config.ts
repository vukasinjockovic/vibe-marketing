export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: true },

  modules: [
    '@unocss/nuxt',
  ],

  runtimeConfig: {
    public: {
      convexUrl: process.env.NUXT_PUBLIC_CONVEX_URL || 'http://localhost:3210',
    },
  },

  ssr: false, // SPA mode — Convex client is client-side only

  app: {
    head: {
      title: 'Vibe Marketing',
      meta: [
        { name: 'description', content: 'AI Marketing Automation Platform' },
      ],
    },
  },
})
