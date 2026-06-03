import { useState } from "react";
import { testDiscord, updateDiscordSettings } from "../api";

export function DiscordSettingsPage({ userId }: { userId: number }) {
  const [webhookUrl, setWebhookUrl] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function save() {
    setMessage("");
    setError("");
    try {
      await updateDiscordSettings(userId, webhookUrl, enabled);
      setMessage("Discord設定を保存しました。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました。");
    }
  }

  async function sendTest() {
    setMessage("");
    setError("");
    try {
      await updateDiscordSettings(userId, webhookUrl, enabled);
      await testDiscord(userId);
      setMessage("テスト通知を送信しました。");
    } catch (err) {
      setError(err instanceof Error ? err.message : "テスト通知に失敗しました。");
    }
  }

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>Discord通知設定</h2>
      </div>
      <div className="card">
        <label>
          Webhook URL
          <input className="input" value={webhookUrl} onChange={(event) => setWebhookUrl(event.target.value)} />
        </label>
        <label className="checkRow">
          <input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} />
          通知を有効にする
        </label>
        <div className="formRow">
          <button className="primaryButton" onClick={save}>保存</button>
          <button className="secondaryButton" onClick={sendTest}>保存してテスト通知</button>
        </div>
        {message && <p className="successText">{message}</p>}
        {error && <p className="errorText">{error}</p>}
      </div>
    </section>
  );
}
