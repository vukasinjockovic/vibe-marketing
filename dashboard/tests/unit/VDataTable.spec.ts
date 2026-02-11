import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VDataTable from '../../components/VDataTable.vue'

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'date', label: 'Date' },
]

const rows = [
  { _id: '1', name: 'Task A', status: 'active', date: '2026-01-01' },
  { _id: '2', name: 'Task B', status: 'completed', date: '2026-01-02' },
]

describe('VDataTable', () => {
  it('renders table headers from columns', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows },
    })
    const headers = wrapper.findAll('th')
    expect(headers).toHaveLength(3)
    expect(headers[0].text()).toBe('Name')
    expect(headers[1].text()).toBe('Status')
    expect(headers[2].text()).toBe('Date')
  })

  it('renders table rows from data', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows },
    })
    const trs = wrapper.findAll('tbody tr')
    expect(trs).toHaveLength(2)
  })

  it('renders cell values by default', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows },
    })
    const cells = wrapper.findAll('tbody td')
    expect(cells[0].text()).toBe('Task A')
    expect(cells[1].text()).toBe('active')
  })

  it('renders scoped cell slot when provided', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows },
      slots: {
        'cell-status': ({ value }: { value: string }) => `[${value}]`,
      },
    })
    const cells = wrapper.findAll('tbody td')
    expect(cells[1].text()).toBe('[active]')
  })

  it('shows loading state', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows: [], loading: true },
    })
    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.find('table').exists()).toBe(false)
  })

  it('shows empty message when no rows and not loading', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows: [] },
    })
    expect(wrapper.text()).toContain('No data found.')
  })

  it('shows custom empty message', () => {
    const wrapper = mount(VDataTable, {
      props: { columns, rows: [], emptyMessage: 'No tasks yet.' },
    })
    expect(wrapper.text()).toContain('No tasks yet.')
  })

  it('applies column class to th and td', () => {
    const columnsWithClass = [
      { key: 'name', label: 'Name', class: 'w-1/2' },
      { key: 'status', label: 'Status' },
    ]
    const wrapper = mount(VDataTable, {
      props: { columns: columnsWithClass, rows: [{ _id: '1', name: 'A', status: 'active' }] },
    })
    expect(wrapper.find('th').classes()).toContain('w-1/2')
    expect(wrapper.find('td').classes()).toContain('w-1/2')
  })
})
