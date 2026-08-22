<template>
  <div v-if="sources && sources.length" class="source-tape">
    <div class="source-tape__label">SOURCES</div>
    <ul class="source-tape__list">
      <li
        v-for="(source, i) in sources"
        :key="source.document_id + '-' + i"
        class="source-tape__item"
      >
        <span class="source-tape__index">{{ String(i + 1).padStart(2, '0') }}</span>
        <span class="source-tape__name">{{ source.document_name }}</span>
        <span v-if="source.page_number" class="source-tape__page">p.{{ source.page_number }}</span>
        <span class="source-tape__score">{{ formatScore(source.score) }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup>
defineProps({
  sources: {
    type: Array,
    default: () => [],
  },
});

function formatScore(score) {
  if (typeof score !== 'number') return '';
  return `${Math.round(score * 100)}%`;
}
</script>

<style scoped>
.source-tape {
  margin-top: 0.75rem;
  border-top: 1px dashed var(--color-sand, #dcd6c9);
  padding-top: 0.5rem;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.7rem;
}

.source-tape__label {
  letter-spacing: 0.12em;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.5;
  margin-bottom: 0.35rem;
}

.source-tape__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.source-tape__item {
  display: grid;
  grid-template-columns: 1.4rem 1fr auto auto;
  gap: 0.5rem;
  align-items: baseline;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.75;
}

.source-tape__index {
  color: var(--color-teal, #1b6f63);
  opacity: 1;
}

.source-tape__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-tape__page {
  opacity: 0.6;
}

.source-tape__score {
  color: var(--color-amber, #e8a33d);
  font-weight: 600;
}
</style>