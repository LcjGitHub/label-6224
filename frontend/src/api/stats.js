import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
})

/**
 * 获取维修统计概览
 * @returns {Promise<import('axios').AxiosResponse<object>>}
 */
export function fetchRepairStats() {
  return client.get('/stats/repair')
}
