import { useState } from "react";
import { Bell, CalendarClock, KeyRound, LayoutDashboard, LogOut, MessageCircle, PackageSearch } from "lucide-react";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { KeywordsPage } from "./pages/KeywordsPage";
import { DiscordSettingsPage } from "./pages/DiscordSettingsPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { ProductsPage } from "./pages/ProductsPage";
import { SchedulerPage } from "./pages/SchedulerPage";
import { clearAccessToken } from "./api";

type Page = "dashboard" | "keywords" | "products" | "scheduler" | "discord" | "notifications";

export default function App() {
  const storedUser = localStorage.getItem("sedori_user_id");
  const [userId, setUserId] = useState<number | null>(storedUser ? Number(storedUser) : null);
  const [page, setPage] = useState<Page>("dashboard");

  function logout() {
    localStorage.removeItem("sedori_user_id");
    clearAccessToken();
    setUserId(null);
  }

  if (!userId) {
    return <LoginPage onLogin={(id) => setUserId(id)} />;
  }

  return (
    <div className="appShell">
      <aside className="sidebar">
        <h1>せどり新着アラート</h1>
        <button className={page === "dashboard" ? "activeNav" : ""} onClick={() => setPage("dashboard")}>
          <LayoutDashboard size={18} />ダッシュボード
        </button>
        <button className={page === "keywords" ? "activeNav" : ""} onClick={() => setPage("keywords")}>
          <KeyRound size={18} />キーワード
        </button>
        <button className={page === "products" ? "activeNav" : ""} onClick={() => setPage("products")}>
          <PackageSearch size={18} />商品一覧
        </button>
        <button className={page === "scheduler" ? "activeNav" : ""} onClick={() => setPage("scheduler")}>
          <CalendarClock size={18} />スケジュール
        </button>
        <button className={page === "discord" ? "activeNav" : ""} onClick={() => setPage("discord")}>
          <MessageCircle size={18} />Discord設定
        </button>
        <button className={page === "notifications" ? "activeNav" : ""} onClick={() => setPage("notifications")}>
          <Bell size={18} />通知履歴
        </button>
        <button className="logoutButton" onClick={logout}>
          <LogOut size={18} />ログアウト
        </button>
      </aside>
      <main className="mainPanel">
        {page === "dashboard" && <DashboardPage userId={userId} />}
        {page === "keywords" && <KeywordsPage userId={userId} />}
        {page === "products" && <ProductsPage />}
        {page === "scheduler" && <SchedulerPage userId={userId} />}
        {page === "discord" && <DiscordSettingsPage userId={userId} />}
        {page === "notifications" && <NotificationsPage userId={userId} />}
      </main>
    </div>
  );
}
