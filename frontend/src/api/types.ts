export type MessageRole = "user" | "assistant" | "owner";

export interface SourceReference {
  source_id?: string;
  title?: string;
  url?: string;
  published_at?: string;
  observed_at?: string;
}

export interface ConversationMessage {
  role: MessageRole;
  content: string;
  sources: SourceReference[];
  created_at?: string;
}

export interface ConversationSummary {
  id: string;
  message_count: number;
  preview: string;
  updated_at?: string;
}

export interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  source_url: string;
  observed_at?: string;
  status: "active" | "draft" | "packaged";
}

export interface ChunkDetail {
  id: string;
  chunk_id: string;
  document_id?: string;
  source_id?: string;
  title: string;
  content: string;
  source_path?: string;
  source_url?: string;
  published_at?: string;
  observed_at?: string;
  content_sha256?: string;
  ordinal?: number;
}

export interface GapQuestion {
  question_id: string;
  question: string;
  category: string;
  time_scope: string;
  status: string;
  unique_source_count: number;
  evidence_urls: string[];
  answer_hint: string;
  custom?: boolean;
  managed_answer?: KnowledgeItem;
}
