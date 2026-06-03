import { useState } from "react";
import { KeywordWatchResult, MockCrawlerResult, runMockCrawler, runRegisteredKeywords, runShopCrawler } from "../api";

export function DashboardPage({ userId }: { userId: number }) {
  const [result, setResult] = useState<MockCrawlerResult | null>(null);
  const [shopResult, setShopResult] = useState<(MockCrawlerResult & { status: string; error_message: string | null }) | null>(null);
  const [keywordWatchResult, setKeywordWatchResult] = useState<KeywordWatchResult | null>(null);
  const [shopCode, setShopCode] = useState("offmall");
  const [keyword, setKeyword] = useState("レコルト");
  const [limit, setLimit] = useState(5);
  const [error, setError] = useState("");

  async function runMock() {
    setError("");
    setResult(null);
    try {
      setResult(await runMockCrawler(userId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "モック巡回に失敗しました");
    }
  }

  async function runShop() {
    setError("");
    setShopResult(null);
    try {
      setShopResult(await runShopCrawler(userId, shopCode, keyword, limit));
    } catch (err) {
      setError(err instanceof Error ? err.message : "ショップ巡回に失敗しました");
    }
  }

  async function runKeywords() {
    setError("");
    setKeywordWatchResult(null);
    try {
      setKeywordWatchResult(await runRegisteredKeywords(userId, limit));
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録キーワード巡回に失敗しました");
    }
  }

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>ダッシュボード</h2>
      </div>
      <div className="metricGrid">
        <div className="card metricCard">
          <span>本日の通知</span>
          <strong>0</strong>
        </div>
        <div className="card metricCard">
          <span>登録キーワード</span>
          <strong>キーワード画面で確認</strong>
        </div>
        <div className="card metricCard">
          <span>ユーザーID</span>
          <strong>{userId}</strong>
        </div>
      </div>
      <div className="card">
        <h3>Phase 1で使える機能</h3>
        <p>キーワード管理、Discord設定、テスト通知、通知履歴、モック巡回を確認できます。</p>
        <button className="primaryButton" onClick={runMock}>モック巡回を実行</button>
        {result && (
          <div className="resultGrid">
            <span>取得: {result.fetched_count}</span>
            <span>一致: {result.matched_count}</span>
            <span>通知作成: {result.notifications_created}</span>
            <span>重複スキップ: {result.duplicates_skipped}</span>
          </div>
        )}
        {error && <p className="errorText">{error}</p>}
      </div>
      <div className="card">
        <h3>次フェーズの監視対象</h3>
        <p>セカンドストリートオンライン、オフモール、駿河屋、まんだらけ、らしんばん</p>
      </div>
      <div className="card">
        <h3>登録キーワード巡回</h3>
        <div className="formRow">
          <input
            className="input tinyInput"
            type="number"
            min={1}
            max={50}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
          />
          <button className="primaryButton" onClick={runKeywords}>登録キーワードを巡回</button>
        </div>
        {keywordWatchResult && (
          <div className="resultGrid">
            <span>巡回: {keywordWatchResult.run_count}</span>
            <span>スキップ: {keywordWatchResult.skipped_count}</span>
            <span>通知作成: {keywordWatchResult.results.reduce((sum, item) => sum + item.result.notifications_created, 0)}</span>
            <span>重複: {keywordWatchResult.results.reduce((sum, item) => sum + item.result.duplicates_skipped, 0)}</span>
          </div>
        )}
      </div>
      <div className="card">
        <h3>実ショップ取得テスト</h3>
        <div className="formRow">
          <select className="input narrowInput" value={shopCode} onChange={(event) => setShopCode(event.target.value)}>
            <option value="offmall">オフモール</option>
            <option value="secondstreet">セカンドストリート</option>
            <option value="mandarake">まんだらけ</option>
            <option value="surugaya">駿河屋</option>
          </select>
          <input className="input" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          <input
            className="input tinyInput"
            type="number"
            min={1}
            max={50}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
          />
          <button className="primaryButton" onClick={runShop}>取得</button>
        </div>
        {shopResult && (
          <div className="resultGrid">
            <span>状態: {shopResult.status}</span>
            <span>取得: {shopResult.fetched_count}</span>
            <span>一致: {shopResult.matched_count}</span>
            <span>通知作成: {shopResult.notifications_created}</span>
            <span>重複: {shopResult.duplicates_skipped}</span>
          </div>
        )}
        {shopResult?.error_message && <p className="errorText">{shopResult.error_message}</p>}
      </div>
    </section>
  );
}
