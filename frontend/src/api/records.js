import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

/**
 * 获取全部维修记录
 * @returns {Promise<import('axios').AxiosResponse<Array>>}
 */
export function fetchRecords() {
  return client.get('/records')
}

/**
 * 新建维修记录
 * @param {object} payload
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function createRecord(payload) {
  return client.post('/records', payload)
}

/**
 * 更新维修记录
 * @param {number} id
 * @param {object} payload
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function updateRecord(id, payload) {
  return client.put(`/records/${id}`, payload)
}

/**
 * 删除维修记录
 * @param {number} id
 * @returns {Promise<import('axios').AxiosResponse<void>>}
 */
export function deleteRecord(id) {
  return client.delete(`/records/${id}`)
}
