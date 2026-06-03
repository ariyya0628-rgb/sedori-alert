import { useEffect, useState } from "react";
import {
  getSchedulerSetting,
  runDueScheduler,
  saveSchedulerSetting,
  SchedulerRunDueResult,
  SchedulerSetting,
} from "../api";

const initialSetting: SchedulerSetting = {
  enabled: false,
  shop_code: "offmall",
  keyword: "レコルト",
  interval_minutes: 10,
  limit: 5,
  last_run_at: null,
  next_run_at: null,
};

export function SchedulerPage({ userId }: { userId: number }) {
  const [setting, setSetting] = useState<SchedulerSetting>(initialSetting);
  const [runResult, setRunResult] = useState<SchedulerRunDueResult | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getSchedulerSetting(userId).then(setSetting).catch((err) => setError(err.message));
  }, []);

  async function save() {
    setMessage("");
    setError("");
    try {
      setSetting(await saveSchedulerSetting(userId, setting));
      setMessage("スケジュール設定を保存しました");
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました");
    }
  }

  async function runDue() {
    setRunResult(null);
    setError("");
    try {
      const result = await runDueScheduler(userId);
      setRunResult(result);
      setSetting(await getSchedulerSetting(userId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "実行に失敗しました");
    }
  }

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>スケジュール</h2>
      </div>
      <div className="card">
        <label className="checkRow">
          <input
            type="checkbox"
            checked={setting.enabled}
            onChange={(event) => setSetting({ ...setting, enabled: event.target.checked })}
          />
          有効にする
        </label>
        <div className="formRow">
          <select
            className="input narrowInput"
            value={setting.shop_code}
            onChange={(event) => setSetting({ ...setting, shop_code: event.target.value })}
          >
            <option value="offmall">オフモール</option>
            <option value="secondstreet">セカンドストリート</option>
          </select>
          <input
            className="input"
            value={setting.keyword}
            onChange={(event) => setSetting({ ...setting, keyword: event.target.value })}
          />
          <input
            className="input tinyInput"
            type="number"
            min={1}
            value={setting.interval_minutes}
            onChange={(event) => setSetting({ ...setting, interval_minutes: Number(event.target.value) })}
          />
          <input
            className="input tinyInput"
            type="number"
            min={1}
            max={50}
            value={setting.limit}
            onChange={(event) => setSetting({ ...setting, limit: Number(event.target.value) })}
          />
        </div>
        <div className="formRow">
          <button className="primaryButton" onClick={save}>保存</button>
          <button className="secondaryButton" onClick={runDue}>期限到来分を実行</button>
        </div>
        <div className="resultGrid">
          <span>最終実行: {setting.last_run_at ? new Date(setting.last_run_at).toLocaleString("ja-JP") : "-"}</span>
          <span>次回実行: {setting.next_run_at ? new Date(setting.next_run_at).toLocaleString("ja-JP") : "-"}</span>
        </div>
        {runResult && (
          <div className="resultGrid">
            <span>実行: {runResult.ran ? "あり" : "なし"}</span>
            {runResult.reason && <span>理由: {runResult.reason}</span>}
            {runResult.result && <span>取得: {runResult.result.fetched_count}</span>}
            {runResult.result && <span>通知: {runResult.result.notifications_created}</span>}
          </div>
        )}
        {message && <p className="successText">{message}</p>}
        {error && <p className="errorText">{error}</p>}
      </div>
    </section>
  );
}
