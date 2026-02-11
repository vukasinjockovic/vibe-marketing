import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EnrichmentFieldStatus from '../../components/EnrichmentFieldStatus.vue'

describe('EnrichmentFieldStatus', () => {
  it('renders the label', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Awareness Stage', value: 'problem_aware', filled: true },
    })
    expect(wrapper.text()).toContain('Awareness Stage')
  })

  it('renders the value when filled', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Awareness Stage', value: 'problem_aware', filled: true },
    })
    expect(wrapper.text()).toContain('problem_aware')
  })

  it('shows placeholder when not filled', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Awareness Stage', value: null, filled: false },
    })
    expect(wrapper.text()).toContain('Not yet enriched')
  })

  it('shows green indicator when filled', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Test', value: 'val', filled: true },
    })
    const indicator = wrapper.find('[data-testid="field-status-indicator"]')
    expect(indicator.classes()).toContain('bg-green-500')
  })

  it('shows muted indicator when not filled', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Test', value: null, filled: false },
    })
    const indicator = wrapper.find('[data-testid="field-status-indicator"]')
    // After redesign: bg-gray-300 was replaced with bg-muted-foreground/30
    expect(indicator.classes().some(c => c.includes('bg-muted-foreground'))).toBe(true)
  })

  it('shows confidence badge when provided', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Test', value: 'val', filled: true, confidence: 'high' },
    })
    expect(wrapper.text()).toContain('high')
  })

  it('does not show confidence badge when not provided', () => {
    const wrapper = mount(EnrichmentFieldStatus, {
      props: { label: 'Test', value: 'val', filled: true },
    })
    const badge = wrapper.find('[data-testid="confidence-badge"]')
    expect(badge.exists()).toBe(false)
  })
})
