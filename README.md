# せどり新着アラート

Web版・単一ユーザー向けの新着通知ツールです。

## 現在の内容

- ログイン
- ダッシュボード
- キーワード登録、一覧、削除
- Discord Webhook設定
- Discordテスト通知
- 通知履歴
- 商品一覧
- 巡回ログ
- モック巡回
- オフモール実検索取得
- セカンドストリート検索アダプター
- まんだらけ検索アダプター
- 駿河屋検索アダプター
- キーワード一致判定
- 重複通知防止
- Discord自動通知
- スケジュール設定
- 期限到来分の実行API

実ショップ巡回はオフモール、セカンドストリート、まんだらけ、駿河屋に対応しています。セカンドストリートなど一部サイトは、この環境からの直接取得では403になる場合があります。

実サイト取得の診断:

```powershell
cd sedori-alert
.\scripts\check-shops-once.ps1 -Keyword recolte -Limit 3
```

各ショップの成功/失敗、取得件数、エラー内容をJSONで確認できます。

## バックエンド起動

専用サイトとして起動:

```powershell
cd sedori-alert
.\scripts\start-site.ps1
```

画面:

```text
http://127.0.0.1:8000/
```

この起動方法では、バックエンドがビルド済みフロントエンドも配信するため、1つのURLで画面とAPIが動きます。

簡単起動:

```powershell
cd sedori-alert
.\scripts\start-backend.ps1
```

手動起動:

```powershell
cd sedori-alert\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-cache-dir --progress-bar off --index-url https://pypi.org/simple -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

初期ログイン:

```text
admin@example.com
password123
```

## フロントエンド起動

簡単起動:

```powershell
cd sedori-alert
.\scripts\start-frontend.ps1
```

このスクリプトは、`npm` が使えない場合でも同梱Node.jsとローカルpnpmを使って起動します。

npmが使える環境:

```powershell
cd sedori-alert\frontend
npm install
npm run dev
```

pnpmが使える環境:

```powershell
cd sedori-alert\frontend
pnpm install
pnpm dev
```

画面:

```text
http://localhost:5173
```

## テスト

バックエンド:

```powershell
cd sedori-alert\backend
.\.venv\Scripts\python.exe -m pytest -v
```

## Git管理

このプロジェクトはGit管理済みです。

この環境ではGitHub Desktop同梱のGitを使うため、Git操作は以下の補助スクリプトから実行できます。

```powershell
cd sedori-alert
.\scripts\git.ps1 status
.\scripts\git.ps1 log --oneline
```

## モック巡回の確認

1. フロントエンドでログインする
2. キーワード管理で `レコルト` を登録する
3. ダッシュボードで `モック巡回を実行` を押す
4. 商品一覧で `レコルト ホットプレート` と巡回ログを確認する

同じキーワードで2回目のモック巡回を実行すると、重複通知としてスキップされます。

## 実ショップ取得テスト

ダッシュボードの `実ショップ取得テスト` でショップとキーワードを指定して取得できます。

おすすめ確認:

```text
ショップ: オフモール
キーワード: レコルト
件数: 5
```

選択できるショップコード:

```text
offmall
secondstreet
mandarake
surugaya
```

取得に成功すると商品一覧と巡回ログに結果が保存されます。

## スケジュール実行

画面の `スケジュール` で、ショップ、キーワード、巡回間隔、取得件数を保存できます。

この段階では常駐プロセスではなく、以下のAPIを外部スケジューラーから定期的に呼ぶ方式です。

```text
POST /api/scheduler/run-due?user_id=1
```

ローカル確認では、画面の `期限到来分を実行` ボタンで同じ処理を試せます。

Discord Webhookが設定済みかつ通知が有効な場合、キーワードに一致した新着商品を検知するとDiscordへ通知します。

画面を開かずに1回だけ実行:

```powershell
cd sedori-alert
.\scripts\run-scheduler-once.ps1 -UserId 1
```

PC起動中に簡易監視:

```powershell
cd sedori-alert
.\scripts\start-monitor.ps1 -UserId 1 -EverySeconds 60
```

本番運用では、WindowsタスクスケジューラやVPSのcronから `run-scheduler-once.ps1` を定期実行する方式がおすすめです。

登録済みキーワードをまとめて巡回:

```powershell
cd sedori-alert
.\scripts\watch-keywords-once.ps1 -UserId 1 -Limit 20
```

元ツールに近い運用では、キーワード管理画面に登録した内容を使う `watch-keywords-once.ps1` を定期実行します。
`全ショップ` のキーワードは対応済みショップすべて、ショップ指定のキーワードは指定ショップだけを巡回します。

PC起動中に登録キーワードを簡易監視:

```powershell
cd sedori-alert
.\scripts\start-keyword-monitor.ps1 -UserId 1 -Limit 20 -EverySeconds 60
```

Windowsログイン時に自動監視を開始:

```powershell
cd sedori-alert
.\scripts\install-keyword-monitor-task.ps1 -UserId 1 -Limit 20 -EverySeconds 60
```

登録状態の確認:

```powershell
.\scripts\show-keyword-monitor-task.ps1
```

自動監視を解除:

```powershell
.\scripts\uninstall-keyword-monitor-task.ps1
```

自動監視ログ:

```text
logs\keyword-monitor.log
```

## 秘密情報

Discord Webhook URLは暗号化してDBに保存します。

本番運用では、以下の環境変数を必ず独自の値に変更してください。

```text
WEBHOOK_CRYPTO_SECRET
JWT_SECRET
```

フロントエンド:

```powershell
cd sedori-alert\frontend
npm run build
```

## 注意

- Discord Webhook URLは暗号化してDBに保存されます。本番では `WEBHOOK_CRYPTO_SECRET` を必ず独自の値に変更してください。
- `backend/.venv/`、`frontend/node_modules/`、`frontend/dist/` はGit管理対象外です。
- `tools/pnpm/` はフロントエンド簡単起動用に自動作成される補助ファイルで、Git管理対象外です。
- 実ショップ巡回では、各サイトの利用規約とアクセス頻度に注意してください。
