<template>
  <div class="chat-message" :class="message.role">
    <div class="chat-message__avatar">
      {{ message.role === 'user' ? 'You' : 'KB' }}
    </div>

    <div class="chat-message__body">
      <div v-if="message.error" class="chat-message__error">
        {{ message.error }}
      </div>
      <div v-else class="chat-message__text">
        {{ message.text }}
      </div>

      <SourceCitations v-if="message.role === 'assistant'" :sources="message.sources" />
    </div>
  </div>
</template>

<script setup>
import SourceCitations from './SourceCitations.vue';

defineProps({
  message: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
  border-radius: 0.75rem;
  max-width: 42rem;
}

.chat-message.user {
  margin-left: auto;
  flex-direction: row-reverse;
  background: var(--color-teal, #1b6f63);
  color: var(--color-paper, #f7f5f0);
}

.chat-message.assistant {
  margin-right: auto;
  background: var(--color-paper, #f7f5f0);
  border: 1px solid var(--color-sand, #dcd6c9);
  color: var(--color-pine, #0f1e1c);
}

.chat-message__avatar {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono, 'JetBrains Mono', monospace);
  font-size: 0.65rem;
  font-weight: 600;
}

.chat-message.user .chat-message__avatar {
  background: rgba(247, 245, 240, 0.2);
}

.chat-message.assistant .chat-message__avatar {
  background: var(--color-amber, #e8a33d);
  color: var(--color-pine, #0f1e1c);
}

.chat-message__text {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.95rem;
  line-height: 1.5;
  white-space: pre-wrap;
}

.chat-message__error {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.9rem;
  color: #b3261e;
}
</style>
