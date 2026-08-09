import request, { BASE_URL } from './client'

export function listDocuments() {
  return request('/api/documents')
}

export function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  return request('/api/documents/upload', { method: 'POST', body: form, isForm: true })
}

export function deleteDocument(id) {
  return request(`/api/documents/${id}`, { method: 'DELETE' })
}

export async function downloadDocument(id, filename) {
  const token = localStorage.getItem('kiwibiz_token')

  const linkRes = await fetch(`${BASE_URL}/api/documents/${id}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!linkRes.ok) throw new Error('Could not get download link.')
  const { download_url } = await linkRes.json()

  const fileUrl = download_url.startsWith('http') ? download_url : `${BASE_URL}${download_url}`

  const fileRes = await fetch(fileUrl)
  if (!fileRes.ok) throw new Error('Download failed.')

  const blob = await fileRes.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = timestampedFilename(filename)
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}

function timestampedFilename(filename) {
  if (!filename) return `document_${timestamp()}`
  const dotIndex = filename.lastIndexOf('.')
  if (dotIndex === -1) return `${filename}_${timestamp()}`
  return `${filename.slice(0, dotIndex)}_${timestamp()}${filename.slice(dotIndex)}`
}

function timestamp() {
  const d = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}`
}