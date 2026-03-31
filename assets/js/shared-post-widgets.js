(function () {
  var ARCHIVES_DIR = "/archives/";
  var DATA_PATH = "assets/data/shared-post-widgets.json";

  function isArchivePage() {
    return window.location.pathname.indexOf(ARCHIVES_DIR) !== -1;
  }

  function isIndexLikePath() {
    var path = window.location.pathname || "/";

    if (path === "/" || path === "/index.html" || path.indexOf("index.html") !== -1) {
      return true;
    }

    // Support GitHub Pages project root paths like /repo/.
    return path.charAt(path.length - 1) === "/";
  }

  function resolveHref(href, basePrefix) {
    if (!href || /^(https?:)?\/\//.test(href) || href.indexOf("#") === 0) {
      return href;
    }
    return basePrefix + href;
  }

  function getBasePrefix() {
    var path = window.location.pathname || "/";
    var segments = path.split("/").filter(function (segment) {
      return segment.length > 0;
    });

    // For GitHub Pages project sites, pages live under /<repo>/...
    // Use the first path segment as a stable site prefix.
    if (/github\.io$/i.test(window.location.hostname) && segments.length > 0) {
      return "/" + segments[0] + "/";
    }

    return "/";
  }

  function getDataUrl() {
    return getBasePrefix() + DATA_PATH;
  }

  function normalizeGitHubPagesRootToIndex() {
    if (!/github\.io$/i.test(window.location.hostname)) {
      return false;
    }

    var path = window.location.pathname || "/";
    var segments = path.split("/").filter(function (segment) {
      return segment.length > 0;
    });

    // Project site root is /<repo>/ and should resolve to /<repo>/index.html.
    if (path.charAt(path.length - 1) === "/" && segments.length === 1) {
      var nextUrl = path + "index.html" + (window.location.search || "") + (window.location.hash || "");
      window.location.replace(nextUrl);
      return true;
    }

    return false;
  }

  function createSection(titleText, listClassName, items, basePrefix) {
    var section = document.createElement("section");

    var title = document.createElement("h2");
    title.className = "wp-block-heading";
    title.textContent = titleText;
    section.appendChild(title);

    var list = document.createElement("ul");
    list.className = listClassName;

    items.forEach(function (item) {
      var li = document.createElement("li");
      var link = document.createElement("a");
      link.textContent = item.title;
      link.href = resolveHref(item.href, basePrefix);

      if (listClassName.indexOf("wp-block-latest-posts") !== -1) {
        link.className = "wp-block-latest-posts__post-title";
      }

      li.appendChild(link);
      list.appendChild(li);
    });

    section.appendChild(list);
    return section;
  }

  function buildWidget(data) {
    var basePrefix = getBasePrefix();
    var wrapper = document.createElement("div");
    wrapper.className = "ylc-shared-post-widgets";

    var latestSection = createSection(
      "最新文章",
      "wp-block-latest-posts__list wp-block-latest-posts",
      data.latestPosts || [],
      basePrefix
    );

    var categoriesSection = createSection(
      "文章分類",
      "wp-block-categories-list wp-block-categories",
      data.categories || [],
      basePrefix
    );

    wrapper.appendChild(latestSection);
    wrapper.appendChild(categoriesSection);
    return wrapper;
  }

  function normalizeData(data) {
    var source = data || {};
    return {
      latestPosts: Array.isArray(source.latestPosts) ? source.latestPosts : [],
      categories: Array.isArray(source.categories) ? source.categories : []
    };
  }

  function hasWidgetItems(data) {
    return data.latestPosts.length > 0 || data.categories.length > 0;
  }

  function normalizedText(element) {
    return (element && element.textContent || "").replace(/\s+/g, "").trim();
  }

  function removeElementRange(parent, startNode, endNode) {
    if (!parent || !startNode || !endNode) {
      return;
    }

    var children = Array.prototype.slice.call(parent.children);
    var startIndex = children.indexOf(startNode);
    var endIndex = children.indexOf(endNode);

    if (startIndex === -1 || endIndex === -1 || endIndex < startIndex) {
      return;
    }

    for (var i = endIndex; i >= startIndex; i -= 1) {
      parent.removeChild(children[i]);
    }
  }

  function replaceArchiveBlock(widget) {
    var markers = Array.prototype.slice.call(document.querySelectorAll("p, h2, h3, h4"));
    var marker = markers.find(function (el) {
      return normalizedText(el).indexOf("所有文章分類") !== -1;
    });

    if (!marker || !marker.parentElement) {
      return false;
    }

    var parent = marker.parentElement;
    var siblings = Array.prototype.slice.call(parent.children);
    var markerIndex = siblings.indexOf(marker);
    var categoryList = null;
    var latestList = null;

    for (var i = markerIndex + 1; i < siblings.length; i += 1) {
      var el = siblings[i];
      if (!categoryList && el.matches("ul.wp-block-categories")) {
        categoryList = el;
      }
      if (!latestList && el.matches("ul.wp-block-latest-posts")) {
        latestList = el;
      }
      if (categoryList && latestList) {
        break;
      }
    }

    var endNode = latestList || categoryList;
    if (!endNode) {
      return false;
    }

    parent.insertBefore(widget, marker);
    removeElementRange(parent, marker, endNode);
    return true;
  }

  function replaceBlogBlock(widget) {
    var latestList = document.querySelector("ul.blog-post-list");
    var categoryList = document.querySelector("ul.blog-category-list");
    if (!latestList || !categoryList || !latestList.parentElement) {
      return false;
    }

    var parent = latestList.parentElement;
    var headingCandidates = Array.prototype.slice.call(parent.querySelectorAll("h1, h2, h3, h4"));
    var categoryHeading = headingCandidates.find(function (el) {
      return normalizedText(el).indexOf("文章分類") !== -1;
    });

    parent.insertBefore(widget, latestList);
    if (categoryHeading) {
      removeElementRange(parent, latestList, categoryList);
    } else {
      parent.removeChild(latestList);
      parent.removeChild(categoryList);
    }

    return true;
  }

  function commonAncestor(a, b) {
    var current = a;
    while (current) {
      if (current.contains(b)) {
        return current;
      }
      current = current.parentElement;
    }
    return null;
  }

  function replaceByPlaceholder(widget) {
    var mount = document.getElementById("shared-post-widgets-mount");
    if (!mount || !mount.parentElement) {
      return false;
    }

    mount.parentElement.insertBefore(widget, mount);
    mount.parentElement.removeChild(mount);
    return true;
  }

  function replaceIndexBlock(widget) {
    if (replaceByPlaceholder(widget)) {
      return true;
    }

    var headings = Array.prototype.slice.call(document.querySelectorAll("h1, h2, h3, h4"));
    var latestHeading = headings.find(function (el) {
      return normalizedText(el) === "最新文章";
    });
    var categoryHeading = headings.find(function (el) {
      return normalizedText(el) === "文章分類";
    });

    if (!latestHeading || !categoryHeading) {
      return false;
    }

    var ancestor = commonAncestor(latestHeading, categoryHeading);
    if (!ancestor) {
      return false;
    }

    var columnsAncestor = ancestor.closest(".wp-block-columns");
    var target = columnsAncestor || ancestor;

    target.parentElement.insertBefore(widget, target);
    target.parentElement.removeChild(target);
    return true;
  }

  function injectWidget(data) {
    var normalizedData = normalizeData(data);
    if (!hasWidgetItems(normalizedData)) {
      return false;
    }

    var widget = buildWidget(normalizedData);

    // Prefer placeholder replacement when available so rendering is consistent
    // regardless of route style (/repo/ vs /repo/index.html).
    if (replaceByPlaceholder(widget)) {
      return true;
    }

    if (isArchivePage()) {
      return replaceArchiveBlock(widget);
    }

    if (window.location.pathname.indexOf("blog.html") !== -1) {
      return replaceBlogBlock(widget);
    }

    if (isIndexLikePath()) {
      return replaceIndexBlock(widget);
    }

    return false;
  }

  function loadWidgetData() {
    return fetch(getDataUrl())
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load shared post widgets data.");
        }
        return response.json();
      })
      .then(normalizeData);
  }

  function init() {
    if (normalizeGitHubPagesRootToIndex()) {
      return;
    }

    loadWidgetData()
      .then(function (data) {
        injectWidget(data);
      })
      .catch(function () {
        // Keep existing markup untouched when shared data is unavailable.
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
