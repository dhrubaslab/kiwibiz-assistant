<template>
  <aside class="convo-sidebar">
    <div class="convo-sidebar__header">
      <span class="convo-sidebar__title">History</span>
      <button class="convo-sidebar__new" @click="handleNew">+ New</button>
    </div>

    <div class="convo-sidebar__list">
      <p v-if="isLoadingList" class="convo-sidebar__empty">Loading…</p>
      <p v-else-if="!conversationList.length" class="convo-sidebar__empty">
        No past conversations yet.
      </p>

      <button
        v-for="conv in conversationList"
        :key="conv.id"
        class="convo-sidebar__item"
        :class="{ 'convo-sidebar__item--active': conv.id === activeConversationId }"
        @click="$emit('select', conv.id)"
      >
        <span class="convo-sidebar__preview">{{ conv.preview }}</span>
        <span class="convo-sidebar__date">{{ formatDate(conv.created_at) }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  conversationList: {
    type: Array,
    default: () => [],
  },
  activeConversationId: {
    type: String,
    default: null,
  },
  isLoadingList: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['select', 'new']);

function handleNew() {
  emit('new');
}

function formatDate(isoString) {
  const date = new Date(isoString);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  if (isToday) {
    return date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  }
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
}
</script>

<style scoped>
.convo-sidebar {
  width: 15rem;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-sand, #dcd6c9);
  padding-right: 1rem;
  height: 100%;
}

.convo-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.convo-sidebar__title {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.5;
}

.convo-sidebar__new {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.75rem;
  background: transparent;
  border: 1px solid var(--color-sand, #dcd6c9);
  border-radius: 0.4rem;
  padding: 0.25rem 0.55rem;
  color: var(--color-teal, #1b6f63);
  cursor: pointer;
}

.convo-sidebar__new:hover {
  background: var(--color-sand, #dcd6c9);
}

.convo-sidebar__list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.convo-sidebar__empty {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.8rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.5;
}

.convo-sidebar__item {
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

.convo-sidebar__item:hover {
  background: var(--color-sand, #dcd6c9);
}

.convo-sidebar__item--active {
  background: var(--color-paper, #f7f5f0);
  border: 1px solid var(--color-teal, #1b6f63);
}

.convo-sidebar__preview {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.82rem;
  color: var(--color-pine, #0f1e1c);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.convo-sidebar__date {
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.65rem;
  color: var(--color-pine, #0f1e1c);
  opacity: 0.45;
}
</style>