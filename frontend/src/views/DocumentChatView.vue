<template>
  <div class="doc-chat-page">
    <ConversationSidebar
      :conversation-list="chatStore.conversationList"
      :active-conversation-id="chatStore.conversationId"
      :is-loading-list="chatStore.isLoadingList"
      @select="handleSelectConversation"
      @new="handleNewConversation"
    />

    <div class="doc-chat">
      <header class="doc-chat__header">
        <h1 class="doc-chat__title">Ask your documents</h1>
        <button
          v-if="chatStore.hasMessages"
          class="doc-chat__new"
          @click="handleNewConversation"
        >
          New conversation
        </button>
      </header>

      <div ref="scrollRef" class="doc-chat__scroll">
        <div v-if="!chatStore.hasMessages" class="doc-chat__empty">
          <p class="doc-chat__empty-title">No questions asked yet.</p>
          <p class="doc-chat__empty-body">
            Ask something like "What's our refund policy?" or "Summarise the Q3 supplier contract."
            Kiwi-Biz Assistant will search your company's documents and answer with sources attached.
          </p>
        </div>

        <ChatMessage
          v-for="message in chatStore.messages"
          :key="message.id"
          :message="message"
        />

        <div v-if="chatStore.isAsking" class="doc-chat__typing">
          <span class="doc-chat__typing-dot"></span>
          <span class="doc-chat__typing-dot"></span>
          <span class="doc-chat__typing-dot"></span>
        </div>
      </div>

      <div class="doc-chat__input">
        <ChatInput :disabled="chatStore.isAsking" @submit="handleAsk" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue';
import { useChatStore } from '../stores/chat';
import ChatMessage from '../components/chat/ChatMessage.vue';
import ChatInput from '../components/chat/ChatInput.vue';
import ConversationSidebar from '../components/chat/ConversationSidebar.vue';

const chatStore = useChatStore();
const scrollRef = ref(null);

async function handleAsk(question) {
  await chatStore.askQuestion(question);
}

async function handleSelectConversation(conversationId) {
  if (conversationId === chatStore.conversationId) return;
  await chatStore.loadConversation(conversationId);
}

function handleNewConversation() {
  chatStore.startNewConversation();
}

onMounted(() => {
  chatStore.fetchConversationList();
});

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick();
    if (scrollRef.value) {
      scrollRef.value.scrollTop = scrollRef.value.scrollHeight;
    }
  }
);
</script>

<style scoped>
.doc-chat-page {
  display: flex;
  gap: 1.5rem;
  height: 100%;
  max-width: 64rem;
  margin: 0 auto;
  padding: 1.5rem;
}

.doc-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  flex: 1;
  min-width: 0;
  gap: 1rem;
}

.doc-chat__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.doc-chat__title {
  font-family: var(--font-display, 'Fraunces', serif);
  font-size: 1.5rem;
  color: var(--color-pine, #0f1e1c);
  margin: 0;
}

.doc-chat__new {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.85rem;
  background: transparent;
  border: 1px solid var(--color-sand, #dcd6c9);
  border-radius: 0.5rem;
  padding: 0.4rem 0.75rem;
  color: var(--color-teal, #1b6f63);
  cursor: pointer;
}

.doc-chat__new:hover {
  background: var(--color-sand, #dcd6c9);
}

.doc-chat__scroll {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-right: 0.25rem;
}

.doc-chat__empty {
  margin: auto;
  text-align: center;
  max-width: 28rem;
  color: var(--color-pine, #0f1e1c);
}

.doc-chat__empty-title {
  font-family: var(--font-display, 'Fraunces', serif);
  font-size: 1.1rem;
  margin-bottom: 0.4rem;
}

.doc-chat__empty-body {
  font-family: var(--font-body, 'Inter', sans-serif);
  font-size: 0.9rem;
  opacity: 0.7;
  line-height: 1.5;
}

.doc-chat__typing {
  display: flex;
  gap: 0.3rem;
  padding: 0.75rem 1rem;
}

.doc-chat__typing-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 999px;
  background: var(--color-teal, #1b6f63);
  opacity: 0.5;
  animation: doc-chat-pulse 1.2s ease-in-out infinite;
}

.doc-chat__typing-dot:nth-child(2) {
  animation-delay: 0.15s;
}
.doc-chat__typing-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes doc-chat-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.85); }
  40% { opacity: 1; transform: scale(1); }
}

.doc-chat__input {
  flex-shrink: 0;
}
</style>