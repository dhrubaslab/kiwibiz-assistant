<template>
  <form class="chat-input" @submit.prevent="submit">
    <textarea
      ref="textareaRef"
      v-model="draft"
      class="chat-input__field"
      rows="1"
      placeholder="Ask about your documents…"
      :disabled="disabled"
      @keydown.enter.exact.prevent="submit"
      @input="autoGrow"
    ></textarea>

    <button
      type="submit"
      class="chat-input__send"
      :disabled="disabled || !draft.trim()"
    >
      {{ disabled ? 'Asking…' : 'Ask' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['submit']);

const draft = ref('');
const textareaRef = ref(null);

function autoGrow() {
  const el = textareaRef.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
}

function submit() {
  const value = draft.value.trim();
  if (!value || props.disabled) return;
  emit('submit', value);
  draft.value = '';
  if (textareaRef.value) textareaRef.value.style.height = 'auto';
}
</script>

<style scoped>
.chat-input {
  display: flex;
  gap: 0.6rem;
  align-items: flex-end;
  padding: 0.75rem;
  border: 1px solid var(--color-sand, #dcd6c9);
  border-radius: 0.85rem;
  background: var(--color-paper, #f7f5f0);
}

.chat-input__field {
  flex: 1;
  resize: none;
  border: none;
  background: transparent;
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.95rem;
  line-height: 1.4;
  max-height: 160px;
  outline: none;
  color: var(--color-pine, #0f1e1c);
}

.chat-input__field:disabled {
  opacity: 0.6;
}

.chat-input__send {
  flex-shrink: 0;
  background: var(--color-teal, #1b6f63);
  color: var(--color-paper, #f7f5f0);
  border: none;
  border-radius: 0.6rem;
  padding: 0.55rem 1.1rem;
  font-family: var(--font-body, 'Inter', sans-serif);
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.chat-input__send:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.chat-input__send:not(:disabled):hover {
  opacity: 0.9;
}
</style>
