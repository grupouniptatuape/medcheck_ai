/* ============================================================
   MEDCHECK AI — script.js
   JavaScript puro — sem frameworks e sem bibliotecas
   ============================================================ */

"use strict";

const URL_BACKEND = "http://192.168.0.19:8000";

async function enviarParaAnalise(tipo_entrada, conteudo) {
  const resposta = await fetch(`${URL_BACKEND}/analisar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      tipo_entrada: tipo_entrada,
      conteudo: conteudo
    })
  });

  return await resposta.json();
}

/* ── Dados simulados ─────────────────────────────────────────────── */
const RESULTADO_SIMULADO = {
  alegacao:
    "A vitamina C em altas doses previne e trata infecções respiratórias, reduzindo significativamente a duração e gravidade de gripes e resfriados.",
  classificacao: "inconclusive",
  nivel_suporte: 38,
  explicacao:
    "As evidências científicas disponíveis não sustentam de forma consistente a alegação de que a vitamina C em altas doses previne infecções respiratórias na população geral. Metanálises de ensaios clínicos randomizados indicam que a suplementação pode reduzir modestamente a duração de sintomas em populações específicas (atletas de alta performance), mas os efeitos são pequenos e inconsistentes na população geral. A alegação de que 'previne' infecções não encontra suporte robusto nas revisões sistemáticas mais recentes.",
  trechos: [
    { texto: "previne e trata infecções respiratórias", tipo: "problematic" },
    { texto: "reduzindo significativamente", tipo: "problematic" },
    { texto: "vitamina C em altas doses", tipo: "neutral" },
  ],
  evidencias: [
    {
      titulo: "Vitamin C for preventing and treating the common cold",
      fonte: "Cochrane Database of Systematic Reviews",
      ano: 2023,
      autores: "Hemilä H, Chalker E.",
      url: "https://pubmed.ncbi.nlm.nih.gov/",
      repositorio: "PubMed / Cochrane",
    },
    {
      titulo: "Supplementation of vitamin C reduces the incidence of infection in athletes",
      fonte: "British Journal of Nutrition",
      ano: 2021,
      autores: "Peters EM, et al.",
      url: "https://pubmed.ncbi.nlm.nih.gov/",
      repositorio: "PubMed",
    },
    {
      titulo: "Vitamin C and infections — a narrative review",
      fonte: "Nutrients",
      ano: 2022,
      autores: "Carr AC, Maggini S.",
      url: "https://www.ncbi.nlm.nih.gov/pmc/",
      repositorio: "PubMed Central",
    },
    {
      titulo: "Vitaminas e imunidade: evidências e limitações das intervenções nutricionais",
      fonte: "Revista Brasileira de Medicina",
      ano: 2022,
      autores: "Silva MR, Ferreira AT, Costa PL.",
      url: "https://www.scielo.br/",
      repositorio: "SciELO Brasil",
    },
  ],
};

const CONFIGURACAO_CLASSIFICACAO = {
  supported:    { rotulo: "Sustentado pelas evidências",  classe: "badge-supported" },
  inconclusive: { rotulo: "Evidências inconclusivas",     classe: "badge-inconclusive" },
  contradicted: { rotulo: "Contradito pelas evidências",  classe: "badge-contradicted" },
  insufficient: { rotulo: "Evidências insuficientes",     classe: "badge-insufficient" },
};

const ETAPAS_ANALISE = [
  {
    rotulo:    "Identificando alegações",
    subrotulo: "Extraindo afirmações do conteúdo...",
    conclui_em:   1200,
  },
  {
    rotulo:    "Buscando evidências científicas",
    subrotulo: "Consultando PubMed, SciELO, ScienceDirect...",
    conclui_em:   3200,
  },
  {
    rotulo:    "Comparando evidências",
    subrotulo: "Avaliando consistência e relevância...",
    conclui_em:   5400,
  },
  {
    rotulo:    "Preparando resultado",
    subrotulo: "Organizando as evidências encontradas...",
    conclui_em:   7200,
  },
];

/* ── Estado ─────────────────────────────────────────────────── */
let tela_atual = "home"; // "home" | "loading" | "results"
let aba_ativa     = "text"; // "text" | "link"
let menu_mobile_aberto = false;
let temporizadores_carregamento  = [];

/* ── Referências do DOM ──────────────────────────────────────────────── */
const selecionar = (seletor, contexto = document) => contexto.querySelector(seletor);
const selecionarTodos = (seletor, contexto = document) => [...contexto.querySelectorAll(seletor)];

/* ── Troca de telas ──────────────────────────────────────── */
function mostrarTela(nome) {
  tela_atual = nome;
  selecionarTodos(".screen").forEach(elemento => elemento.classList.remove("active"));
  const alvo = selecionar(`#screen-${nome}`);
  if (alvo) {
    alvo.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

/* ── Menu mobile ───────────────────────────────────────────── */
function alternarMenuMobile() {
  menu_mobile_aberto = !menu_mobile_aberto;
  const menu = selecionar("#mobile-drawer");
  const botao    = selecionar("#mobile-menu-btn");

  menu.classList.toggle("open", menu_mobile_aberto);

  // Alterna o ícone
  botao.innerHTML = menu_mobile_aberto
    ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M4 4l12 12M16 4L4 16" stroke-linecap="round"/>
       </svg>`
    : `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
         <path d="M3 6h14M3 10h14M3 14h14" stroke-linecap="round"/>
       </svg>`;
}

function fecharMenuMobile() {
  menu_mobile_aberto = false;
  const menu = selecionar("#mobile-drawer");
  const botao    = selecionar("#mobile-menu-btn");
  menu.classList.remove("open");
  botao.innerHTML = `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M3 6h14M3 10h14M3 14h14" stroke-linecap="round"/>
  </svg>`;
}

/* ── Troca de abas ─────────────────────────────────────────── */
function trocarAba(aba) {
  aba_ativa = aba;
  selecionarTodos(".tab-btn").forEach(botao => botao.classList.toggle("active", botao.dataset.tab === aba));
  selecionarTodos(".input-panel").forEach(painel => painel.classList.toggle("active", painel.dataset.panel === aba));
  atualizarEstadoBotao();
}

/* ── Estado do botão de envio ───────────────────────────────────── */
function atualizarEstadoBotao() {
  const valor_texto = selecionar("#content-textarea")?.value.trim() || "";
  const valor_link = selecionar("#content-link")?.value.trim()     || "";
  const pode_enviar = aba_ativa === "text" ? valor_texto.length > 0 : valor_link.length > 0;
  const botao = selecionar("#submit-btn");
  if (botao) botao.disabled = !pode_enviar;
}

/* ── Animação de carregamento ─────────────────────────────────────── */
function iniciarAnimacaoCarregamento() {
  // Limpa temporizadores anteriores
  temporizadores_carregamento.forEach(clearTimeout);
  temporizadores_carregamento = [];

  const linhas = selecionarTodos(".step-row");

  // Reinicia todas as etapas como pendentes
  linhas.forEach((linha, i) => {
    const indicador = selecionar(".step-indicator", linha);
    const nome_etapa  = selecionar(".step-name", linha);
    const subtexto_etapa   = selecionar(".step-sub", linha);
    const barra_progresso = selecionar(".step-progress-bar", linha);

    indicador.className = "step-indicator pending";
    indicador.innerHTML = `<span class="step-indicator-num">${i + 1}</span>`;
    nome_etapa.className  = "step-name pending";
    nome_etapa.textContent = ETAPAS_ANALISE[i].rotulo;
    subtexto_etapa.textContent  = "Aguardando...";
    if (barra_progresso) barra_progresso.remove();
    linha.classList.remove("is-active");
  });

  // Ativa a primeira etapa imediatamente
  ativarEtapa(0);

  // Agenda as ativações e conclusões das próximas etapas
  ETAPAS_ANALISE.forEach((etapa, i) => {
    // Ativa a próxima etapa
    if (i < ETAPAS_ANALISE.length - 1) {
      const temporizador_ativacao = setTimeout(() => ativarEtapa(i + 1), etapa.conclui_em);
      temporizadores_carregamento.push(temporizador_ativacao);
    }
    // Conclui esta etapa
    const temporizador_conclusao = setTimeout(() => concluirEtapa(i), etapa.conclui_em);
    temporizadores_carregamento.push(temporizador_conclusao);
  });

  // Depois de concluir todas as etapas, exibe os resultados
  const tempo_total = ETAPAS_ANALISE[ETAPAS_ANALISE.length - 1].conclui_em + 900;
  const temporizador_final = setTimeout(() => {
    exibirResultados();
    mostrarTela("results");
  }, tempo_total);
  temporizadores_carregamento.push(temporizador_final);
}

function ativarEtapa(i) {
  const linhas = selecionarTodos(".step-row");
  if (!linhas[i]) return;
  const linha       = linhas[i];
  const indicador = selecionar(".step-indicator", linha);
  const nome_etapa  = selecionar(".step-name", linha);
  const subtexto_etapa   = selecionar(".step-sub", linha);

  linha.classList.add("is-active");
  indicador.className = "step-indicator active";
  indicador.innerHTML = "";
  nome_etapa.className  = "step-name active";
  subtexto_etapa.textContent = ETAPAS_ANALISE[i].subrotulo;

  // Adiciona a barra de progresso
  if (!selecionar(".step-progress-bar", linha)) {
    const nova_barra = document.createElement("div");
    nova_barra.className = "step-progress-bar";
    nova_barra.innerHTML = `<div class="step-progress-fill"></div>`;
    selecionar(".step-info", linha).appendChild(nova_barra);
  }
}

function concluirEtapa(i) {
  const linhas = selecionarTodos(".step-row");
  if (!linhas[i]) return;
  const linha       = linhas[i];
  const indicador = selecionar(".step-indicator", linha);
  const nome_etapa  = selecionar(".step-name", linha);
  const subtexto_etapa   = selecionar(".step-sub", linha);

  linha.classList.remove("is-active");
  indicador.className = "step-indicator done";
  indicador.innerHTML = `
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M3 7l3 3 5-5" stroke="#17826A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  nome_etapa.className  = "step-name done";
  subtexto_etapa.textContent = "Concluído";

  const barra_progresso = selecionar(".step-progress-bar", linha);
  if (barra_progresso) barra_progresso.remove();
}

/* ── Exibição dos resultados ─────────────────────────────────────── */
function obterRotuloSuporte(nivel) {
  if (nivel >= 70) return "Forte suporte";
  if (nivel >= 40) return "Suporte moderado";
  if (nivel >= 20) return "Suporte fraco";
  return "Suporte muito limitado";
}

function obterClasseSuporte(nivel) {
  if (nivel >= 70) return "strong";
  if (nivel >= 40) return "moderate";
  if (nivel >= 20) return "weak";
  return "minimal";
}

function exibirResultados() {
  const resultado   = RESULTADO_SIMULADO;
  const configuracao = CONFIGURACAO_CLASSIFICACAO[resultado.classificacao];

  // Alegação
  const elemento_alegacao = selecionar("#result-claim");
  if (elemento_alegacao) elemento_alegacao.textContent = `"${resultado.alegacao}"`;

  // Classificação
  const elemento_classificacao = selecionar("#result-badge");
  if (elemento_classificacao) {
    elemento_classificacao.className  = `classification-badge ${configuracao.classe}`;
    elemento_classificacao.innerHTML  = `
      <span class="badge-dot"></span>
      <span class="badge-label">${configuracao.rotulo}</span>`;
  }

  // Barra de suporte
  const elemento_barra  = selecionar("#support-bar-fill");
  const elemento_rotulo = selecionar("#support-bar-label");
  if (elemento_barra) {
    elemento_barra.className = `support-bar-fill ${obterClasseSuporte(resultado.nivel_suporte)}`;
    // Pequeno atraso para permitir a animação da transição
    setTimeout(() => { elemento_barra.style.width = resultado.nivel_suporte + "%"; }, 50);
  }
  if (elemento_rotulo) elemento_rotulo.textContent = obterRotuloSuporte(resultado.nivel_suporte);

  // Explicação
  const elemento_explicacao = selecionar("#result-explanation");
  if (elemento_explicacao) elemento_explicacao.textContent = resultado.explicacao;

  // Trechos identificados
  const lista_trechos = selecionar("#highlights-list");
  if (lista_trechos) {
    lista_trechos.innerHTML = resultado.trechos.map(trecho => `
      <div class="highlight-item ${trecho.tipo}">
        ${trecho.tipo === "problematic"
          ? `<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
               <path d="M7 2L1 12h12L7 2zM7 6v3M7 10.5h.01" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
             </svg>`
          : `<svg width="14" height="14" viewBox="0 0 14 14" fill="none">
               <circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.3"/>
             </svg>`
        }
        <span class="highlight-text">"${trecho.texto}"</span>
      </div>`).join("");
  }

  // Evidências
  const lista_evidencias = selecionar("#references-list");
  if (lista_evidencias) {
    lista_evidencias.innerHTML = resultado.evidencias.map(evidencia => `
      <div class="ref-card">
        <div class="ref-meta">
          <div class="ref-tags">
            <span class="ref-repo-tag">${evidencia.repositorio}</span>
            <span class="ref-year">${evidencia.ano}</span>
          </div>
          <div class="ref-title">${evidencia.titulo}</div>
          <div class="ref-authors">${evidencia.autores} · <em>${evidencia.fonte}</em></div>
        </div>
        <a href="${evidencia.url}" target="_blank" rel="noopener noreferrer" class="view-study-btn">
          Ver estudo
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 8L8 2M8 2H4M8 2v4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
        </a>
      </div>`).join("");
  }
}

/* ── Funções de navegação ────────────────────────────────────── */
function irParaInicio() {
  temporizadores_carregamento.forEach(clearTimeout);
  temporizadores_carregamento = [];
  mostrarTela("home");
}

function rolarParaSecao(id) {
  fecharMenuMobile();
  if (tela_atual !== "home") {
    mostrarTela("home");
    setTimeout(() => {
      const elemento = document.getElementById(id);
      if (elemento) elemento.scrollIntoView({ behavior: "smooth" });
    }, 150);
  } else {
    const elemento = document.getElementById(id);
    if (elemento) elemento.scrollIntoView({ behavior: "smooth" });
  }
}

/* ── Inicialização ──────────────────────────────────────────────────── */
function iniciar() {
  /* Menu mobile */
  const botao_mobile = selecionar("#mobile-menu-btn");
  if (botao_mobile) botao_mobile.addEventListener("click", alternarMenuMobile);

  /* Logo → início */
  selecionarTodos(".logo-btn").forEach(botao => botao.addEventListener("click", irParaInicio));

  /* Navegação desktop */
  selecionarTodos("[data-nav]").forEach(elemento => {
    elemento.addEventListener("click", () => {
      const alvo = elemento.dataset.nav;
      if (alvo === "home" || alvo === "analyze") {
        fecharMenuMobile();
        irParaInicio();
        window.scrollTo({ top: 0, behavior: "smooth" });
      } else {
        rolarParaSecao(alvo);
      }
    });
  });

  /* Abas */
  selecionarTodos(".tab-btn").forEach(botao => {
    botao.addEventListener("click", () => trocarAba(botao.dataset.tab));
  });

  /* Campos de entrada → atualizam o estado do botão */
  const campo_texto = selecionar("#content-textarea");
  const campo_link = selecionar("#content-link");
  if (campo_texto)  campo_texto.addEventListener("input", atualizarEstadoBotao);
  if (campo_link) campo_link.addEventListener("input", atualizarEstadoBotao);

  /* Botão de envio */
  const botao_enviar = selecionar("#submit-btn");
  if (botao_enviar) {
    botao_enviar.addEventListener("click", async () => {
  if (botao_enviar.disabled) return;

  const conteudo = aba_ativa === "text"
    ? selecionar("#content-textarea").value.trim()
    : selecionar("#content-link").value.trim();

  const tipo_entrada = aba_ativa === "text" ? "texto" : "link";

  mostrarTela("loading");
  iniciarAnimacaoCarregamento();

  const resultado = await enviarParaAnalise(tipo_entrada, conteudo);

  console.log("Resposta do backend:", resultado);
});
  }

  /* Botões de nova análise */
  selecionarTodos(".new-analysis-trigger").forEach(botao => {
    botao.addEventListener("click", irParaInicio);
  });

  /* Inicializa o estado da aba */
  trocarAba("text");
  atualizarEstadoBotao();

  /* Inicializa a barra de suporte em 0 para permitir a transição */
  const barra = selecionar("#support-bar-fill");
  if (barra) barra.style.width = "0%";
}

document.addEventListener("DOMContentLoaded", iniciar);
