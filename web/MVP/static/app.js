// app.js — theme, mobile menu, contribution tabs (text/audio/image), recorder, REST submit.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var root = document.documentElement;
  var API = window.location.origin + "/api/submissions";

  // ---- Theme (remembered if storage is available)
  var saved = null;
  try { saved = localStorage.getItem("igede-theme"); } catch (e) {}
  root.setAttribute("data-theme", saved || "dark");
  if ($("theme")) {
    $("theme").addEventListener("click", function () {
      var dark =
        root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("igede-theme", next); } catch (e) {}
    });
  }


  // ---- Fixed header: gets a solid background after scrolling
  var hdr = document.querySelector(".top");
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle("scrolled", window.scrollY > 10); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }




  // ---- Mobile sidebar menu
  var burger = $("burger"), menu = document.querySelector(".menu"), bd = $("backdrop");
  if (burger && menu && bd) {
    var setMenu = function (open) {
      menu.classList.toggle("open", open);
      bd.classList.toggle("on", open);
      burger.setAttribute("aria-expanded", open);
    };
    burger.addEventListener("click", function () { setMenu(!menu.classList.contains("open")); });
    bd.addEventListener("click", function () { setMenu(false); });
    menu.addEventListener("click", function (e) { if (e.target.tagName === "A") setMenu(false); });
  }




  // ---- Sample audio players (Explore Approved Contributions)
  var PLAY = '<svg viewBox="0 0 24 24" width="14" height="14" fill="#fff"><path d="M7 4.5v15l13-7.5z"/></svg>';
  var PAUSE = '<svg viewBox="0 0 24 24" width="14" height="14" fill="#fff"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></svg>';
  document.querySelectorAll(".player").forEach(function (p) {
    var src = p.dataset.src;
    var wave = p.querySelector(".wave");
    var btn = p.querySelector(".pbtn");
    var time = p.querySelector(".time");
    var N = 42, bars = [];
    for (var i = 0; i < N; i++) {
      var bar = document.createElement("i");
      bar.style.height = (6 + Math.abs(Math.sin(i * 1.7)) * 18 + (i % 5)) + "px";
      wave.appendChild(bar);
      bars.push(bar);
    }
    if (!src) { btn.disabled = true; return; }

    var audio = new Audio();
    audio.preload = "metadata";
    audio.src = src;
    function fmt(s) {
      if (!isFinite(s)) return "0:00";
      var m = Math.floor(s / 60), r = Math.floor(s % 60);
      return m + ":" + (r < 10 ? "0" : "") + r;
    }
    function paint(k) { bars.forEach(function (b, idx) { b.classList.toggle("on", idx < k); }); }
    audio.addEventListener("loadedmetadata", function () { time.textContent = fmt(audio.duration); });
    audio.addEventListener("timeupdate", function () {
      paint(isFinite(audio.duration) && audio.duration ? Math.floor(audio.currentTime / audio.duration * N) : 0);
      time.textContent = fmt(audio.currentTime);
    });
    audio.addEventListener("ended", function () { btn.innerHTML = PLAY; paint(0); time.textContent = fmt(audio.duration); });
    btn.addEventListener("click", function () {
      if (audio.paused) { audio.play(); btn.innerHTML = PAUSE; }
      else { audio.pause(); btn.innerHTML = PLAY; }
    });
  });



















  // ---- Contribution form (home page only)
  var form = $("f");
  if (!form) return;

  var mt = "text";
  var recorder = null, chunks = [], recorded = null, recordedExt = "webm";
  var tabs = document.querySelectorAll(".card .tab[data-mt]");

  function showErr(msg) { $("err").textContent = msg; }

  function updateLabels() {
    var enFirst = $("dir").value === "en-ig";
    var noun = mt === "image" ? "Label" : "Sentence";
    $("l1").textContent = (enFirst ? "English " : "Igede ") + noun;
    $("l2").textContent = (enFirst ? "Igede " : "English ") + (mt === "image" ? "Label" : "Translation");
    $("en").placeholder = "Type the " + (enFirst ? "English " : "Igede ") + noun.toLowerCase() + " here...";
    $("ig").placeholder = "Type the " + (enFirst ? "Igede " : "English ") + (mt === "image" ? "label" : "translation") + " here...";
  }

  function clearFile() {
    $("file").value = "";
    recorded = null;
    $("preview").hidden = true;
    $("preview").removeAttribute("src");
    $("imgPreview").hidden = true;
    $("imgPreview").removeAttribute("src");
    $("rec").innerHTML = "&#9679; Record now";
    if (recorder && recorder.state === "recording") recorder.stop();
  }

  function setTab(t) {
    mt = t;
    tabs.forEach(function (b) {
      var on = b.dataset.mt === t;
      b.classList.toggle("on", on);
      b.setAttribute("aria-selected", on);
    });
    $("fbox").hidden = t === "text";
    $("audioTools").hidden = t !== "audio";
    $("file").accept = t === "audio" ? "audio/*" : "image/*";
    $("fileLabel").textContent = t === "audio" ? "Audio recording (upload or record)" : "Image file";
    clearFile();
    showErr("");
    updateLabels();
  }

  tabs.forEach(function (b) { b.addEventListener("click", function () { setTab(b.dataset.mt); }); });
  // Feature cards on the left act as shortcuts to a tab
  document.querySelectorAll("[data-tab]").forEach(function (el) {
    el.addEventListener("click", function () { setTab(el.dataset.tab); });
  });

  $("dir").addEventListener("change", updateLabels);

  [["en", "c1"], ["ig", "c2"]].forEach(function (p) {
    $(p[0]).addEventListener("input", function () { $(p[1]).textContent = this.value.length; });
  });

  // Preview a chosen file
  $("file").addEventListener("change", function () {
    recorded = null;
    var f = this.files[0];
    if (!f) return;
    var url = URL.createObjectURL(f);
    if (mt === "audio") { $("preview").src = url; $("preview").hidden = false; }
    if (mt === "image") { $("imgPreview").src = url; $("imgPreview").hidden = false; }
  });

  // Browser recorder
  $("rec").addEventListener("click", async function () {
    if (recorder && recorder.state === "recording") { recorder.stop(); return; }
    var stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (e) {
      showErr("Microphone access was denied or is unavailable.");
      return;
    }
    showErr("");
    chunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = function (e) { if (e.data.size) chunks.push(e.data); };
    recorder.onstop = function () {
      stream.getTracks().forEach(function (t) { t.stop(); });
      var type = recorder.mimeType || "audio/webm";
      recordedExt = type.indexOf("mp4") > -1 ? "mp4" : type.indexOf("ogg") > -1 ? "ogg" : "webm";
      recorded = new Blob(chunks, { type: type });
      $("file").value = "";
      $("preview").src = URL.createObjectURL(recorded);
      $("preview").hidden = false;
      $("rec").innerHTML = "&#9679; Record again";
    };
    recorder.start();
    $("rec").innerHTML = "&#9632; Stop recording";
  });

  // Submit
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!$("en").value.trim()) {
      showErr(mt === "image" ? "Please type a label for the image." : "Please type the sentence.");
      return;
    }
    if (!$("cat").value) { showErr("Please select a category."); return; }
    if (!$("src").value) { showErr("Please select a source type."); return; }

    var fd = new FormData();
    fd.append("media_type", mt);
    fd.append("direction", $("dir").value);
    fd.append("source_text", $("en").value.trim());
    fd.append("translation", $("ig").value.trim());
    fd.append("category", $("cat").value);
    fd.append("source_type", $("src").value);

    if (mt !== "text") {
      if (recorded) {
        fd.append("file", recorded, "recording." + recordedExt);
      } else if ($("file").files[0]) {
        fd.append("file", $("file").files[0]);
      } else {
        showErr(mt === "audio" ? "Please record or upload an audio file." : "Please choose an image.");
        return;
      }
    }
    showErr("");

    var res;
    try {
      res = await fetch(API, { method: "POST", body: fd });
    } catch (_e) {
      toast("Connection failed. Please check your network and reload.");
      return;
    }

    var data;
    try { data = await res.json(); } catch (_e) { data = {}; }

    if (!res.ok || !data.ok) {
      var msgs = data.errors && data.errors.length ? data.errors : ["Something went wrong. Please try again."];
      showErr(msgs.join("\n"));
      return;
    }

    form.reset();
    $("c1").textContent = "0";
    $("c2").textContent = "0";
    clearFile();
    updateLabels();
    toast(data.message || "Thank you! Your contribution was submitted.");
  });

  function toast(msg) {
    var t = $("toast");
    t.textContent = msg;
    t.classList.add("on");
    setTimeout(function () { t.classList.remove("on"); }, 3200);
  }

  setTab("text");
})();