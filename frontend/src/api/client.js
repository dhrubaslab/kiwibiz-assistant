const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('kiwibiz_token')
}

async function request(path, { method = 'GET', body, isForm = false, auth = true } = {}) {
  const headers = {}
  if (!isForm) headers['Content-Type'] = 'application/json'
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let detail = 'Something went wrong.'
    try {
      const data = await res.json()
      detail = data.detail || detail
    } catch {}
    const err = new Error(detail)
    err.status = res.status
    throw err
  }

const contentType = res.headers.get('content-type')
if (res.status === 204 || !contentType) return null

if (contentType.includes('application/json')) {
  const text = await res.text()
  return text ? JSON.parse(text) : null
}

return res
}

export default request
export { BASE_URL }