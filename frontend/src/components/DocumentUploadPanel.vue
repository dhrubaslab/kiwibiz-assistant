<template>
  <div class="upload-panel">
    <div
      class="upload-panel__dropzone"
      :class="{ 'upload-panel__dropzone--active': isDragging }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        class="upload-panel__hidden-input"
        @change="handleFileSelect"
      />

      <template v-if="!selectedFile">
        <p class="upload-panel__hint">Drag a file here, or click to browse</p>
        <p class="upload-panel__hint-sub">PDF, DOCX, TXT, CSV, XLSX — up to 20MB</p>
      </template>
      <template v-else>
        <p class="upload-panel__filename">{{ selectedFile.name }}</p>
        <p class="upload-panel__hint-sub">{{ formatSize(selectedFile.size) }}</p>
      </template>
    </div>

    <div class="upload-panel__controls">
      <label class="upload-panel__label">
        Category
        <select v-model="category" class="upload-panel__select" :disabled="isUploading">
          <option v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </label>

      <button
        class="upload-panel__submit"
        :disabled="!selectedFile || isUploading"
        @click="handleUpload"
      >
        {{ isUploading ? `Uploading… ${progress}%` : 'Upload' }}
      </button>
    </div>

    <div v-if="isUploading" class="upload-panel__progress-track">
      <div class="upload-panel__progress-fill" :style="{ width: progress + '%' }"></div>
    </div>

    <p v-if="error" class="upload-panel__error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { uploadDocumentWithProgress } from '@/api/documents';

const emit = defineEmits(['uploaded']);

const categoryOptions = [
  { value: 'policy', label: 'Policy' },
  { value: 'contract', label: 'Contract' },
  { value: 'financial', label: 'Financial' },
  { value: 'hr', label: 'HR' },
  { value: 'other', label: 'Other' },
];

const fileInput = ref(null);
const selectedFile = ref(null);
const category = ref('other');
const isDragging = ref(false);
const isUploading = ref(false);
const progress = ref(0);
const error = ref('');

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) selectedFile.value = file;
}

function handleDrop(e) {
  isDragging.value = false;
  const file = e.dataTransfer.files[0];
  if (file) selectedFile.value = file;
}

async function handleUpload() {
  if (!selectedFile.value || isUploading.value) return;

  isUploading.value = true;
  progress.value = 0;
  error.value = '';

  try {
    await uploadDocumentWithProgress(selectedFile.value, category.value, (pct) => {
      progress.value = pct;
    });
    selectedFile.value = null;
    category.value = 'other';
    if (fileInput.value) fileInput.value.value = '';
    emit('uploaded');
  } catch (err) {
    error.value = err.message || 'Upload failed.';
  } finally {
    isUploading.value = false;
  }
}

function formatSize(bytes) {
  const kb = bytes / 1024;
  return kb > 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb.toFixed(0)} KB`;
}
</script>

<style scoped>
.upload-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 22rem;
  max-width: 100%;
}

.upload-panel__dropzone {
  border: 2px dashed var(--color-sand, #dcd6c9);
  border-radius: 0.6rem;
  padding: 1.5rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.upload-panel__dropzone:hover,
.upload-panel__dropzone--active {
  border-color: var(--color-teal, #1b6f63);
  background: rgba(27, 111, 99, 0.04);
}

.upload-panel__hidden-input {
  display: none;
}

.upload-panel__hint {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.9rem;
  color: var(--color-pine, #0f1e1c);
  margin: 0 0 0.2rem 0;
}

.upload-panel__hint-sub {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.75rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.55;
  margin: 0;
}

.upload-panel__filename {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.85rem;
  color: var(--color-teal, #1b6f63);
  margin: 0 0 0.2rem 0;
  word-break: break-all;
}

.upload-panel__controls {
  display: flex;
  align-items: flex-end;
  gap: 0.6rem;
}

.upload-panel__label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.75rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.7;
  flex: 1;
}

.upload-panel__select {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.85rem;
  border: 1px solid var(--color-sand, #dcd6c9);
  border-radius: 0.4rem;
  padding: 0.4rem 0.5rem;
  background: white;
  color: var(--color-pine, #0f1e1c);
}

.upload-panel__submit {
  background: var(--color-amber, #e8a33d);
  color: var(--color-pine, #0f1e1c);
  border: none;
  border-radius: 0.4rem;
  padding: 0.5rem 1rem;
  font-family: var(--font-body, 'Inter', sans-serif);
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
}

.upload-panel__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.upload-panel__submit:not(:disabled):hover {
  background: var(--color-amber, #e8a33d);
  opacity: 0.9;
}

.upload-panel__progress-track {
  height: 0.35rem;
  background: var(--color-sand, #dcd6c9);
  border-radius: 999px;
  overflow: hidden;
}

.upload-panel__progress-fill {
  height: 100%;
  background: var(--color-teal, #1b6f63);
  transition: width 0.2s ease;
}

.upload-panel__error {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.8rem;
  color: #b3261e;
  margin: 0;
}
</style>
