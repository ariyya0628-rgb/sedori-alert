const API_BASE = "http://localhost:8000";

export type Keyword = {
  id: number;
  keyword: string;
  shop_code: string;
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
  const response = await fetch(`${API_BASE}/api/keywords?user_id=${userId}`);
  if (!response.ok) throw new Error("キーワード取得に失敗しました");
  return response.json();
}

export async function createKeyword(userId: number, keyword: string, shopCode: string) {
  const response = await fetch(`${API_BASE}/api/keywords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, keyword, shop_code: shopCode }),
  });
  if (!response.ok) throw new Error("キーワード登録に失敗しました");
  return response.json();
}

export async function deleteKeyword(keywordId: number) {
  const response = await fetch(`${API_BASE}/api/keywords/${keywordId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("キーワード削除に失敗しました");
}

export async function updateDiscordSettings(userId: number, webhookUrl: string, enabled: boolean) {
  const response = await fetch(`${API_BASE}/api/notification-settings?user_id=${userId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ discord_webhook_url: webhookUrl || null, discord_enabled: enabled }),
  });
  if (!response.ok) throw new Error("Discord設定の保存に失敗しました");
  return response.json();
}

export async function testDiscord(userId: number) {
  const response = await fetch(`${API_BASE}/api/notifications/test-discord?user_id=${userId}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("テスト通知に失敗しました");
  return response.json();
}

export async function listNotifications(userId: number): Promise<NotificationItem[]> {
  const response = await fetch(`${API_BASE}/api/notifications?user_id=${userId}`);
  if (!response.ok) throw new Error("通知履歴の取得に失敗しました");
  return response.json();
}

export async function runMockCrawler(userId: number): Promise<MockCrawlerResult> {
  const response = await fetch(`${API_BASE}/api/crawler/run-mock?user_id=${userId}`, {
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
  const response = await fetch(`${API_BASE}/api/crawler/run-shop?${params.toString()}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("ショップ巡回に失敗しました");
  return response.json();
}

export async function listProducts(): Promise<Product[]> {
  const response = await fetch(`${API_BASE}/api/products`);
  if (!response.ok) throw new Error("商品一覧の取得に失敗しました");
  return response.json();
}

export async function listCrawlLogs(): Promise<CrawlLog[]> {
  const response = await fetch(`${API_BASE}/api/crawl-logs`);
  if (!response.ok) throw new Error("巡回ログの取得に失敗しました");
  return response.json();
}

export async function getSchedulerSetting(userId: number): Promise<SchedulerSetting> {
  const response = await fetch(`${API_BASE}/api/scheduler/settings?user_id=${userId}`);
  if (!response.ok) throw new Error("スケジュール設定の取得に失敗しました");
  return response.json();
}

export async function saveSchedulerSetting(userId: number, setting: SchedulerSetting): Promise<SchedulerSetting> {
  const response = await fetch(`${API_BASE}/api/scheduler/settings?user_id=${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(setting),
  });
  if (!response.ok) throw new Error("スケジュール設定の保存に失敗しました");
  return response.json();
}

export async function runDueScheduler(userId: number): Promise<SchedulerRunDueResult> {
  const response = await fetch(`${API_BASE}/api/scheduler/run-due?user_id=${userId}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("期限到来分の実行に失敗しました");
  return response.json();
}
