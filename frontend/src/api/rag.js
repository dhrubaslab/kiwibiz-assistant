// src/api/rag.js
// RAG / document Q&A API module, following the same pattern as documents.js
// (thin wrapper around the centralised client in src/api/client.js)

import request from './client';

/**
 * Ask a question against the company's document corpus.
 * Expected backend endpoint: POST /api/rag/ask
 *
 * Request body:
 *   { question: string, conversation_id?: string }
 *
 * Expected response shape:
 *   {
 *     answer: string,
 *     conversation_id: string,
 *     sources: [
 *       {
 *         document_id: string,
 *         document_name: string,
 *         chunk_text: string,
 *         page_number: number | null,
 *         score: number
 *       }
 *     ]
 *   }
 */
export async function askQuestion(question, conversationId = null) {
  return request('/api/rag/ask', {
    method: 'POST',
    body: { question, conversation_id: conversationId },
  });
}

/**
 * Fetch prior turns for a conversation (for reload / history panel).
 * Expected backend endpoint: GET /api/rag/conversations/:id
 */
export async function getConversation(conversationId) {
  return request(`/api/rag/conversations/${conversationId}`);
}

/**
 * List a company's recent Q&A conversations (sidebar / history list).
 * Expected backend endpoint: GET /api/rag/conversations
 */
export async function listConversations() {
  return request('/api/rag/conversations');
}

export default {
  askQuestion,
  getConversation,
  listConversations,
};