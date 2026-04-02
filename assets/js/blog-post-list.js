(function () {
  var DATA_PATH = "assets/data/blog-post-list.json";

  function getBasePrefix() {
    var path = window.location.pathname || "/";
    var segments = path.split("/").filter(function (segment) {
      return segment.length > 0;
    });

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

    title.className = "wp-block-heading";
    title.textContent = "所有文章";

    mount.innerHTML = "";
    mount.appendChild(title);
    mount.appendChild(createPostList(posts, basePrefix));
    return true;
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
