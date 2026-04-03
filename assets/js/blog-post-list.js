(function () {
  var DATA_PATH = "assets/data/blog-post-list.json";
  var EXCERPT_LENGTH = 200;
  var INDEX_PAGE_SIZE = 10;

  function normalizePrefix(pathname) {
    var normalized = pathname || "/";

    if (normalized.charAt(0) !== "/") {
      normalized = "/" + normalized;
    }

    if (normalized.charAt(normalized.length - 1) !== "/") {
      normalized += "/";
    }

    return normalized;
  }

  function getPrefixFromScriptPath() {
    var script = document.querySelector('script[src*="assets/js/blog-post-list.js"]');
    var src = script && script.getAttribute("src");
    var marker = "/assets/js/blog-post-list.js";
    var scriptPath;
    var markerIndex;

    if (!src) {
      return null;
    }

    try {
      scriptPath = new URL(src, window.location.href).pathname;
    } catch (e) {
      return null;
    }

    markerIndex = scriptPath.lastIndexOf(marker);
    if (markerIndex === -1) {
      return null;
    }

    return normalizePrefix(scriptPath.slice(0, markerIndex + 1));
  }

  function getBasePrefix() {
    var prefixFromScript = getPrefixFromScriptPath();
    var path = window.location.pathname || "/";
    var segments = path.split("/").filter(function (segment) {
      return segment.length > 0;
    });

    if (prefixFromScript) {
      return prefixFromScript;
    }

    if (/github\.io$/i.test(window.location.hostname) && segments.length > 0) {
      return "/" + segments[0] + "/";
    }

    return "/";
  }

  function resolveHref(href, basePrefix) {
    if (!href || /^(https?:)?\/\//.test(href) || href.indexOf("#") === 0) {
      return href;
    }
    return basePrefix + href;
  }

  function getDataUrl() {
    return getBasePrefix() + DATA_PATH;
  }

  function normalizeData(data) {
    var source = data || {};
    var posts = Array.isArray(source.posts) ? source.posts : [];

    posts = posts
      .filter(function (item) {
        return item && item.title && item.href && item.datetime;
      })
      .sort(function (a, b) {
        if (a.datetime === b.datetime) {
          return a.href < b.href ? 1 : -1;
        }
        return a.datetime < b.datetime ? 1 : -1;
      });

    return { posts: posts };
  }

  function createPostList(posts, basePrefix) {
    var list = document.createElement("ul");
    list.className = "blog-post-list";

    posts.forEach(function (post) {
      var li = document.createElement("li");
      var link = document.createElement("a");
      var time = document.createElement("time");

      link.textContent = post.title;
      link.href = resolveHref(post.href, basePrefix);

      time.dateTime = post.datetime;
      time.textContent = post.datetime;

      li.appendChild(link);
      li.appendChild(time);
      list.appendChild(li);
    });

    return list;
  }

  function sanitizeText(text) {
    return (text || "").replace(/\s+/g, " ").trim();
  }

  function trimExcerpt(text, maxLength) {
    if (!text) {
      return "";
    }

    if (text.length <= maxLength) {
      return text;
    }

    return text.slice(0, maxLength) + "...";
  }

  function extractContentTextFromHtml(html) {
    if (!html) {
      return "";
    }

    var parser = new DOMParser();
    var doc = parser.parseFromString(html, "text/html");
    var content = doc.querySelector(".entry-content .kv-page-content") || doc.querySelector("article") || doc.body;

    return sanitizeText(content ? content.textContent : "");
  }

  function fetchPostExcerpt(postUrl) {
    if (!postUrl) {
      return Promise.resolve("");
    }

    return fetch(postUrl)
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load post html");
        }
        return response.text();
      })
      .then(extractContentTextFromHtml)
      .then(function (text) {
        return trimExcerpt(text, EXCERPT_LENGTH);
      })
      .catch(function () {
        return "";
      });
  }

  function createIndexPostCard(item) {
    var card = document.createElement("a");
    var title = document.createElement("h3");
    var excerpt = document.createElement("p");
    var meta = document.createElement("div");
    var time = document.createElement("time");

    card.className = "index-post-card";
    card.href = item.href;
    card.setAttribute("aria-label", "閱讀文章：" + item.title);

    title.className = "index-post-card-title";
    title.textContent = item.title;

    excerpt.className = "index-post-card-excerpt";
    excerpt.textContent = item.excerpt || "（此文章尚無可顯示的摘要）";

    meta.className = "index-post-card-meta";
    time.dateTime = item.datetime;
    time.textContent = item.datetime;
    meta.appendChild(time);

    card.appendChild(title);
    card.appendChild(excerpt);
    card.appendChild(meta);

    return card;
  }

  function loadIndexPostBatch(posts, start, size, basePrefix) {
    var batch = posts.slice(start, start + size);

    return Promise.all(
      batch.map(function (post) {
        var url = resolveHref(post.href, basePrefix);

        return fetchPostExcerpt(url).then(function (excerpt) {
          return {
            title: post.title,
            href: url,
            datetime: post.datetime,
            excerpt: excerpt
          };
        });
      })
    );
  }

  function renderBlogPage(posts, basePrefix) {
    var mount = document.getElementById("blog-post-list-mount");
    if (!mount) {
      return false;
    }

    mount.innerHTML = "";
    mount.appendChild(createPostList(posts, basePrefix));
    return true;
  }

  function renderIndexPage(posts, basePrefix) {
    var mount = document.getElementById("index-blog-post-list-mount");
    if (!mount) {
      return false;
    }

    var title = document.createElement("h2");
    var cards = document.createElement("div");
    var controls = document.createElement("div");
    var moreButton = document.createElement("button");
    var renderedCount = 0;
    var isLoading = false;

    title.className = "wp-block-heading";
    title.textContent = "所有文章";

    cards.className = "index-post-cards";

    controls.className = "index-post-controls";
    moreButton.className = "index-post-more-button";
    moreButton.type = "button";
    moreButton.textContent = "More";
    controls.appendChild(moreButton);

    mount.innerHTML = "";
    mount.appendChild(title);
    mount.appendChild(cards);
    mount.appendChild(controls);

    function updateMoreButton() {
      if (renderedCount >= posts.length) {
        moreButton.style.display = "none";
        return;
      }

      moreButton.style.display = "inline-flex";
      moreButton.disabled = false;
      moreButton.textContent = "More";
    }

    function loadMore() {
      if (isLoading || renderedCount >= posts.length) {
        return Promise.resolve();
      }

      isLoading = true;
      moreButton.disabled = true;
      moreButton.textContent = "Loading...";

      return loadIndexPostBatch(posts, renderedCount, INDEX_PAGE_SIZE, basePrefix)
        .then(function (items) {
          items.forEach(function (item) {
            cards.appendChild(createIndexPostCard(item));
          });

          renderedCount += items.length;
          updateMoreButton();
        })
        .catch(function () {
          moreButton.disabled = false;
          moreButton.textContent = "Retry";
        })
        .finally(function () {
          isLoading = false;
        });
    }

    moreButton.addEventListener("click", loadMore);

    if (!posts.length) {
      controls.style.display = "none";
      return true;
    }

    return loadMore().then(function () {
      return true;
    });
  }

  function loadData() {
    return fetch(getDataUrl())
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load blog post data.");
        }
        return response.json();
      })
      .then(normalizeData);
  }

  function init() {
    var basePrefix = getBasePrefix();

    function hydrateWpOverviewCards() {
      var cards = document.querySelectorAll(".wpblogabc10 .kv-ee-post-wrapper");

      cards.forEach(function (card) {
        var link = card.querySelector("a[href]");
        var titleNode;

        if (!link) {
          return;
        }

        if (card.getAttribute("tabindex") !== "0") {
          card.setAttribute("tabindex", "0");
        }

        if (card.getAttribute("role") !== "link") {
          card.setAttribute("role", "link");
        }

        titleNode = card.querySelector(".kv-ee-post-title");
        if (titleNode && !card.getAttribute("aria-label")) {
          card.setAttribute("aria-label", "閱讀文章：" + sanitizeText(titleNode.textContent));
        }
      });
    }

    function onWpOverviewCardClick(event) {
      var card = event.target.closest(".wpblogabc10 .kv-ee-post-wrapper");
      var link;

      if (!card) {
        return;
      }

      if (event.target.closest("a, button, input, select, textarea, label")) {
        return;
      }

      link = card.querySelector("a[href]");
      if (!link) {
        return;
      }

      link.click();
    }

    function onWpOverviewCardKeydown(event) {
      var card = event.target.closest(".wpblogabc10 .kv-ee-post-wrapper");
      var link;

      if (!card) {
        return;
      }

      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      link = card.querySelector("a[href]");
      if (!link) {
        return;
      }

      event.preventDefault();
      link.click();
    }

    hydrateWpOverviewCards();
    document.addEventListener("click", onWpOverviewCardClick);
    document.addEventListener("keydown", onWpOverviewCardKeydown);

    if ("MutationObserver" in window) {
      new MutationObserver(function () {
        hydrateWpOverviewCards();
      }).observe(document.body, {
        childList: true,
        subtree: true
      });
    }

    loadData()
      .then(function (data) {
        renderBlogPage(data.posts, basePrefix);
        renderIndexPage(data.posts, basePrefix);
      })
      .catch(function () {
        // Keep fallback markup untouched if data cannot be loaded.
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
