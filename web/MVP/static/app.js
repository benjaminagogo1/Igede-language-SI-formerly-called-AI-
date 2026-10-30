// app.js — theme toggle, direction swap, counters, validation, submit via REST.
(function () {
  var $ = function (id) {
    return document.getElementById(id);
  };
  var root = document.documentElement;
  var URL = window.location.origin + "/api/submissions";

  // Theme (remembered if storage is available)
  try {
    var t = localStorage.getItem("igede-theme");
    if (t) root.setAttribute("data-theme", t);
  } catch (e) {}
  $("theme").addEventListener("click", function () {
    var dark =
      root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") &&
        matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem("igede-theme", next);
    } catch (e) {}
  });

  // Direction swap: first box is the source (required), second is the translation (optional)
  $("dir").addEventListener("change", function () {
    var enFirst = this.value === "en-ig";
    $("l1").textContent = enFirst ? "English Sentence" : "Igede Sentence";
    $("l2").textContent = enFirst ? "Igede Translation" : "English Translation";
    $("en").placeholder = enFirst
      ? "Type the English sentence here..."
      : "Type the Igede sentence here...";
    $("ig").placeholder = enFirst
      ? "Type the Igede translation here..."
      : "Type the English translation here...";
  });

  // Character counters
  [
    ["en", "c1"],
    ["ig", "c2"],
  ].forEach(function (p) {
    $(p[0]).addEventListener("input", function () {
      $(p[1]).textContent = this.value.length;
    });
  });

  // Submit — POST JSON to the Flask REST endpoint
  $("f").addEventListener("submit", async function (e) {
    e.preventDefault();
    var err = $("err");
    if (!$("en").value.trim()) {
      err.textContent = "Please type the sentence.";
      return;
    }
    if (!$("cat").value) {
      err.textContent = "Please select a category.";
      return;
    }
    if (!$("src").value) {
      err.textContent = "Please select a source type.";
      return;
    }
    err.textContent = "";

    var payload = {
      direction: $("dir").value,
      source_text: $("en").value.trim(),
      translation: $("ig").value.trim(),
      category: $("cat").value,
      source_type: $("src").value,
      submitted_at: new Date().toISOString(),
    };

    var res;
    try {
      res = await fetch(URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (_e) {
      toastError();
      return;
    }

    var data;
    try {
      data = await res.json();
    } catch (_e) {
      data = {};
    }

    if (!res.ok || !data.ok) {
      var msgs = data.errors && data.errors.length
        ? data.errors
        : ["Something went wrong. Please try again."];
      err.textContent = msgs.join("\n");
      return;
    }

    this.reset();
    $("c1").textContent = "0";
    $("c2").textContent = "0";
    $("dir").dispatchEvent(new Event("change"));

    var t = $("toast");
    t.classList.add("on");
    t.textContent = data.message || "Thank you! Your sentence was submitted.";
    setTimeout(function () {
      t.classList.remove("on");
    }, 3200);
  });

  function toastError() {
    var t = $("toast");
    t.textContent = "Connection failed. Please check your network and reload.";
    t.classList.add("on");
    setTimeout(function () {
      t.classList.remove("on");
    }, 3200);
  }

  // Sidebar menu
  var burger = $('burger'), menu = document.querySelector('.menu'), bd = $('backdrop');
  function setMenu(open) {
    menu.classList.toggle('open', open);
    bd.classList.toggle('on', open);
    burger.setAttribute('aria-expanded', open);
  }
  burger.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
  bd.addEventListener('click', function () { setMenu(false); });
  menu.addEventListener('click', function (e) { if (e.target.tagName === 'A') setMenu(false); });
})();
