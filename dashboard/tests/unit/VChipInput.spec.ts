import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VChipInput from '../../components/VChipInput.vue'

describe('VChipInput', () => {
  it('renders existing chips', () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['vue', 'nuxt'] },
    })
    const chips = wrapper.findAll('.rounded-full')
    expect(chips).toHaveLength(2)
    expect(chips[0].text()).toContain('vue')
    expect(chips[1].text()).toContain('nuxt')
  })

  it('adds a chip on Enter keydown', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['existing'] },
    })
    const input = wrapper.find('input')
    await input.setValue('new-tag')
    await input.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([['existing', 'new-tag']])
  })

  it('does not add duplicate chips', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['vue'] },
    })
    const input = wrapper.find('input')
    await input.setValue('vue')
    await input.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('does not add empty strings', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: [] },
    })
    const input = wrapper.find('input')
    await input.setValue('   ')
    await input.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('removes chip when X button is clicked', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['vue', 'nuxt', 'vite'] },
    })
    // Click the remove button on the second chip (nuxt)
    const removeButtons = wrapper.findAll('.rounded-full button')
    await removeButtons[1].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([['vue', 'vite']])
  })

  it('removes last chip on Backspace when input is empty', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['vue', 'nuxt'] },
    })
    const input = wrapper.find('input')
    await input.setValue('')
    await input.trigger('keydown', { key: 'Backspace' })
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([['vue']])
  })

  it('shows placeholder when no chips', () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: [], placeholder: 'Add tags...' },
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Add tags...')
  })

  it('hides placeholder when chips exist', () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: ['vue'], placeholder: 'Add tags...' },
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('')
  })

  it('clears input after adding a chip', async () => {
    const wrapper = mount(VChipInput, {
      props: { modelValue: [] },
    })
    const input = wrapper.find('input')
    await input.setValue('test')
    await input.trigger('keydown', { key: 'Enter' })
    // Input should be cleared (via v-model with inputValue ref)
    expect((input.element as HTMLInputElement).value).toBe('')
  })
})
