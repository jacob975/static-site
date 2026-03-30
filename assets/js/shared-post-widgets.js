(function () {
  var ARCHIVE_PREFIX = "archives/";
  var ARCHIVES_DIR = "/archives/";

  function isArchivePage() {
    return window.location.pathname.indexOf(ARCHIVES_DIR) !== -1;
  }

  function resolveHref(href, basePrefix) {
    if (!href || /^(https?:)?\/\//.test(href) || href.indexOf("#") === 0) {
      return href;
    }
    return basePrefix + href;
  }

  function getBasePrefix() {
    return isArchivePage() ? "../" : "";
  }

  function getDataUrl() {
    return getBasePrefix() + "assets/data/shared-post-widgets.json";
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

  function replaceIndexBlock(widget) {
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
    var widget = buildWidget(data);

    if (isArchivePage()) {
      return replaceArchiveBlock(widget);
    }

    if (window.location.pathname.indexOf("blog.html") !== -1) {
      return replaceBlogBlock(widget);
    }

    if (
      window.location.pathname === "/" ||
      window.location.pathname === "/index.html" ||
      window.location.pathname.indexOf("index.html") !== -1
    ) {
      return replaceIndexBlock(widget);
    }

    return false;
  }

  function init() {
    fetch(getDataUrl())
      .then(function (response) {
        if (!response.ok) {
          throw new Error("Failed to load shared post widgets data.");
        }
        return response.json();
      })
      .then(function (data) {
        injectWidget(data);
      })
      .catch(function () {
        // Keep legacy blocks untouched when data cannot be loaded.
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
