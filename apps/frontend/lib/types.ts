/** Mirrors backend DTOs used by the admin UI (Phase 8). */

export type ThemeItem = {
  name: string;
  volume_hint?: string | null;
  frequency_rank?: number | null;
};

export type QuoteItem = {
  theme: string;
  quote: string;
  review_id?: string | null;
};

export type AnalysisJson = {
  themes: ThemeItem[];
  top_3_theme_names: string[];
  quotes: QuoteItem[];
};

export type PulseMeta = {
  reviews_sampled: number;
  groq_model: string;
  gemini_model: string;
  generated_at_iso: string;
  note_word_count: number;
};

export type FeeExplainerBlock = {
  fee_scenario: string;
  explanation_bullets: string[];
  source_links: string[];
  last_checked_iso: string;
};

export type PulseGenerateResponse = {
  analysis: AnalysisJson;
  weekly_note: string;
  actions: string[];
  meta: PulseMeta;
  fee: FeeExplainerBlock | null;
};

export type AsOnBlock = {
  iso_utc: string;
  display: string;
};

export type DocAppendPayload = {
  date: string;
  weekly_pulse: string;
  fee_scenario: string;
  explanation_bullets: string[];
  source_links: string[];
  last_checked_iso: string;
  weekly_pulse_n: number | null;
};

export type EmailPreview = {
  subject: string;
  body_plain: string;
  body_html: string;
  /** Must be `"2"` for PM email labels (TOP 3 CUSTOMER THEMES, etc.). If missing/wrong, restart backend. */
  format_version: string;
};

export type PreviewCreateResponse = {
  /** Must be `"2"` for current PM email template — duplicated at root for quick checks */
  email_template_version: string;
  weekly_pulse_n: number;
  as_on: AsOnBlock;
  pulse: PulseGenerateResponse;
  doc_append: DocAppendPayload;
  email: EmailPreview;
  doc_block_plain: string;
};

export type SubscriberRecord = {
  email: string;
  subscribed_at_iso: string;
};

export type SubscribersListResponse = {
  subscribers: SubscriberRecord[];
  count: number;
};

export type GoogleDocAppendResponse = {
  document_id: string;
  document_url: string;
  inserted_char_count: number;
};

export type GmailSendResponse = {
  sent_to: string[];
  rejected: string[];
  message: string;
};
