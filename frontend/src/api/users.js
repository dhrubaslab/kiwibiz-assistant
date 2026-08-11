import request from './client'

export function listCompanyUsers() {
  return request('/api/users')
}

export function createStaff(payload) {
  return request('/api/users/staff', { method: 'POST', body: payload })
}

export function updateUserStatus(userId, isActive) {
  return request(`/api/users/${userId}/status`, { method: 'PATCH', body: { is_active: isActive } })
}