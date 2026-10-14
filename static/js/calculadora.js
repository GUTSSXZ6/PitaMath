'use strict';

// PitaMath: interface da calculadora. O Python/Flask realiza os cálculos.
document.addEventListener('DOMContentLoaded', () => {
  const $ = (id) => document.getElementById(id);
  const input = $('expressao');
  const visor = $('resultado-visor');
  const feedback = $('mensagem-calculadora');
  const placeholder = $('estado-inicial');
  const conteudo = $('conteudo-solucao');
  const erroBox = $('erro-solucao');
  const textoErro = $('texto-erro');
  const expressaoResolvida = $('expressao-resolvida');
  const resultadoFinal = $('resultado-final');
  const listaEtapas = $('lista-etapas');
  const observacao = $('observacao-solucao');
  const copiar = $('copiar-resolucao');
  const listaHistorico = $('lista-historico');
  const historicoVazio = $('historico-vazio');
  const limparHistorico = $('limpar-historico');
  if (!input || !visor) return;

  const historico = [];
  let resolucaoCopiavel = '';
  let calculando = false;
  const LIMITE = Number(input.maxLength) || 200;

  function mensagem(texto) { feedback.textContent = texto; }
  function inserir(texto) {
    if (calculando) return;
    const inicio = input.selectionStart ?? input.value.length;
    const fim = input.selectionEnd ?? inicio;
    const nova = input.value.slice(0, inicio) + texto + input.value.slice(fim);
    if (nova.length > LIMITE) { mensagem(`Limite de ${LIMITE} caracteres.`); return; }
    input.value = nova;
    const posicao = inicio + texto.length;
    input.focus(); input.setSelectionRange(posicao, posicao);
    mensagem('');
  }
  function apagar() {
    const inicio = input.selectionStart ?? input.value.length;
    const fim = input.selectionEnd ?? inicio;
    if (inicio !== fim) {
      input.setRangeText('', inicio, fim, 'start');
    } else if (inicio > 0) {
      input.setRangeText('', inicio - 1, inicio, 'start');
    }
    input.focus(); mensagem('');
  }
  function limpar() {
    input.value = ''; visor.textContent = '0'; mensagem('');
    mostrarInicial(); input.focus();
  }
  function mostrarInicial() {
    placeholder.hidden = false; conteudo.hidden = true; erroBox.hidden = true;
    copiar.disabled = true; resolucaoCopiavel = '';
  }
  function mostrarErro(texto) {
    placeholder.hidden = true; conteudo.hidden = true; erroBox.hidden = false;
    textoErro.textContent = texto; copiar.disabled = true; resolucaoCopiavel = '';
    mensagem(texto);
  }
  function alterarSinal() {
    const valor = input.value.trim();
    if (!valor) { inserir('−'); return; }
    // Aplica sinal à expressão inteira, sem tentar reinterpretar termos.
    input.value = valor.startsWith('−(') && valor.endsWith(')')
      ? valor.slice(2, -1) : `−(${valor})`;
    input.focus(); mensagem('');
  }
  function exibirResolucao(expressao, dados) {
    const resultado = String(dados.resultado);
    const etapas = dados.etapas;
    visor.textContent = resultado;
    expressaoResolvida.textContent = expressao;
    resultadoFinal.textContent = resultado;
    listaEtapas.replaceChildren();
    for (const etapa of etapas) {
      const li = document.createElement('li');
      li.textContent = typeof etapa === 'string' ? etapa : etapa.texto;
      listaEtapas.appendChild(li);
    }
    const nota = dados.observacao ? String(dados.observacao) : '';
    observacao.textContent = nota; observacao.hidden = !nota;
    placeholder.hidden = true; erroBox.hidden = true; conteudo.hidden = false;
    resolucaoCopiavel = `${expressao} = ${resultado}\n\n${etapas.map((e, i) => `${i + 1}. ${typeof e === 'string' ? e : e.texto}`).join('\n')}${nota ? `\n\n${nota}` : ''}`;
    copiar.disabled = false; mensagem('Cálculo concluído.');
    historico.unshift({ expressao, resultado });
    if (historico.length > 20) historico.pop();
    renderizarHistorico();
  }
  function renderizarHistorico() {
    listaHistorico.replaceChildren();
    historicoVazio.hidden = historico.length > 0;
    limparHistorico.disabled = historico.length === 0;
    for (const item of historico) {
      const li = document.createElement('li');
      const botao = document.createElement('button');
      botao.type = 'button'; botao.className = 'history-item';
      botao.textContent = `${item.expressao} = ${item.resultado}`;
      botao.title = 'Reutilizar esta expressão';
      botao.addEventListener('click', () => {
        input.value = item.expressao; input.focus();
        document.getElementById('calculadora')?.scrollIntoView({ behavior: 'smooth' });
      });
      li.appendChild(botao); listaHistorico.appendChild(li);
    }
  }
  async function calcular() {
    if (calculando) return;
    const expressao = input.value.trim();
    if (!expressao) { mostrarErro('Digite uma expressão antes de calcular.'); return; }
    if (expressao.length > LIMITE) { mostrarErro('Expressão muito longa.'); return; }
    calculando = true; mensagem('Calculando...');
    const botaoIgual = document.querySelector('[data-action="calculate"]');
    if (botaoIgual) botaoIgual.disabled = true;
    try {
      const resposta = await fetch('/api/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expressao }),
      });
      let dados;
      try { dados = await resposta.json(); }
      catch { throw new Error('O servidor não retornou uma resposta JSON válida.'); }
      if (!resposta.ok || dados.erro) {
        throw new Error(typeof dados.erro === 'string' ? dados.erro : 'Não foi possível resolver a expressão.');
      }
      if (dados.resultado === undefined || dados.resultado === null || !Array.isArray(dados.etapas)) {
        throw new Error('Resposta incompleta do servidor: esperado resultado e etapas.');
      }
      if (!dados.etapas.every(e => typeof e === 'string' || (e && typeof e.texto === 'string'))) {
        throw new Error('Formato das etapas de resolução inválido.');
      }
      exibirResolucao(expressao, dados);
    } catch (erro) {
      mostrarErro(erro instanceof TypeError
        ? 'Não foi possível conectar ao servidor. Verifique se o Flask está em execução.'
        : erro.message);
    } finally {
      calculando = false;
      if (botaoIgual) botaoIgual.disabled = false;
    }
  }

  document.querySelectorAll('.calculator-keyboard button').forEach(botao => {
    botao.addEventListener('click', () => {
      switch (botao.dataset.action) {
        case 'clear': limpar(); break;
        case 'backspace': apagar(); break;
        case 'toggle-sign': alterarSinal(); break;
        case 'calculate': calcular(); break;
        default: if (botao.dataset.value) inserir(botao.dataset.value);
      }
    });
  });
  document.querySelectorAll('[data-example]').forEach(botao => {
    botao.addEventListener('click', () => {
      input.value = botao.dataset.example || '';
      document.getElementById('calculadora')?.scrollIntoView({ behavior: 'smooth' });
      input.focus(); mensagem('Exemplo inserido. Pressione = para calcular.');
    });
  });
  input.addEventListener('keydown', (evento) => {
    if (evento.key === 'Enter' || (evento.key === '=' && !evento.ctrlKey)) {
      evento.preventDefault(); calcular();
    } else if (evento.key === 'Escape') {
      evento.preventDefault(); limpar();
    }
  });
  copiar?.addEventListener('click', async () => {
    if (!resolucaoCopiavel) return;
    try {
      await navigator.clipboard.writeText(resolucaoCopiavel);
      mensagem('Resolução copiada.');
    } catch { mensagem('Não foi possível copiar. Verifique a permissão do navegador.'); }
  });
  limparHistorico?.addEventListener('click', () => {
    historico.length = 0; renderizarHistorico(); mensagem('Histórico limpo.');
  });
  mostrarInicial();
});
