/* ============================================================
   MEDCHECK AI — script.js
   Vanilla JavaScript — no frameworks, no libraries
   ============================================================ */

"use strict";

/* ── Mock data ─────────────────────────────────────────────── */
const MOCK_RESULT = {
  claim:
    "A vitamina C em altas doses previne e trata infecções respiratórias, reduzindo significativamente a duração e gravidade de gripes e resfriados.",
  classification: "inconclusive",
  supportLevel: 38,
  explanation:
    "As evidências científicas disponíveis não sustentam de forma consistente a alegação de que a vitamina C em altas doses previne infecções respiratórias na população geral. Metanálises de ensaios clínicos randomizados indicam que a suplementação pode reduzir modestamente a duração de sintomas em populações específicas (atletas de alta performance), mas os efeitos são pequenos e inconsistentes na população geral. A alegação de que 'previne' infecções não encontra suporte robusto nas revisões sistemáticas mais recentes.",
  highlights: [
    { text: "previne e trata infecções respiratórias", type: "problematic" },
    { text: "reduzindo significativamente", type: "problematic" },
    { text: "vitamina C em altas doses", type: "neutral" },
  ],
  references: [
    {
      title: "Vitamin C for preventing and treating the common cold",
      source: "Cochrane Database of Systematic Reviews",
      year: 2023,
      authors: "Hemilä H, Chalker E.",
      url: "https://pubmed.ncbi.nlm.nih.gov/",
      repo: "PubMed / Cochrane",
    },
    {
      title: "Supplementation of vitamin C reduces the incidence of infection in athletes",
      source: "British Journal of Nutrition",
      year: 2021,
      authors: "Peters EM, et al.",
      url: "https://pubmed.ncbi.nlm.nih.gov/",
      repo: "PubMed",
    },
    {
      title: "Vitamin C and infections — a narrative review",
      source: "Nutrients",
      year: 2022,
      authors: "Carr AC, Maggini S.",
      url: "https://www.ncbi.nlm.nih.gov/pmc/",
      repo: "PubMed Central",
    },
    {
      title: "Vitaminas e imunidade: evidências e limitações das intervenções nutricionais",
      source: "Revista Brasileira de Medicina",
      year: 2022,
      authors: "Silva MR, Ferreira AT, Costa PL.",
      url: "https://www.scielo.br/",
      repo: "SciELO Brasil",
    },
  ],
};

const CLASSIFICATION_CONFIG = {
  supported:    { label: "Sustentado pelas evidências",  cls: "badge-supported" },
  inconclusive: { label: "Evidências inconclusivas",     cls: "badge-inconclusive" },
  contradicted: { label: "Contradito pelas evidências",  cls: "badge-contradicted" },
  insufficient: { label: "Evidências insuficientes",     cls: "badge-insufficient" },
};

const ANALYSIS_STEPS = [
  {
    label:    "Identificando alegações",
    sublabel: "Extraindo afirmações do conteúdo...",
    doneAt:   1200,
  },
  {
    label:    "Buscando evidências científicas",
    sublabel: "Consultando PubMed, SciELO, ScienceDirect...",
    doneAt:   3200,
  },
  {
    label:    "Comparando evidências",
    sublabel: "Avaliando consistência e relevância...",
    doneAt:   5400,
  },
  {
    label:    "Preparando resultado",
    sublabel: "Organizando as evidências encontradas...",
    doneAt:   7200,
  },
];

/* ── State ─────────────────────────────────────────────────── */
let currentScreen = "home"; // "home" | "loading" | "results"
let activeTab     = "text"; // "text" | "link"
let mobileMenuOpen = false;
let loadingTimers  = [];

