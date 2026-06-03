import { useEffect, useState } from "react";
import { listCrawlLogs, listProducts, CrawlLog, Product } from "../api";

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [logs, setLogs] = useState<CrawlLog[]>([]);
  const [error, setError] = useState("");

  async function refresh() {
    const [productItems, logItems] = await Promise.all([listProducts(), listCrawlLogs()]);
    setProducts(productItems);
    setLogs(logItems);
  }

  useEffect(() => {
    refresh().catch((err) => setError(err.message));
  }, []);

  return (
    <section className="panel">
      <div className="pageHeader">
        <h2>商品一覧</h2>
        <button className="secondaryButton" onClick={() => refresh().catch((err) => setError(err.message))}>更新</button>
      </div>
      {error && <p className="errorText">{error}</p>}
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>検知日時</th>
              <th>ショップ</th>
              <th>商品名</th>
              <th>価格</th>
              <th>カテゴリ</th>
              <th>在庫</th>
            </tr>
          </thead>
          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{new Date(product.detected_at).toLocaleString("ja-JP")}</td>
                <td>{product.shop_code}</td>
                <td><a href={product.product_url} target="_blank" rel="noreferrer">{product.title}</a></td>
                <td>{product.price.toLocaleString("ja-JP")}円</td>
                <td>{product.category || "-"}</td>
                <td>{product.stock_status}</td>
              </tr>
            ))}
            {products.length === 0 && (
              <tr>
                <td colSpan={6} className="emptyCell">商品はまだありません</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="card">
        <h3>巡回ログ</h3>
        <table className="table">
          <thead>
            <tr>
              <th>終了日時</th>
              <th>対象</th>
              <th>取得</th>
              <th>一致</th>
              <th>通知</th>
              <th>重複</th>
            </tr>
          </thead>
          <tbody>
            {logs.slice(0, 10).map((log) => (
              <tr key={log.id}>
                <td>{new Date(log.finished_at).toLocaleString("ja-JP")}</td>
                <td>{log.shop_code}</td>
                <td>{log.fetched_count}</td>
                <td>{log.matched_count}</td>
                <td>{log.notified_count}</td>
                <td>{log.duplicates_skipped}</td>
              </tr>
            ))}
            {logs.length === 0 && (
              <tr>
                <td colSpan={6} className="emptyCell">巡回ログはまだありません</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
