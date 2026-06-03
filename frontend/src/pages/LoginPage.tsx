import { useState } from "react";
import { login, setAccessToken } from "../api";

export function LoginPage({ onLogin }: { onLogin: (userId: number) => void }) {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  async function submit() {
    setError("");
    try {
      const result = await login(email, password);
      localStorage.setItem("sedori_user_id", String(result.user_id));
      setAccessToken(result.access_token);
      onLogin(result.user_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "ログインに失敗しました");
    }
  }

  return (
    <div className="loginWrap">
      <div className="loginCard">
        <h1>せどり新着アラート</h1>
        <p>管理画面へログイン</p>
        <label>
          メールアドレス
          <input className="input" value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        <label>
          パスワード
          <input
            className="input"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        <button className="primaryButton" onClick={submit}>ログイン</button>
        {error && <p className="errorText">{error}</p>}
      </div>
    </div>
  );
}
