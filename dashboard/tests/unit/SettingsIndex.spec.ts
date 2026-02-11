import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import SettingsIndex from '../../pages/settings/index.vue'

vi.stubGlobal('useRoute', () => ({
  path: '/settings',
}))
vi.stubGlobal('navigateTo', vi.fn())
vi.stubGlobal('useState', (key: string, init: () => any) => ref(init()))

describe('SettingsIndex (pages/settings/index.vue)', () => {
  function mountPage() {
    return mount(SettingsIndex, {
      global: {
        stubs: {
          VPageHeader: {
            template: '<div class="page-header"><h1>{{ title }}</h1></div>',
            props: ['title', 'description'],
          },
          NuxtLink: {
            template: '<a :href="to" :class="$attrs.class"><slot /></a>',
            props: ['to'],
          },
        },
      },
    })
  }

  it('renders settings page header', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Settings')
  })

  it('shows Service Registry section link', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Service Registry')
  })

  it('shows Notifications section link', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Notifications')
  })

  it('shows Agents section link', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Agents')
  })

  it('has correct link paths', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a')
    const hrefs = links.map(l => l.attributes('href'))
    expect(hrefs).toContain('/services')
    expect(hrefs).toContain('/settings/notifications')
    expect(hrefs).toContain('/agents')
  })

  it('shows descriptions for each section', () => {
    const wrapper = mountPage()
    const text = wrapper.text()
    expect(text).toContain('external API services')
    expect(text).toContain('notification')
    expect(text).toContain('AI agents')
  })

  it('renders three settings cards', () => {
    const wrapper = mountPage()
    const links = wrapper.findAll('a').filter(l => {
      const href = l.attributes('href')
      return href === '/services' || href === '/settings/notifications' || href === '/agents'
    })
    expect(links.length).toBe(3)
  })
})
