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
      setMessage("Discord setting saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed.");
    }
  }

  async function sendTest() {
    setMessage("");
    setError("");
    try {
      await updateDiscordSettings(userId, webhookUrl, enabled);
      await testDiscord(userId);
      setMessage("Test notification sent.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test notification failed.");
    }
  }

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>Discord Settings</h2>
      </div>
      <div className="card">
        <label>
          Webhook URL
          <input className="input" value={webhookUrl} onChange={(event) => setWebhookUrl(event.target.value)} />
        </label>
        <label className="checkRow">
          <input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} />
          Enable notifications
        </label>
        <div className="formRow">
          <button className="primaryButton" onClick={save}>Save</button>
          <button className="secondaryButton" onClick={sendTest}>Save and send test</button>
        </div>
        {message && <p className="successText">{message}</p>}
        {error && <p className="errorText">{error}</p>}
      </div>
    </section>
  );
}
