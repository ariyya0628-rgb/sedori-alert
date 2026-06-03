import { useEffect, useState } from "react";
import { createKeyword, deleteKeyword, Keyword, listKeywords } from "../api";

export function KeywordsPage({ userId }: { userId: number }) {
  const [items, setItems] = useState<Keyword[]>([]);
  const [keyword, setKeyword] = useState("");
  const [shopCode, setShopCode] = useState("all");
  const [error, setError] = useState("");

  async function refresh() {
    setItems(await listKeywords(userId));
  }

  async function addKeyword() {
    setError("");
    try {
      await createKeyword(userId, keyword, shopCode);
      setKeyword("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録に失敗しました");
    }
  }

  async function removeKeyword(id: number) {
    setError("");
    try {
      await deleteKeyword(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "削除に失敗しました");
    }
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>キーワード管理</h2>
      </div>
      <div className="card">
        <div className="formRow">
          <input
            className="input"
            placeholder="例: レコルト"
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
          />
          <select className="input narrowInput" value={shopCode} onChange={(event) => setShopCode(event.target.value)}>
            <option value="all">全ショップ</option>
            <option value="secondstreet">セカンドストリート</option>
            <option value="offmall">オフモール</option>
            <option value="surugaya">駿河屋</option>
            <option value="mandarake">まんだらけ</option>
            <option value="lashinbang">らしんばん</option>
          </select>
          <button className="primaryButton" onClick={addKeyword}>登録</button>
        </div>
        {error && <p className="errorText">{error}</p>}
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>キーワード</th>
              <th>ショップ</th>
              <th>状態</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.keyword}</td>
                <td>{item.shop_code}</td>
                <td>{item.enabled ? "有効" : "無効"}</td>
                <td><button className="dangerButton" onClick={() => removeKeyword(item.id)}>削除</button></td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={4} className="emptyCell">登録済みキーワードはありません</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
