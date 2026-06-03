import { useEffect, useState } from "react";
import { listNotifications, NotificationItem } from "../api";

export function NotificationsPage({ userId }: { userId: number }) {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listNotifications(userId).then(setItems).catch((err) => setError(err.message));
  }, []);

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>通知履歴</h2>
      </div>
      {error && <p className="errorText">{error}</p>}
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>日時</th>
              <th>ショップ</th>
              <th>商品</th>
              <th>キーワード</th>
              <th>状態</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{new Date(item.notified_at).toLocaleString("ja-JP")}</td>
                <td>{item.shop_code}</td>
                <td><a href={item.product_url} target="_blank" rel="noreferrer">{item.product_title}</a></td>
                <td>{item.matched_keyword}</td>
                <td>{item.discord_status}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={5} className="emptyCell">通知履歴はまだありません</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
