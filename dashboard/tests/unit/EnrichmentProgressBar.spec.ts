import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EnrichmentProgressBar from '../../components/EnrichmentProgressBar.vue'

describe('EnrichmentProgressBar', () => {
  it('renders with a given score', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 50 },
    })
    expect(wrapper.find('[data-testid="enrichment-bar"]').exists()).toBe(true)
  })

  it('shows percentage text by default', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 75 },
    })
    expect(wrapper.text()).toContain('75%')
  })

  it('hides percentage text when showPercentage is false', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 75, showPercentage: false },
    })
    expect(wrapper.text()).not.toContain('75%')
  })

  it('renders label when provided', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 60, label: 'Enrichment' },
    })
    expect(wrapper.text()).toContain('Enrichment')
  })

  it('applies red color class when score < 30', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 20 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.classes()).toContain('bg-red-500')
  })

  it('applies yellow color class when score is between 30 and 70', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 50 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.classes()).toContain('bg-yellow-500')
  })

  it('applies green color class when score > 70', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 85 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.classes()).toContain('bg-green-500')
  })

  it('sets width style based on score', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 45 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.attributes('style')).toContain('width: 45%')
  })

  it('clamps score at 0', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: -10 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.attributes('style')).toContain('width: 0%')
  })

  it('clamps score at 100', () => {
    const wrapper = mount(EnrichmentProgressBar, {
      props: { score: 120 },
    })
    const bar = wrapper.find('[data-testid="enrichment-bar-fill"]')
    expect(bar.attributes('style')).toContain('width: 100%')
  })
})
