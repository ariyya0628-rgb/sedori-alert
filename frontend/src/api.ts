const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const TOKEN_STORAGE_KEY = "sedori_access_token";

export function getAccessToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function setAccessToken(token: string) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearAccessToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

function authHeaders(extra?: HeadersInit): HeadersInit {
  const token = getAccessToken();
  return {
    ...(extra || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

function apiFetch(path: string, init: RequestInit = {}) {
  return fetch(`${API_BASE}${path}`, {
    ...init,
    headers: authHeaders(init.headers),
  });
}

export type Keyword = {
  id: number;
  keyword: string;
  shop_code: string;
  min_price: number | null;
  max_price: number | null;
  include_terms: string;
  exclude_terms: string;
  allowed_condition_ranks: string;
  secondstreet_condition_ranks: string;
  offmall_condition_ranks: string;
  mandarake_condition_ranks: string;
  surugaya_condition_tags: string;
  enabled: boolean;
  created_at: string;
};

export type NotificationItem = {
  id: number;
  shop_code: string;
  product_title: string;
  product_url: string;
  matched_keyword: string;
  discord_status: string;
  discord_error: string | null;
  match_reason: string | null;
  skip_reason: string | null;
  notified_at: string;
};

export type Product = {
  id: number;
  shop_code: string;
  external_product_id: string;
  title: string;
  price: number;
  product_url: string;
  image_url: string | null;
  category: string | null;
  condition_rank: string | null;
  stock_status: string;
  detected_at: string;
};

export type CrawlLog = {
  id: number;
  shop_code: string;
  status: string;
  fetched_count: number;
  matched_count: number;
  notified_count: number;
  duplicates_skipped: number;
  error_message: string | null;
  started_at: string;
  finished_at: string;
};

export type SchedulerSetting = {
  enabled: boolean;
  shop_code: string;
  keyword: string;
  interval_minutes: number;
  limit: number;
  last_run_at: string | null;
  next_run_at: string | null;
};

export type SchedulerRunDueResult = {
  ran: boolean;
  reason: string | null;
  result: (MockCrawlerResult & { status: string; error_message: string | null }) | null;
};

export type KeywordWatchResult = {
  run_count: number;
  skipped_count: number;
  results: Array<{
    shop_code: string;
    keyword: string;
    result: MockCrawlerResult & { status: string; error_message: string | null };
  }>;
};

export type MockCrawlerResult = {
  fetched_count: number;
  matched_count: number;
  notifications_created: number;
  duplicates_skipped: number;
};

export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("ログインに失敗しました");
  return response.json();
}

export async function listKeywords(userId: number): Promise<Keyword[]> {
  const response = await apiFetch(`/api/keywords?user_id=${userId}`);
  if (!response.ok) throw new Error("キーワード取得に失敗しました");
  return response.json();
}

export type KeywordCreatePayload = {
  keyword: string;
  shop_code: string;
  min_price?: number | null;
  max_price?: number | null;
  include_terms?: string;
  exclude_terms?: string;
  allowed_condition_ranks?: string;
  secondstreet_condition_ranks?: string;
  offmall_condition_ranks?: string;
  mandarake_condition_ranks?: string;
  surugaya_condition_tags?: string;
};

export async function createKeyword(userId: number, payload: KeywordCreatePayload) {
  const response = await apiFetch(`/api/keywords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, ...payload }),
  });
  if (!response.ok) throw new Error("キーワード登録に失敗しました");
  return response.json();
}

export async function deleteKeyword(keywordId: number) {
  const response = await apiFetch(`/api/keywords/${keywordId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("キーワード削除に失敗しました");
}

export async function updateDiscordSettings(userId: number, webhookUrl: string, enabled: boolean) {
  const response = await apiFetch(`/api/notification-settings?user_id=${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ discord_webhook_url: webhookUrl || null, discord_enabled: enabled }),
  });
  if (!response.ok) throw new Error("Discord設定の保存に失敗しました");
  return response.json();
}

export async function testDiscord(userId: number) {
  const response = await apiFetch(`/api/notifications/test-discord?user_id=${userId}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("テスト通知に失敗しました");
  return response.json();
}

export async function listNotifications(userId: number): Promise<NotificationItem[]> {
  const response = await apiFetch(`/api/notifications?user_id=${userId}`);
  if (!response.ok) throw new Error("通知履歴の取得に失敗しました");
  return response.json();
}

export async function runMockCrawler(userId: number): Promise<MockCrawlerResult> {
  const response = await apiFetch(`/api/crawler/run-mock?user_id=${userId}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("モック巡回に失敗しました");
  return response.json();
}

export async function runShopCrawler(
  userId: number,
  shopCode: string,
  keyword: string,
  limit: number,
): Promise<MockCrawlerResult & { status: string; error_message: string | null }> {
  const params = new URLSearchParams({
    user_id: String(userId),
    shop_code: shopCode,
    keyword,
    limit: String(limit),
  });
  const response = await apiFetch(`/api/crawler/run-shop?${params.toString()}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("ショップ巡回に失敗しました");
  return response.json();
}

export async function runRegisteredKeywords(userId: number, limit: number): Promise<KeywordWatchResult> {
  const params = new URLSearchParams({
    user_id: String(userId),
    limit: String(limit),
  });
  const response = await apiFetch(`/api/crawler/run-keywords?${params.toString()}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("登録キーワード巡回に失敗しました");
  return response.json();
}

export async function listProducts(): Promise<Product[]> {
  const response = await apiFetch(`/api/products`);
  if (!response.ok) throw new Error("商品一覧の取得に失敗しました");
  return response.json();
}

export async function listCrawlLogs(): Promise<CrawlLog[]> {
  const response = await apiFetch(`/api/crawl-logs`);
  if (!response.ok) throw new Error("巡回ログの取得に失敗しました");
  return response.json();
}

export async function getSchedulerSetting(userId: number): Promise<SchedulerSetting> {
  const response = await apiFetch(`/api/scheduler/settings?user_id=${userId}`);
  if (!response.ok) throw new Error("スケジュール設定の取得に失敗しました");
  return response.json();
}

export async function saveSchedulerSetting(userId: number, setting: SchedulerSetting): Promise<SchedulerSetting> {
  const response = await apiFetch(`/api/scheduler/settings?user_id=${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(setting),
  });
  if (!response.ok) throw new Error("スケジュール設定の保存に失敗しました");
  return response.json();
}

export async function runDueScheduler(userId: number): Promise<SchedulerRunDueResult> {
  const response = await apiFetch(`/api/scheduler/run-due?user_id=${userId}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("期限到来分の実行に失敗しました");
  return response.json();
}
