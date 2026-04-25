(function () {
  function ensureLiveRegion() {
    var existing = document.getElementById("copy-status");
    if (existing) {
      return existing;
    }

    var region = document.createElement("div");
    region.id = "copy-status";
    region.setAttribute("aria-live", "polite");
    region.className = "sr-only";
    document.body.appendChild(region);
    return region;
  }

  function getCopyText(targetId) {
    var target = document.getElementById(targetId);
    if (!target) {
      return "";
    }

    return target.innerText.trim();
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }

    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
    return Promise.resolve();
  }

  function bindCopyButtons() {
    var liveRegion = ensureLiveRegion();
    var buttons = document.querySelectorAll("[data-copy-target]");

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var targetId = button.getAttribute("data-copy-target");
        var text = getCopyText(targetId);

        copyText(text).then(function () {
          var originalText = button.textContent;
          button.textContent = "Copied";
          liveRegion.textContent = "コマンドをコピーしました。";
          window.setTimeout(function () {
            button.textContent = originalText;
          }, 1400);
        });
      });
    });
  }

  function inferGitHubPagesRepo() {
    var host = window.location.hostname;
    var pathParts = window.location.pathname.split("/").filter(Boolean);

    if (!host.endsWith(".github.io") || pathParts.length === 0) {
      return null;
    }

    return {
      owner: host.replace(".github.io", ""),
      repo: pathParts[0]
    };
  }

  function hydrateRepositoryCommands() {
    var repoInfo = inferGitHubPagesRepo();

    if (!repoInfo) {
      return;
    }

    document.querySelectorAll("pre code").forEach(function (codeBlock) {
      codeBlock.textContent = codeBlock.textContent
        .replaceAll("OWNER/REPO", repoInfo.owner + "/" + repoInfo.repo)
        .replaceAll("cd REPO", "cd " + repoInfo.repo);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    hydrateRepositoryCommands();
    bindCopyButtons();
  });
})();

// Version History
// ver0.1 - 2026-04-25 - Added accessible copy-to-clipboard behavior and GitHub Pages command hydration.
