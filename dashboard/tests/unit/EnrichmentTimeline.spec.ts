import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EnrichmentTimeline from '../../components/EnrichmentTimeline.vue'

const sampleEnrichments = [
  {
    timestamp: 1707600000000,
    source: 'pipeline',
    agentName: 'audience-researcher',
    field: 'awarenessStage',
    previousValue: undefined,
    newValue: '"problem_aware"',
    confidence: 'high',
    reasoning: 'Detected from pain points analysis',
  },
  {
    timestamp: 1707610000000,
    source: 'pipeline',
    agentName: 'enrichment-agent',
    field: 'purchaseBehavior',
    previousValue: '{"priceRange":"$50-100"}',
    newValue: '{"priceRange":"$50-150","buyingTriggers":["seasonal"]}',
    confidence: 'medium',
    reasoning: 'Updated from competitor analysis',
  },
  {
    timestamp: 1707620000000,
    source: 'manual',
    agentName: 'system',
    field: 'negativeTriggers',
    previousValue: undefined,
    newValue: '{"dealBreakers":["high cost"]}',
    confidence: 'low',
    reasoning: 'Added manually by user',
  },
]

describe('EnrichmentTimeline', () => {
  it('renders an entry for each enrichment', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: sampleEnrichments },
    })
    const entries = wrapper.findAll('[data-testid="timeline-entry"]')
    expect(entries).toHaveLength(3)
  })

  it('shows agent name for each entry', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: sampleEnrichments },
    })
    expect(wrapper.text()).toContain('audience-researcher')
    expect(wrapper.text()).toContain('enrichment-agent')
  })

  it('shows field name for each entry', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: sampleEnrichments },
    })
    expect(wrapper.text()).toContain('awarenessStage')
    expect(wrapper.text()).toContain('purchaseBehavior')
  })

  it('shows reasoning text', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: sampleEnrichments },
    })
    expect(wrapper.text()).toContain('Detected from pain points analysis')
  })

  it('uses green dot for high confidence', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: [sampleEnrichments[0]] },
    })
    const dot = wrapper.find('[data-testid="confidence-dot"]')
    expect(dot.classes()).toContain('bg-green-500')
  })

  it('uses yellow dot for medium confidence', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: [sampleEnrichments[1]] },
    })
    const dot = wrapper.find('[data-testid="confidence-dot"]')
    expect(dot.classes()).toContain('bg-yellow-500')
  })

  it('uses red dot for low confidence', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: [sampleEnrichments[2]] },
    })
    const dot = wrapper.find('[data-testid="confidence-dot"]')
    expect(dot.classes()).toContain('bg-red-500')
  })

  it('shows empty state when no enrichments', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: [] },
    })
    expect(wrapper.text()).toContain('No enrichment history')
  })

  it('sorts enrichments by timestamp descending (newest first)', () => {
    const wrapper = mount(EnrichmentTimeline, {
      props: { enrichments: sampleEnrichments },
    })
    const entries = wrapper.findAll('[data-testid="timeline-entry"]')
    // First entry should be the newest (negativeTriggers at 1707620000000)
    expect(entries[0].text()).toContain('negativeTriggers')
  })
})