/* ── DOM refs ──────────────────────────────────────────────── */
const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* ── Screen switching ──────────────────────────────────────── */
function showScreen(name) {
  currentScreen = name;
  $$(".screen").forEach(el => el.classList.remove("active"));
  const target = $(`#screen-${name}`);
  if (target) {
    target.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

/* ── Mobile menu ───────────────────────────────────────────── */
function toggleMobileMenu() {
  mobileMenuOpen = !mobileMenuOpen;
  const drawer = $("#mobile-drawer");
  const btn    = $("#mobile-menu-btn");

  drawer.classList.toggle("open", mobileMenuOpen);

  // Swap icon
  btn.innerHTML = mobileMenuOpen
    ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M4 4l12 12M16 4L4 16" stroke-linecap="round"/>
       </svg>`
    : `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M3 6h14M3 10h14M3 14h14" stroke-linecap="round"/>
       </svg>`;
}

function closeMobileMenu() {
  mobileMenuOpen = false;
  const drawer = $("#mobile-drawer");
  const btn    = $("#mobile-menu-btn");
  drawer.classList.remove("open");
  btn.innerHTML = `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M3 6h14M3 10h14M3 14h14" stroke-linecap="round"/>
  </svg>`;
}

/* ── Tab switching ─────────────────────────────────────────── */
function switchTab(tab) {
  activeTab = tab;
  $$(".tab-btn").forEach(btn => btn.classList.toggle("active", btn.dataset.tab === tab));
  $$(".input-panel").forEach(panel => panel.classList.toggle("active", panel.dataset.panel === tab));
  updateSubmitState();
}

/* ── Submit button state ───────────────────────────────────── */
function updateSubmitState() {
  const textVal = $("#content-textarea")?.value.trim() || "";
  const linkVal = $("#content-link")?.value.trim()     || "";
  const canSubmit = activeTab === "text" ? textVal.length > 0 : linkVal.length > 0;
  const btn = $("#submit-btn");
  if (btn) btn.disabled = !canSubmit;
}

/* ── Loading animation ─────────────────────────────────────── */
function startLoadingAnimation() {
  // Clear any previous timers
  loadingTimers.forEach(clearTimeout);
  loadingTimers = [];

  const rows = $$(".step-row");

  // Reset all rows to pending
  rows.forEach((row, i) => {
    const indicator = $(".step-indicator", row);
    const stepName  = $(".step-name", row);
    const stepSub   = $(".step-sub", row);
    const progressBar = $(".step-progress-bar", row);

    indicator.className = "step-indicator pending";
    indicator.innerHTML = `<span class="step-indicator-num">${i + 1}</span>`;
    stepName.className  = "step-name pending";
    stepName.textContent = ANALYSIS_STEPS[i].label;
    stepSub.textContent  = "Aguardando...";
    if (progressBar) progressBar.remove();
    row.classList.remove("is-active");
  });

  // Activate step 0 immediately
  activateStep(0);

  // Schedule subsequent activations and completions
  ANALYSIS_STEPS.forEach((step, i) => {
    // Activate next step
    if (i < ANALYSIS_STEPS.length - 1) {
      const t1 = setTimeout(() => activateStep(i + 1), step.doneAt);
      loadingTimers.push(t1);
    }
    // Complete this step
    const t2 = setTimeout(() => completeStep(i), step.doneAt);
    loadingTimers.push(t2);
  });

  // After all done, show results
  const totalTime = ANALYSIS_STEPS[ANALYSIS_STEPS.length - 1].doneAt + 900;
  const tFinal = setTimeout(() => {
    renderResults();
    showScreen("results");
  }, totalTime);
  loadingTimers.push(tFinal);
}

function activateStep(i) {
  const rows = $$(".step-row");
  if (!rows[i]) return;
  const row       = rows[i];
  const indicator = $(".step-indicator", row);
  const stepName  = $(".step-name", row);
  const stepSub   = $(".step-sub", row);

  row.classList.add("is-active");
  indicator.className = "step-indicator active";
  indicator.innerHTML = "";
  stepName.className  = "step-name active";
  stepSub.textContent = ANALYSIS_STEPS[i].sublabel;

  // Add progress bar
  if (!$(".step-progress-bar", row)) {
    const bar = document.createElement("div");
    bar.className = "step-progress-bar";
    bar.innerHTML = `<div class="step-progress-fill"></div>`;
    $(".step-info", row).appendChild(bar);
  }
}

function completeStep(i) {
  const rows = $$(".step-row");
  if (!rows[i]) return;
  const row       = rows[i];
  const indicator = $(".step-indicator", row);
  const stepName  = $(".step-name", row);
  const stepSub   = $(".step-sub", row);

  row.classList.remove("is-active");
  indicator.className = "step-indicator done";
  indicator.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M3 7l3 3 5-5" stroke="#17826A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  stepName.className  = "step-name done";
  stepSub.textContent = "Concluído";

  const progressBar = $(".step-progress-bar", row);
  if (progressBar) progressBar.remove();
}

/* ── Results rendering ─────────────────────────────────────── */
function getSupportLabel(level) {
  if (level >= 70) return "Forte suporte";
  if (level >= 40) return "Suporte moderado";
  if (level >= 20) return "Suporte fraco";
  return "Suporte muito limitado";
}

function getSupportClass(level) {
  if (level >= 70) return "strong";
  if (level >= 40) return "moderate";
  if (level >= 20) return "weak";
  return "minimal";
}

function renderResults() {
  const r   = MOCK_RESULT;
  const cfg = CLASSIFICATION_CONFIG[r.classification];

  // Claim
  const claimEl = $("#result-claim");
  if (claimEl) claimEl.textContent = `"${r.claim}"`;

  // Classification badge
  const badgeEl = $("#result-badge");
  if (badgeEl) {
    badgeEl.className  = `classification-badge ${cfg.cls}`;
    badgeEl.innerHTML  = `
      <span class="badge-dot"></span>
      <span class="badge-label">${cfg.label}</span>`;
  }

  // Support bar
  const fillEl  = $("#support-bar-fill");
  const labelEl = $("#support-bar-label");
  if (fillEl) {
    fillEl.className = `support-bar-fill ${getSupportClass(r.supportLevel)}`;
    // Animate after small delay for transition to kick in
    setTimeout(() => { fillEl.style.width = r.supportLevel + "%"; }, 50);
  }
  if (labelEl) labelEl.textContent = getSupportLabel(r.supportLevel);

  // Explanation
  const explEl = $("#result-explanation");
  if (explEl) explEl.textContent = r.explanation;

  // Highlights
  const hlList = $("#highlights-list");
  if (hlList) {
    hlList.innerHTML = r.highlights.map(h => `
      <div class="highlight-item ${h.type}">
        ${h.type === "problematic"
          ? `<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
               <path d="M7 2L1 12h12L7 2zM7 6v3M7 10.5h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
             </svg>`
          : `<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
               <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.3"/>
             </svg>`
        }
        <span class="highlight-text">"${h.text}"</span>
      </div>`).join("");
  }

  // References
  const refList = $("#references-list");
  if (refList) {
    refList.innerHTML = r.references.map(ref => `
      <div class="ref-card">
        <div class="ref-meta">
          <div class="ref-tags">
            <span class="ref-repo-tag">${ref.repo}</span>
            <span class="ref-year">${ref.year}</span>
          </div>
          <div class="ref-title">${ref.title}</div>
          <div class="ref-authors">${ref.authors} · <em>${ref.source}</em></div>
        </div>
        <a href="${ref.url}" target="_blank" rel="noopener noreferrer" class="view-study-btn">
          Ver estudo
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 8L8 2M8 2H4M8 2v4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
        </a>
      </div>`).join("");
  }
}

/* ── Navigation helpers ────────────────────────────────────── */
function goHome() {
  loadingTimers.forEach(clearTimeout);
  loadingTimers = [];
  showScreen("home");
}

function scrollToSection(id) {
  closeMobileMenu();
  if (currentScreen !== "home") {
    showScreen("home");
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: "smooth" });
    }, 150);
  } else {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  }
}

/* ── Init ──────────────────────────────────────────────────── */
function init() {
  /* Mobile menu */
  const mobileBtn = $("#mobile-menu-btn");
  if (mobileBtn) mobileBtn.addEventListener("click", toggleMobileMenu);

  /* Logo → home */
  $$(".logo-btn").forEach(btn => btn.addEventListener("click", goHome));

  /* Desktop nav */
  $$("[data-nav]").forEach(el => {
    el.addEventListener("click", () => {
      const target = el.dataset.nav;
      if (target === "home" || target === "analyze") {
        closeMobileMenu();
        goHome();
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        scrollToSection(target);
      }
    });
  });

  /* Tabs */
  $$(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  /* Input fields → update submit state */
  const textarea = $("#content-textarea");
  const linkInput = $("#content-link");
  if (textarea)  textarea.addEventListener("input", updateSubmitState);
  if (linkInput) linkInput.addEventListener("input", updateSubmitState);

  /* Submit button */
  const submitBtn = $("#submit-btn");
  if (submitBtn) {
    submitBtn.addEventListener("click", () => {
      if (submitBtn.disabled) return;
      showScreen("loading");
      startLoadingAnimation();
    });
  }

  /* New analysis buttons */
  $$(".new-analysis-trigger").forEach(btn => {
    btn.addEventListener("click", goHome);
  });

  /* Initialize tab state */
  switchTab("text");
  updateSubmitState();

  /* Initialize support bar at 0 so transition works */
  const fill = $("#support-bar-fill");
  if (fill) fill.style.width = "0%";
}

document.addEventListener("DOMContentLoaded", init);
