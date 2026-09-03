// src/stores/chat.js
import { defineStore } from 'pinia';
import ragApi from '../api/rag';

let messageCounter = 0;
const nextId = () => `msg-${Date.now()}-${messageCounter++}`;

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [], // { id, role: 'user' | 'assistant', text, sources, timestamp, error }
    conversationId: null,
    isAsking: false,
    error: null,

    conversationList: [], // { id, preview, created_at }
    isLoadingList: false,
  }),

  getters: {
    hasMessages: (state) => state.messages.length > 0,
  },

  actions: {
    async askQuestion(question) {
      const trimmed = question.trim();
      if (!trimmed || this.isAsking) return;

      this.error = null;

      // Optimistically push the user's message
      this.messages.push({
        id: nextId(),
        role: 'user',
        text: trimmed,
        timestamp: new Date().toISOString(),
      });

      this.isAsking = true;

      try {
        const response = await ragApi.askQuestion(trimmed, this.conversationId);

        this.conversationId = response.conversation_id ?? this.conversationId;

        this.messages.push({
          id: nextId(),
          role: 'assistant',
          text: response.answer,
          sources: response.sources ?? [],
          timestamp: new Date().toISOString(),
        });
      } catch (err) {
        this.error = err?.message ?? 'Something went wrong answering that question.';
        this.messages.push({
          id: nextId(),
          role: 'assistant',
          text: null,
          error: this.error,
          timestamp: new Date().toISOString(),
        });
      } finally {
        this.isAsking = false;
      }
    },

    async loadConversation(conversationId) {
      this.error = null;
      try {
        const data = await ragApi.getConversation(conversationId);
        this.conversationId = conversationId;
        this.messages = data.messages ?? [];
      } catch (err) {
        this.error = err?.message ?? 'Could not load that conversation.';
      }
    },
    
    async fetchConversationList() {
      this.isLoadingList = true;
      try {
        this.conversationList = await ragApi.listConversations();
      } catch (err) {
        // Non-fatal — sidebar just stays empty/stale if this fails.
        console.error('Failed to load conversation list:', err);
      } finally {
        this.isLoadingList = false;
      }
    },
    startNewConversation() {
      this.messages = [];
      this.conversationId = null;
      this.error = null;
    },
  },
});
