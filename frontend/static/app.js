function normalizeApi(api) {
  const x = (api || "").toString().trim();
  if (!x) return "http://127.0.0.1:8000";
  return x.replace(/\/$/, "");
}

function shortText(t, limit = 180) {
  const x = (t || "").toString().replaceAll("\n", " ").trim();
  if (x.length <= limit) return x;
  return x.slice(0, limit) + "…";
}

function getInitialApiBase() {
  const params = new URLSearchParams(window.location.search);
  return (
    params.get("api") ||
    window.GOSTCHECKER_API_BASE ||
    localStorage.getItem("gostchecker_api_base") ||
    "http://127.0.0.1:8000"
  );
}

const PROFILE_IDS = ["LIGHT", "MEDIUM", "HARD", "CUSTOM"];
const PROFILE_BUTTONS = {
  LIGHT: "profileLightBtn",
  MEDIUM: "profileMediumBtn",
  HARD: "profileHardBtn",
  CUSTOM: "profileCustomBtn",
};

let API_BASE = normalizeApi(getInitialApiBase());
let METHODS_CACHE = null;
let MODULES_CACHE = null;
let CLASSIFY_CACHE = null;
let LAST_FIXED_FILE = null;
let ACTIVE_PROFILE = "HARD";

function selectedCustomChecks() {
  return Array.from(document.querySelectorAll('input[name="custom-check"]:checked')).map((x) => x.value);
}

function setProfile(profile) {
  ACTIVE_PROFILE = PROFILE_IDS.includes(profile) ? profile : "HARD";
  for (const p of PROFILE_IDS) {
    const btn = document.getElementById(PROFILE_BUTTONS[p]);
    if (!btn) continue;
    if (p === ACTIVE_PROFILE) {
      btn.style.outline = "2px solid #1d4ed8";
    } else {
      btn.style.outline = "none";
    }
  }
  document.getElementById("customChecksBlock").style.display = ACTIVE_PROFILE === "CUSTOM" ? "block" : "none";
  document.getElementById("profileHint").textContent =
    ACTIVE_PROFILE === "CUSTOM"
      ? "Выбран пользовательский профиль: ограничения по типу документа не применяются."
      : `Выбран профиль ${ACTIVE_PROFILE}.`;
}

function fillCustomChecks(catalog) {
  const host = document.getElementById("customChecksList");
  host.innerHTML = "";
  for (const item of catalog) {
    const row = document.createElement("label");
    row.className = "violation";
    row.style.display = "flex";
    row.style.gap = "10px";
    row.style.alignItems = "center";
    row.innerHTML = `
      <input type="checkbox" name="custom-check" value="${item.checker_id}" />
      <div>
        <div class="code">${item.title_ru}</div>
        <div class="kv">${item.checker_id}</div>
      </div>
    `;
    host.appendChild(row);
  }
}

async function loadModules() {
  const res = await fetch(`${API_BASE}/api/modules`);
  if (!res.ok) throw new Error("Не удалось получить список модулей");
  return await res.json();
}

async function loadMethods() {
  const res = await fetch(`${API_BASE}/api/methods`);
  if (res.ok) return await res.json();
  const modules = await loadModules();
  const scopes = modules?.scopes || [];
  const byId = new Map(scopes.map((s) => [s.scope_id, s]));
  const methods = [];
  for (const s of scopes) {
    if (!s?.scope_id?.startsWith("validate_")) continue;
    const base = s.scope_id.slice("validate_".length);
    const correctScope = byId.get(`correct_${base}`) || null;
    methods.push({
      method_id: base,
      title: s.title,
      description: s.description,
      actions: {
        validate: s.scope_id,
        correct: correctScope ? correctScope.scope_id : null,
        analyze: s.scope_id,
      },
    });
  }
  return { methods };
}

function fillMethodSelect(methods) {
  const methodSelect = document.getElementById("methodSelect");
  methodSelect.innerHTML = "";
  for (const m of methods) {
    const opt = document.createElement("option");
    opt.value = m.method_id;
    opt.textContent = m.title;
    methodSelect.appendChild(opt);
  }
  if (methods.length) methodSelect.value = methods[0].method_id;
}

