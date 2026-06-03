import { useEffect, useState } from "react";
import { createKeyword, deleteKeyword, Keyword, listKeywords } from "../api";

const shopOptions = [
  ["all", "全ショップ"],
  ["secondstreet", "セカンドストリート"],
  ["offmall", "オフモール"],
  ["surugaya", "駿河屋"],
  ["mandarake", "まんだらけ"],
];

function parseOptionalNumber(value: string) {
  const trimmed = value.trim();
  return trimmed ? Number(trimmed) : null;
}

function priceRangeLabel(item: Keyword) {
  if (item.min_price === null && item.max_price === null) return "-";
  const min = item.min_price === null ? "下限なし" : `${item.min_price.toLocaleString("ja-JP")}円`;
  const max = item.max_price === null ? "上限なし" : `${item.max_price.toLocaleString("ja-JP")}円`;
  return `${min} - ${max}`;
}

export function KeywordsPage({ userId }: { userId: number }) {
  const [items, setItems] = useState<Keyword[]>([]);
  const [keyword, setKeyword] = useState("");
  const [shopCode, setShopCode] = useState("all");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [includeTerms, setIncludeTerms] = useState("");
  const [excludeTerms, setExcludeTerms] = useState("");
  const [secondstreetRanks, setSecondstreetRanks] = useState("");
  const [offmallRanks, setOffmallRanks] = useState("");
  const [mandarakeRanks, setMandarakeRanks] = useState("");
  const [surugayaTags, setSurugayaTags] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    setItems(await listKeywords(userId));
  }

  async function addKeyword() {
    setError("");
    try {
      await createKeyword(userId, {
        keyword,
        shop_code: shopCode,
        min_price: parseOptionalNumber(minPrice),
        max_price: parseOptionalNumber(maxPrice),
        include_terms: includeTerms,
        exclude_terms: excludeTerms,
        secondstreet_condition_ranks: secondstreetRanks,
        offmall_condition_ranks: offmallRanks,
        mandarake_condition_ranks: mandarakeRanks,
        surugaya_condition_tags: surugayaTags,
      });
      setKeyword("");
      setMinPrice("");
      setMaxPrice("");
      setIncludeTerms("");
      setExcludeTerms("");
      setSecondstreetRanks("");
      setOffmallRanks("");
      setMandarakeRanks("");
      setSurugayaTags("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "登録に失敗しました。");
    }
  }

  async function removeKeyword(id: number) {
    setError("");
    try {
      await deleteKeyword(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "削除に失敗しました。");
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
        <div className="formGrid">
          <label>
            キーワード
            <input className="input" placeholder="例: レコルト" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          </label>
          <label>
            ショップ
            <select className="input" value={shopCode} onChange={(event) => setShopCode(event.target.value)}>
              {shopOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            価格下限
            <input className="input" inputMode="numeric" placeholder="空欄なら下限なし" value={minPrice} onChange={(event) => setMinPrice(event.target.value)} />
          </label>
          <label>
            価格上限
            <input className="input" inputMode="numeric" placeholder="空欄なら上限なし" value={maxPrice} onChange={(event) => setMaxPrice(event.target.value)} />
          </label>
          <label>
            表記ゆれ / 追加一致語
            <textarea className="input multiInput" placeholder={"例:\nrecolte\nRRF"} value={includeTerms} onChange={(event) => setIncludeTerms(event.target.value)} />
          </label>
          <label>
            除外語
            <textarea className="input multiInput" placeholder={"例:\nジャンク\n部品"} value={excludeTerms} onChange={(event) => setExcludeTerms(event.target.value)} />
          </label>
          <label>
            セカスト通知ランク
            <input className="input" placeholder="例: 新品,未使用品,中古A,中古B" value={secondstreetRanks} onChange={(event) => setSecondstreetRanks(event.target.value)} />
          </label>
          <label>
            オフモール通知ランク
            <input className="input" placeholder="例: N,S,A,B" value={offmallRanks} onChange={(event) => setOffmallRanks(event.target.value)} />
          </label>
          <label>
            まんだらけ通知ランク
            <input className="input" placeholder="例: 10,9,8,7" value={mandarakeRanks} onChange={(event) => setMandarakeRanks(event.target.value)} />
          </label>
          <label>
            駿河屋通知状態
            <input className="input" placeholder="例: 未開封品,帯付き,美品,通常中古" value={surugayaTags} onChange={(event) => setSurugayaTags(event.target.value)} />
          </label>
        </div>
        <div className="formRow">
          <button className="primaryButton" onClick={addKeyword}>
            登録
          </button>
        </div>
        {error && <p className="errorText">{error}</p>}
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>キーワード</th>
              <th>ショップ</th>
              <th>価格</th>
              <th>追加一致語</th>
              <th>除外語</th>
              <th>セカスト</th>
              <th>オフモール</th>
              <th>まんだらけ</th>
              <th>駿河屋</th>
              <th>状態</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.keyword}</td>
                <td>{item.shop_code}</td>
                <td>{priceRangeLabel(item)}</td>
                <td>{item.include_terms || "-"}</td>
                <td>{item.exclude_terms || "-"}</td>
                <td>{item.secondstreet_condition_ranks || "-"}</td>
                <td>{item.offmall_condition_ranks || "-"}</td>
                <td>{item.mandarake_condition_ranks || "-"}</td>
                <td>{item.surugaya_condition_tags || "-"}</td>
                <td>{item.enabled ? "有効" : "無効"}</td>
                <td>
                  <button className="dangerButton" onClick={() => removeKeyword(item.id)}>
                    削除
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={11} className="emptyCell">
                  登録済みキーワードはありません
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
