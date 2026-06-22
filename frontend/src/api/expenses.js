import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

/**
 * 按维修记录编号查询花费列表
 * @param {number} recordId
 * @returns {Promise<import('axios').AxiosResponse<Array>>}
 */
export function fetchExpenses(recordId) {
  return client.get(`/records/${recordId}/expenses`)
}

/**
 * 新增花费
 * @param {object} payload
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function createExpense(payload) {
  return client.post('/expenses', payload)
}

/**
 * 删除花费
 * @param {number} id
 * @returns {Promise<import('axios').AxiosResponse<void>>}
 */
export function deleteExpense(id) {
  return client.delete(`/expenses/${id}`)
}
