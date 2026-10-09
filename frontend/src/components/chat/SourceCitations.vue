<template>
  <div v-if="grouped.length" class="source-tape">
    <p v-for="g in grouped" :key="g.id" class="source-tape__line">
      <span class="source-tape__label">SOURCE</span>
      <span class="source-tape__name" :title="g.name">{{ g.name }}</span>
      <span v-if="g.pages.length" class="source-tape__pages">
        {{ g.pages.length > 1 ? 'pages' : 'page' }} {{ g.pages.join(', ') }}
      </span>
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  sources: {
    type: Array,
    default: () => [],
  },
});

// One entry per document, with unique page numbers in ascending order
const grouped = computed(() => {
  const map = new Map();
  for (const s of props.sources || []) {
    const id = s.document_id ?? s.document_name;
    if (!map.has(id)) {
      map.set(id, {
        id,
        name: (s.document_name || 'Document').replace(/\.pdf$/i, ''),
        pages: new Set(),
      });
    }
    if (s.page_number) map.get(id).pages.add(s.page_number);
  }
  return [...map.values()].map((g) => ({
    ...g,
    pages: [...g.pages].sort((a, b) => a - b),
  }));
});
</script>

<style scoped>
.source-tape {
  margin-top: 0.75rem;
  border-top: 1px dashed var(--color-sand, #dcd6c9);
  padding-top: 0.5rem;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.7rem;
  color: var(--color-pine, #0f1e1c);
}

.source-tape__line {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin: 0 0 0.2rem;
}

.source-tape__label {
  letter-spacing: 0.12em;
  opacity: 0.5;
  flex-shrink: 0;
}

.source-tape__name {
  opacity: 0.75;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

.source-tape__pages {
  color: var(--color-teal, #1b6f63);
  font-weight: 600;
  flex-shrink: 0;
}
</style>