function getSelectedMethod(methods, methodId) {
  return methods.find((m) => m.method_id === methodId) || null;
}

function setActionAvailability(method) {
  const actionSelect = document.getElementById("actionSelect");
  const actions = method?.actions || {};
  const order = ["validate", "correct", "analyze"];
  let firstAvailable = null;
  for (const action of order) {
    const opt = actionSelect.querySelector(`option[value="${action}"]`);
    const available = actions[action] !== null && actions[action] !== undefined;
    if (opt) opt.disabled = !available;
    if (available && firstAvailable === null) firstAvailable = action;
  }
  const current = actionSelect.value;
  const currentOpt = actionSelect.querySelector(`option[value="${current}"]`);
  if (currentOpt && currentOpt.disabled && firstAvailable) actionSelect.value = firstAvailable;
}

function applySelection() {
  const method = getSelectedMethod(METHODS_CACHE?.methods || [], document.getElementById("methodSelect").value);
  if (!method) return;
  setActionAvailability(method);
  const action = document.getElementById("actionSelect").value;
  const scope = method.actions?.[action] || "-";
  document.getElementById("scopeHint").textContent = `${method.description || ""} | scope_id: ${scope}`;
}

function fillManualClassSelect(choices) {
  const sel = document.getElementById("manualClassSelect");
  sel.innerHTML = "";
  for (const c of choices || []) {
    const opt = document.createElement("option");
    opt.value = c.class_id;
    opt.textContent = c.title_ru;
    sel.appendChild(opt);
  }
}

async function classifyDocument() {
  const file = document.getElementById("fileInput").files?.[0];
  if (!file) {
    alert("Сначала выберите DOCX файл");
    return;
  }
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/api/classify`, { method: "POST", body: fd });
  if (!res.ok) throw new Error("Не удалось определить тип документа");
  CLASSIFY_CACHE = await res.json();

  const hint = document.getElementById("classifyHint");
  const manualBlock = document.getElementById("manualClassBlock");
  if (CLASSIFY_CACHE.detected) {
    hint.textContent = `Документ определен как: ${CLASSIFY_CACHE.title_ru}. Рекомендуемый режим: ${CLASSIFY_CACHE.recommended_mode}.`;
    if (CLASSIFY_CACHE.warning) {
      hint.textContent += ` ${CLASSIFY_CACHE.warning}`;
    }
    manualBlock.style.display = "none";
    if (CLASSIFY_CACHE.recommended_mode) setProfile(CLASSIFY_CACHE.recommended_mode);
  } else {
    hint.textContent = "Тип документа не удалось определить автоматически. Выберите тип вручную.";
    manualBlock.style.display = "block";
    fillManualClassSelect(CLASSIFY_CACHE.choices || []);
  }
}

function setupDownload(fixedFile) {
  const block = document.getElementById("downloadBlock");
  const btn = document.getElementById("downloadBtn");
  const hint = document.getElementById("downloadHint");
  LAST_FIXED_FILE = fixedFile || null;
  if (!fixedFile?.base64) {
    block.style.display = "none";
    return;
  }
  block.style.display = "block";
  hint.textContent = `${fixedFile.filename || "document_fixed.docx"} (${Math.round((fixedFile.size_bytes || 0) / 1024)} KB)`;
  btn.onclick = () => {
    if (!LAST_FIXED_FILE?.base64) return;
    const binary = atob(LAST_FIXED_FILE.base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    const blob = new Blob([bytes], {
      type:
        LAST_FIXED_FILE.content_type ||
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = LAST_FIXED_FILE.filename || "document_fixed.docx";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };
}

function renderViolations(violations) {
  const host = document.getElementById("violationsBlock");
  host.innerHTML = "";
  if (!violations?.length) {
    host.innerHTML = "<div class='violation'>Нарушения не найдены.</div>";
    return;
  }
  const dict = window.VIOLATION_DICTIONARY || {};
  const sev = window.SEVERITY_LABELS_RU || {};
  for (const v of violations) {
    const item = document.createElement("div");
    item.className = "violation";
    const tr = dict[v.code] || {};
    const title = tr.title || v.code || "Нарушение";
    const description = tr.description || v.message || "";
    const details = [];
    if (v.element_id) details.push(`Элемент: ${v.element_id}`);
    if (v.actual_text) details.push(`Текст: ${shortText(v.actual_text)}`);
    if (v.actual) details.push(`Обнаружено: ${v.actual}`);
    if (v.expected) details.push(`Ожидается: ${v.expected}`);
    const sevLabel = sev[v.severity] || v.severity || "—";
    item.innerHTML = `
      <div class="code">[!] ${title}</div>
      <div class="msg">${description}</div>
      <div class="kv">${details.join("\n")}</div>
      <div class="kv">Серьезность: ${sevLabel}</div>
    `;
    host.appendChild(item);
  }
}

async function runCheck() {
  const file = document.getElementById("fileInput").files?.[0];
  if (!file) {
    alert("Выберите DOCX файл");
    return;
  }
  const method = getSelectedMethod(METHODS_CACHE.methods, document.getElementById("methodSelect").value);
  const action = document.getElementById("actionSelect").value;
  const scopeId = method?.actions?.[action] || null;
  if (!scopeId) {
    alert("Для выбранного метода это действие недоступно.");
    return;
  }

  const params = new URLSearchParams({
    mode: action,
    scope_id: scopeId,
    profile: ACTIVE_PROFILE,
  });

  if (ACTIVE_PROFILE === "CUSTOM") {
    const checks = selectedCustomChecks();
    if (!checks.length) {
      alert("В режиме Custom выберите хотя бы одну проверку.");
      return;
    }
    params.set("custom_checks", checks.join(","));
  }

  if (CLASSIFY_CACHE && !CLASSIFY_CACHE.detected) {
    const manual = document.getElementById("manualClassSelect").value;
    if (manual) params.set("doc_class_override", manual);
  }

  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/api/run?${params.toString()}`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();

  document.getElementById("resultCard").style.display = "block";
  setupDownload(data.fixed_file);
  document.getElementById("metaBlock").textContent = JSON.stringify(
    {
      profile: data.profile,
      checker_ids: data.checker_ids,
      document_type: data.document_type,
      metrics: data.metrics,
    },
    null,
    2
  );

  const hs = document.getElementById("helpSummary");
  hs.innerHTML = `<div><b>${data.help?.summary || ""}</b></div>`;
  renderViolations(data.report?.violations || []);
}

