import request, { BASE_URL } from './client'

export function listDocuments() {
  return request('/api/documents')
}

export function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  return request('/api/documents/upload', { method: 'POST', body: form, isForm: true })
}

export function getDocument(id) {
  return request(`/api/documents/${id}`)
}
/**
 * Uploads a document with a category and reports progress via onProgress(percent).
 * Uses XMLHttpRequest directly because the fetch API (used by client.js) has
 * no upload progress event — XHR is the only way to get real percentage updates.
 */
export function uploadDocumentWithProgress(file, category, onProgress) {
  return new Promise((resolve, reject) => {
    const form = new FormData()
    form.append('file', file)
    form.append('category', category)

    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${BASE_URL}/api/documents/upload`)

    const token = localStorage.getItem('kiwibiz_token')
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    })

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText))
        } catch {
          resolve(null)
        }
      } else {
        let detail = 'Upload failed.'
        try {
          detail = JSON.parse(xhr.responseText)?.detail || detail
        } catch {}
        const err = new Error(detail)
        err.status = xhr.status
        reject(err)
      }
    }

    xhr.onerror = () => reject(new Error('Network error during upload.'))

    xhr.send(form)
  })
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

/**
 * Fetches a document's raw bytes as a Blob, for inline viewing (as opposed
 * to downloadDocument, which triggers a save-to-disk). Reuses the same
 * signed-URL flow: get the download link, then fetch the actual bytes.
 */
export async function getDocumentBlob(id) {
  const token = localStorage.getItem('kiwibiz_token')
 
  const linkRes = await fetch(`${BASE_URL}/api/documents/${id}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!linkRes.ok) throw new Error('Could not get file link.')
  const { download_url } = await linkRes.json()
 
  const fileUrl = download_url.startsWith('http') ? download_url : `${BASE_URL}${download_url}`
 
  const fileRes = await fetch(fileUrl)
  if (!fileRes.ok) throw new Error('Could not load file.')
 
  return fileRes.blob()
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