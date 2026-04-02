# 貼文流程
+ 寫一個新內容在`archives/yyyymmdd.md`
+ 轉換成`html`
+ 附加GA code snippet
+ 更新`assets/data/blog-post-list.json`（給 blog/index 的文章清單 JS 使用）
+ 更新最新文章和文章分類 in `assets/data/shared-post-widgets.json`。

## Markdown 轉 HTML
1. 安裝 Python 套件

```bash
python3 -m pip install markdown
```

2. 轉換文章

```bash
python3 scripts/md_to_html.py archives/20260402.md
```

3. 可選參數

```bash
python3 scripts/md_to_html.py archives/20260402.md \
	--date 2026-04-02 \
	--author "Yi-Lung Chiu" \
	--email "ylchiu@gapp.nthu.edu.tw" \
	--site-url "https://ylchiu.com"
```

## 將新文章加入 widgets 與文章清單
```bash
python3 scripts/register_post.py archives/20260402.html
```

可選參數：
```bash
python3 scripts/register_post.py archives/20260402.html \
	--posts-json assets/data/blog-post-list.json \
	--widgets-json assets/data/shared-post-widgets.json \
	--blog-html blog.html \
	--latest-limit 5
```

說明：
+ `blog.html` 與 `index.html` 的文章清單由 `assets/js/blog-post-list.js` 讀取 `assets/data/blog-post-list.json` 動態渲染。
+ `latestPosts` 每次執行都會檢查並強制最多保留 5 篇。