async function reloadAll() {
  MODULES_CACHE = await loadModules();
  METHODS_CACHE = await loadMethods();
  fillMethodSelect(METHODS_CACHE.methods || []);
  fillCustomChecks(MODULES_CACHE.checker_catalog || []);
  applySelection();
}

const apiInputEl = document.getElementById("apiBaseInput");
apiInputEl.value = API_BASE;
apiInputEl.addEventListener("change", async () => {
  API_BASE = normalizeApi(apiInputEl.value);
  localStorage.setItem("gostchecker_api_base", API_BASE);
  await reloadAll();
});

document.getElementById("methodSelect").addEventListener("change", applySelection);
document.getElementById("actionSelect").addEventListener("change", applySelection);
document.getElementById("classifyBtn").addEventListener("click", async () => {
  try {
    await classifyDocument();
  } catch (e) {
    alert(e?.message || String(e));
  }
});
document.getElementById("runBtn").addEventListener("click", async () => {
  try {
    if (!METHODS_CACHE || !MODULES_CACHE) await reloadAll();
    await runCheck();
  } catch (e) {
    alert(e?.message || String(e));
  }
});

document.getElementById("profileLightBtn").addEventListener("click", () => setProfile("LIGHT"));
document.getElementById("profileMediumBtn").addEventListener("click", () => setProfile("MEDIUM"));
document.getElementById("profileHardBtn").addEventListener("click", () => setProfile("HARD"));
document.getElementById("profileCustomBtn").addEventListener("click", () => setProfile("CUSTOM"));

(async () => {
  await reloadAll();
  setProfile("HARD");
})();

