import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

/**
 * 获取全部工具
 * @returns {Promise<import('axios').AxiosResponse<Array>>}
 */
export function fetchTools() {
  return client.get('/tools')
}

/**
 * 新建工具
 * @param {object} payload
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function createTool(payload) {
  return client.post('/tools', payload)
}

/**
 * 更新工具
 * @param {number} id
 * @param {object} payload
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function updateTool(id, payload) {
  return client.put(`/tools/${id}`, payload)
}

/**
 * 删除工具
 * @param {number} id
 * @returns {Promise<import('axios').AxiosResponse<void>>}
 */
export function deleteTool(id) {
  return client.delete(`/tools/${id}`)
}
