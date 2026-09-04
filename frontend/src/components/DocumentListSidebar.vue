<template>
  <aside class="doc-list-sidebar">
    <div class="doc-list-sidebar__header">Documents</div>

    <div class="doc-list-sidebar__list">
      <p v-if="isLoading" class="doc-list-sidebar__empty">Loading…</p>
      <p v-else-if="!documents.length" class="doc-list-sidebar__empty">No documents yet.</p>

      <button
        v-for="doc in documents"
        :key="doc.id"
        class="doc-list-sidebar__item"
        :class="{ 'doc-list-sidebar__item--active': doc.id === activeDocumentId }"
        @click="$emit('select', doc.id)"
      >
        <span class="doc-list-sidebar__name">{{ doc.original_filename }}</span>
        <span class="doc-list-sidebar__category">{{ doc.category }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  documents: {
    type: Array,
    default: () => [],
  },
  activeDocumentId: {
    type: String,
    default: null,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['select']);
</script>

<style scoped>
.doc-list-sidebar {
  width: 15rem;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-sand, #dcd6c9);
  padding-right: 1rem;
  max-height: 85vh;
}

.doc-list-sidebar__header {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.5;
  margin-bottom: 0.75rem;
}

.doc-list-sidebar__list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.doc-list-sidebar__empty {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.8rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.5;
}

.doc-list-sidebar__item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.15rem;
  text-align: left;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  padding: 0.5rem 0.6rem;
  cursor: pointer;
  width: 100%;
}

.doc-list-sidebar__item:hover {
  background: var(--color-sand, #dcd6c9);
}

.doc-list-sidebar__item--active {
  background: var(--color-paper, #f7f5f0);
  border: 1px solid var(--color-teal, #1b6f63);
}

.doc-list-sidebar__name {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.82rem;
  color: var(--color-pine, #0f1e1c);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.doc-list-sidebar__category {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.65rem;
  color: var(--color-teal, #1b6f63);
  opacity: 0.7;
  text-transform: uppercase;
}
</style>