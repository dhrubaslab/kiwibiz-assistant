<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppShell from '@/layouts/AppShell.vue'
import { listDocuments, deleteDocument, downloadDocument } from '@/api/documents'
import { getMyCompany } from '@/api/companies'
import DocumentUploadPanel from '@/components/DocumentUploadPanel.vue'

const auth = useAuthStore()
const company = ref(null)
const documents = ref([])
const loading = ref(true)
const error = ref('')
const showUploadPanel = ref(false)
const selectedCategory = ref('all')

const CATEGORY_LABELS = {
  policy: 'Policy',
  contract: 'Contract',
  financial: 'Financial',
  hr: 'HR',
  other: 'Other',
}

const filteredDocuments = computed(() => {
  if (selectedCategory.value === 'all') return documents.value
  return documents.value.filter((d) => d.category === selectedCategory.value)
})

async function loadDocuments() {
  loading.value = true
  try {
    documents.value = await listDocuments()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function handleUploaded() {
  showUploadPanel.value = false
  await loadDocuments()
}

async function handleDelete(id) {
  try {
    await deleteDocument(id)
    documents.value = documents.value.filter((d) => d.id !== id)
  } catch (e) {
    error.value = e.message
  }
}

async function handleDownload(doc) {
  try {
    await downloadDocument(doc.id, doc.original_filename)
  } catch (e) {
    error.value = e.message
  }
}

function formatSize(bytes) {
  if (!bytes) return '—'
  const kb = bytes / 1024
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-NZ', {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function categoryLabel(category) {
  return CATEGORY_LABELS[category] || category
}
const CONTENT_TYPE_LABELS = {
  'application/pdf': 'PDF',
  'text/plain': 'TXT',
  'text/csv': 'CSV',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
}

function fileTypeLabel(contentType) {
  return CONTENT_TYPE_LABELS[contentType] || contentType?.split('/').pop()?.toUpperCase() || '—'
}
onMounted(() => {
  auth.fetchMe().catch(() => {})
  loadDocuments()
  getMyCompany().then((c) => { company.value = c }).catch(() => {})
})
</script>

<template>
  <AppShell>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="font-display text-2xl">Documents</h2>
        <p class="text-sm text-ink/60 mt-1 flex items-center gap-2">
          <span>{{ company?.name }}</span>
          <span v-if="auth.user?.role" class="text-xs uppercase tracking-wide bg-sand text-ink/70 px-2 py-0.5 rounded-full font-mono">
            {{ auth.user.role.replace('_', ' ') }}
          </span>
        </p>
      </div>

      <button
        class="bg-amber hover:bg-amber/90 text-ink font-medium text-sm px-4 py-2 rounded transition-colors"
        @click="showUploadPanel = !showUploadPanel"
      >
        {{ showUploadPanel ? 'Cancel' : '+ Upload document' }}
      </button>
    </div>

    <div v-if="showUploadPanel" class="mb-8">
      <DocumentUploadPanel @uploaded="handleUploaded" />
    </div>

    <div class="mb-6 flex items-center gap-2">
      <label class="text-sm text-ink/60 flex items-center gap-2">
        Filter by category
        <select v-model="selectedCategory" class="border border-sand rounded px-2 py-1 text-sm">
          <option value="all">All</option>
          <option value="policy">Policy</option>
          <option value="contract">Contract</option>
          <option value="financial">Financial</option>
          <option value="hr">HR</option>
          <option value="other">Other</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="text-sm text-danger mb-4">{{ error }}</p>
    <div v-if="loading" class="text-sm text-ink/50">Loading…</div>

    <div v-else-if="filteredDocuments.length === 0" class="border border-dashed border-sand rounded p-10 text-center">
      <p class="text-ink/60 text-sm">
        {{ selectedCategory === 'all' ? 'No documents yet. Upload your first file to get started.' : 'No documents in this category.' }}
      </p>
    </div>

    <table v-else class="w-full text-sm">
      <thead>
        <tr class="border-b border-sand text-left text-ink/50">
          <th class="py-2 font-medium">Name</th>
          <th class="py-2 font-medium">Category</th>
          <th class="py-2 font-medium">Uploaded by</th>
          <th class="py-2 font-medium">Type</th>
          <th class="py-2 font-medium font-mono">Size</th>
          <th class="py-2 font-medium">Uploaded</th>
          <th class="py-2 font-medium"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in filteredDocuments" :key="doc.id" class="border-b border-sand/60">
          <td class="py-3">{{ doc.original_filename }}</td>
          <td class="py-3">
            <span class="text-xs uppercase tracking-wide bg-sand text-ink/70 px-2 py-0.5 rounded-full font-mono">
              {{ categoryLabel(doc.category) }}
            </span>
          </td>
          <td class="py-3 text-ink/60">{{ doc.owner_email }}</td>
          <td class="py-3 text-ink/60">{{ fileTypeLabel(doc.content_type) }}</td>
          <td class="py-3 font-mono text-ink/60">{{ formatSize(doc.file_size_bytes) }}</td>
          <td class="py-3 text-ink/60">{{ formatDate(doc.uploaded_at) }}</td>
          <td class="py-3 text-right space-x-3">
            <RouterLink
              :to="{ name: 'document-view', params: { id: doc.id } }"
              class="text-harbour hover:underline"
            >
              View
            </RouterLink>
            <button @click="handleDownload(doc)" class="text-harbour hover:underline">Download</button>
            <button @click="handleDelete(doc.id)" class="text-danger hover:underline">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </AppShell>
</template>