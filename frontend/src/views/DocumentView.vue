<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import DocumentListSidebar from '@/components/DocumentListSidebar.vue'
import { getDocument, getDocumentBlob, downloadDocument, listDocuments } from '@/api/documents'

const route = useRoute()
const router = useRouter()

const currentId = computed(() => route.params.id)

const doc = ref(null)
const blobUrl = ref(null)
const textContent = ref(null)
const loading = ref(true)
const error = ref('')

const allDocuments = ref([])
const listLoading = ref(true)

const PREVIEWABLE_TEXT_TYPES = new Set(['text/plain', 'text/csv'])

const viewerKind = computed(() => {
  if (!doc.value) return null
  if (doc.value.content_type === 'application/pdf') return 'pdf'
  if (PREVIEWABLE_TEXT_TYPES.has(doc.value.content_type)) return 'text'
  return 'unsupported'
})

function cleanupBlobUrl() {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = null
  }
}

async function loadDocument(id) {
  loading.value = true
  error.value = ''
  cleanupBlobUrl()
  textContent.value = null

  try {
    doc.value = await getDocument(id)
    const blob = await getDocumentBlob(id)

    if (doc.value.content_type === 'application/pdf') {
      blobUrl.value = URL.createObjectURL(blob)
    } else if (PREVIEWABLE_TEXT_TYPES.has(doc.value.content_type)) {
      textContent.value = await blob.text()
    }
  } catch (e) {
    error.value = e.message || 'Could not load this document.'
  } finally {
    loading.value = false
  }
}

async function loadDocumentList() {
  listLoading.value = true
  try {
    allDocuments.value = await listDocuments()
  } catch {
    // Non-fatal — sidebar just stays empty if this fails.
  } finally {
    listLoading.value = false
  }
}

async function handleDownload() {
  if (!doc.value) return
  try {
    await downloadDocument(doc.value.id, doc.value.original_filename)
  } catch (e) {
    error.value = e.message
  }
}

function handleSelectDocument(id) {
  if (id === currentId.value) return
  router.push({ name: 'document-view', params: { id } })
}

// Route stays on the same component when switching between documents
// (only the :id param changes), so we watch it explicitly rather than
// relying on onMounted alone.
watch(currentId, (newId) => {
  if (newId) loadDocument(newId)
})

onMounted(() => {
  loadDocument(currentId.value)
  loadDocumentList()
})

onBeforeUnmount(cleanupBlobUrl)
</script>

<template>
  <AppShell>
    <RouterLink to="/dashboard" class="text-sm text-ink/60 hover:text-ink inline-block mb-4">
      ← Back to Documents
    </RouterLink>

    <div class="flex gap-6" style="height: 85vh;">
      <DocumentListSidebar
        :documents="allDocuments"
        :active-document-id="currentId"
        :is-loading="listLoading"
        @select="handleSelectDocument"
      />

      <div class="flex-1 min-w-0">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h2 class="font-display text-2xl">{{ doc?.original_filename || 'Loading…' }}</h2>
            <p v-if="doc" class="text-sm text-ink/60 mt-1">{{ doc.content_type }}</p>
          </div>
          <button
            v-if="doc"
            @click="handleDownload"
            class="text-sm font-medium text-harbour hover:underline"
          >
            Download
          </button>
        </div>

        <p v-if="error" class="text-sm text-danger mb-4">{{ error }}</p>
        <div v-if="loading" class="text-sm text-ink/50">Loading document…</div>

        <template v-else>
          <iframe
            v-if="viewerKind === 'pdf'"
            :src="blobUrl"
            class="w-full border border-sand rounded"
            style="height: 75vh;"
          />

          <pre
            v-else-if="viewerKind === 'text'"
            class="w-full border border-sand rounded p-4 text-sm font-mono overflow-auto whitespace-pre-wrap"
            style="max-height: 75vh;"
          >{{ textContent }}</pre>

          <div
            v-else-if="viewerKind === 'unsupported'"
            class="border border-dashed border-sand rounded p-10 text-center"
          >
            <p class="text-ink/60 text-sm mb-4">
              Preview isn't available for this file type yet. You can download it instead.
            </p>
            <button
              @click="handleDownload"
              class="bg-amber hover:bg-amber/90 text-ink font-medium text-sm px-4 py-2 rounded transition-colors"
            >
              Download document
            </button>
          </div>
        </template>
      </div>
    </div>
  </AppShell>
</template>