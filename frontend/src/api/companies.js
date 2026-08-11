import request from './client'

export function getMyCompany() {
  return request('/api/companies/me')
}

export function updateMyCompany(payload) {
  return request('/api/companies/me', { method: 'PATCH', body: payload })
}

export function listCompanies() {
  return request('/api/companies')
}

export function createCompany(payload) {
  return request('/api/companies', { method: 'POST', body: payload })
}

export function getCompany(id) {
  return request(`/api/companies/${id}`)
}

export function updateCompany(id, payload) {
  return request(`/api/companies/${id}`, { method: 'PATCH', body: payload })
}

export function updateSubscription(companyId, payload) {
  return request(`/api/companies/${companyId}/subscription`, { method: 'PATCH', body: payload })
}