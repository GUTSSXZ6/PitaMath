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

  // Calculadora escolar: interface independente da calculadora básica.
  const formFracoes = $('form-fracoes');
  if (formFracoes) {
    const primeira = $('fracao-primeira');
    const operador = $('fracao-operador');
    const segunda = $('fracao-segunda');
    const botaoFracoes = $('calcular-fracoes');
    const mensagemFracoes = $('mensagem-fracoes');
    const inicialFracoes = $('estado-inicial-fracoes');
    const conteudoFracoes = $('conteudo-fracoes');
    const erroFracoes = $('erro-fracoes');
    const copiarFracoes = $('copiar-fracoes');
    let textoCopiarFracoes = '';
    const simbolos = { '+': '+', '-': '−', '*': '×', '/': '÷' };

    function falhaFracoes(texto) {
      inicialFracoes.hidden = true;
      conteudoFracoes.hidden = true;
      erroFracoes.hidden = false;
      $('texto-erro-fracoes').textContent = texto;
      mensagemFracoes.textContent = texto;
      copiarFracoes.disabled = true;
      textoCopiarFracoes = '';
    }

    formFracoes.addEventListener('submit', async (evento) => {
      evento.preventDefault();
      const a = primeira.value.trim();
      const b = segunda.value.trim();
      const op = operador.value;
      if (!a || !b) { falhaFracoes('Informe as duas frações.'); return; }
      if (!/^[+-]?\d+\s*\/\s*[+-]?\d+$/.test(a) || !/^[+-]?\d+\s*\/\s*[+-]?\d+$/.test(b)) {
        falhaFracoes('Use o formato numerador/denominador, por exemplo 1/2.');
        return;
      }
      botaoFracoes.disabled = true;
      mensagemFracoes.textContent = 'Calculando...';
      try {
        const resposta = await fetch('/api/escolar/fracoes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ primeira: a, operador: op, segunda: b }),
        });
        const dados = await resposta.json();
        if (!resposta.ok || dados.erro) throw new Error(dados.erro || 'Não foi possível calcular.');
        if (dados.resultado == null || !Array.isArray(dados.etapas) || !dados.etapas.every(e => typeof e === 'string')) {
          throw new Error('O servidor retornou uma resolução inválida.');
        }
        const expressao = `${a} ${simbolos[op]} ${b}`;
        $('expressao-fracoes').textContent = expressao;
        $('resultado-fracoes').textContent = String(dados.resultado);
        const etapas = $('etapas-fracoes');
        etapas.replaceChildren();
        dados.etapas.forEach(etapa => {
          const li = document.createElement('li');
          li.textContent = etapa;
          etapas.appendChild(li);
        });
        const nota = dados.observacao ? String(dados.observacao) : '';
        $('observacao-fracoes').textContent = nota;
        $('observacao-fracoes').hidden = !nota;
        textoCopiarFracoes = `${expressao} = ${dados.resultado}\n\n${dados.etapas.map((e, i) => `${i + 1}. ${e}`).join('\n')}${nota ? `\n\n${nota}` : ''}`;
        inicialFracoes.hidden = true;
        erroFracoes.hidden = true;
        conteudoFracoes.hidden = false;
        copiarFracoes.disabled = false;
        mensagemFracoes.textContent = 'Cálculo concluído.';
      } catch (erro) {
        falhaFracoes(erro instanceof TypeError
          ? 'Não foi possível conectar ao servidor. Verifique se o Flask está em execução.'
          : erro.message);
      } finally {
        botaoFracoes.disabled = false;
      }
    });
    copiarFracoes.addEventListener('click', async () => {
      if (!textoCopiarFracoes) return;
      try {
        await navigator.clipboard.writeText(textoCopiarFracoes);
        mensagemFracoes.textContent = 'Resolução copiada.';
      } catch {
        mensagemFracoes.textContent = 'Não foi possível copiar a resolução.';
      }
    });
  }

  // MMC/MDC — 2 a 10 números. Os cálculos são feitos exclusivamente no Python.
  const painelFracoes = $('painel-fracoes');
  const painelMmc = $('painel-mmc-mdc');
  document.querySelectorAll('[data-school-tab]').forEach(botao => {
    botao.addEventListener('click', () => {
      const aba = botao.dataset.schoolTab;
      painelFracoes.hidden = aba !== 'fracoes';
      painelMmc.hidden = aba !== 'mmc-mdc';
      const painelConteudos = $('painel-conteudos');
      if (painelConteudos) painelConteudos.hidden = aba !== 'conteudos';
      document.querySelectorAll('[data-school-tab]').forEach(b => {
        const ativo = b === botao;
        b.classList.toggle('active', ativo);
        b.setAttribute('aria-pressed', String(ativo));
      });
    });
  });

  const formMmc = $('form-mmc-mdc');
  if (formMmc) {
    const campos = $('campos-mmc-mdc');
    const adicionar = $('adicionar-numero');
    const tipo = $('tipo-mmc-mdc');
    const enviar = $('calcular-mmc-mdc');
    const aviso = $('mensagem-mmc-mdc');
    const inicial = $('estado-inicial-mmc-mdc');
    const conteudoMmc = $('conteudo-mmc-mdc');
    const erroMmc = $('erro-mmc-mdc');
    const copiarMmc = $('copiar-mmc-mdc');
    let textoCopiar = '';
    let ocupado = false;
    let proximoId = 3;

    function atualizarCampos() {
      const itens = [...campos.querySelectorAll('.number-field')];
      itens.forEach((item, indice) => {
        const label = item.querySelector('label');
        label.textContent = `Número ${indice + 1}`;
        const botao = item.querySelector('.number-remove');
        if (botao) botao.hidden = itens.length <= 2;
      });
      adicionar.disabled = itens.length >= 10 || ocupado;
    }
    function adicionarCampo() {
      if (campos.children.length >= 10 || ocupado) return;
      const id = `numero-mmc-${proximoId++}`;
      const item = document.createElement('div');
      item.className = 'number-field fraction-field';
      const rotulo = document.createElement('div');
      rotulo.className = 'number-label-row';
      const label = document.createElement('label');
      label.htmlFor = id;
      const remover = document.createElement('button');
      remover.type = 'button';
      remover.className = 'number-remove';
      remover.textContent = 'Remover';
      remover.addEventListener('click', () => {
        if (campos.children.length <= 2 || ocupado) return;
        item.remove(); atualizarCampos();
      });
      rotulo.append(label, remover);
      const campo = document.createElement('input');
      campo.id = id; campo.type = 'number'; campo.inputMode = 'numeric';
      campo.min = '1'; campo.max = '1000000'; campo.step = '1'; campo.required = true;
      campo.placeholder = 'Ex.: 24';
      item.append(rotulo, campo);
      campos.appendChild(item);
      atualizarCampos(); campo.focus();
    }
    adicionar.addEventListener('click', adicionarCampo);
    tipo.addEventListener('change', () => {
      enviar.textContent = `Calcular ${tipo.value.toUpperCase()}`;
    });
    atualizarCampos();

    function falha(texto) {
      inicial.hidden = true; conteudoMmc.hidden = true; erroMmc.hidden = false;
      $('texto-erro-mmc-mdc').textContent = texto;
      aviso.textContent = texto; copiarMmc.disabled = true; textoCopiar = '';
    }
    formMmc.addEventListener('submit', async evento => {
      evento.preventDefault();
      if (ocupado) return;
      const entradas = [...campos.querySelectorAll('input')];
      const numeros = [];
      for (const campo of entradas) {
        const valor = campo.value.trim();
        if (!/^\d+$/.test(valor) || !Number.isSafeInteger(Number(valor)) || Number(valor) < 1 || Number(valor) > 1000000) {
          falha('Informe apenas inteiros positivos de 1 a 1.000.000.'); campo.focus(); return;
        }
        numeros.push(Number(valor));
      }
      if (numeros.length < 2 || numeros.length > 10) { falha('Informe de 2 a 10 números.'); return; }
      ocupado = true; enviar.disabled = true; adicionar.disabled = true;
      aviso.textContent = 'Calculando...';
      try {
        const resposta = await fetch('/api/escolar/mmc-mdc', {
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ numeros, operacao: tipo.value })
        });
        const dados = await resposta.json();
        if (!resposta.ok || dados.erro) throw new Error(dados.erro || 'Não foi possível calcular.');
        if (dados.resultado == null || !Array.isArray(dados.etapas)) throw new Error('Resposta incompleta do servidor.');
        const expressao = `${tipo.value.toUpperCase()}(${numeros.join(', ')})`;
        $('expressao-mmc-mdc').textContent = expressao;
        $('resultado-mmc-mdc').textContent = String(dados.resultado);
        const lista = $('etapas-mmc-mdc'); lista.replaceChildren();
        dados.etapas.forEach(etapa => {
          const li = document.createElement('li');
          li.textContent = typeof etapa === 'string' ? etapa : etapa.texto;
          lista.appendChild(li);
        });
        const nota = dados.observacao || '';
        $('observacao-mmc-mdc').textContent = nota;
        $('observacao-mmc-mdc').hidden = !nota;
        textoCopiar = `${expressao} = ${dados.resultado}\n\n${dados.etapas.map((e,i)=>`${i+1}. ${typeof e === 'string' ? e : e.texto}`).join('\n')}${nota ? '\n\n'+nota : ''}`;
        inicial.hidden = true; erroMmc.hidden = true; conteudoMmc.hidden = false;
        copiarMmc.disabled = false; aviso.textContent = 'Cálculo concluído.';
      } catch (erro) {
        falha(erro instanceof TypeError ? 'Não foi possível conectar ao servidor Flask.' : erro.message);
      } finally {
        ocupado = false; enviar.disabled = false; atualizarCampos();
      }
    });
    copiarMmc.addEventListener('click', async () => {
      if (!textoCopiar) return;
      try { await navigator.clipboard.writeText(textoCopiar); aviso.textContent = 'Resolução copiada.'; }
      catch { aviso.textContent = 'Não foi possível copiar a resolução.'; }
    });
  }

  // Novos conteúdos escolares — o Python executa todos os cálculos.
  const formConteudos = $('form-conteudos');
  if (formConteudos) {
    const tipo = $('tipo-conteudo');
    const campos = $('campos-conteudos');
    const aviso = $('mensagem-conteudos');
    const enviar = $('calcular-conteudos');
    const copiar = $('copiar-conteudos');
    let textoCopiar = '';
    const modelos = {
      potencia: [['base', 'Base', '2'], ['expoente', 'Expoente', '5']],
      raiz: [['numero', 'Número (radicando)', '81'], ['indice', 'Índice da raiz', '2']],
      equacao: [['a', 'Coeficiente a', '2'], ['b', 'Coeficiente b', '3'], ['c', 'Resultado c', '11']],
      equacao2: [['a', 'Coeficiente a (x²)', '1'], ['b', 'Coeficiente b (x)', '-5'], ['c', 'Termo independente c', '6']]
    };
    function desenharCampos() {
      campos.replaceChildren();
      for (const [chave, rotulo, padrao] of modelos[tipo.value]) {
        const caixa = document.createElement('div'); caixa.className = 'fraction-field';
        const label = document.createElement('label'); label.htmlFor = `escolar-${chave}`; label.textContent = rotulo;
        const input = document.createElement('input'); input.type = 'number'; input.step = '1';
        input.required = true; input.id = `escolar-${chave}`; input.name = chave; input.value = padrao;
        caixa.append(label, input); campos.appendChild(caixa);
      }
      $('estado-inicial-conteudos').hidden = false;
      $('conteudo-conteudos').hidden = true;
      $('erro-conteudos').hidden = true;
      copiar.disabled = true; textoCopiar = ''; aviso.textContent = '';
    }
    tipo.addEventListener('change', desenharCampos);
    desenharCampos();
    formConteudos.addEventListener('submit', async evento => {
      evento.preventDefault();
      const dados = {tipo: tipo.value};
      for (const entrada of campos.querySelectorAll('input')) {
        if (!/^-?\d+$/.test(entrada.value.trim()) || !Number.isSafeInteger(Number(entrada.value))) {
          aviso.textContent = 'Informe apenas números inteiros válidos.'; entrada.focus(); return;
        }
        dados[entrada.name] = Number(entrada.value);
      }
      enviar.disabled = true; aviso.textContent = 'Calculando...';
      try {
        const resposta = await fetch('/api/escolar/conteudos', {
          method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados)
        });
        const retorno = await resposta.json();
        if (!resposta.ok || retorno.erro) throw new Error(retorno.erro || 'Erro ao calcular.');
        if (retorno.resultado == null || !Array.isArray(retorno.etapas)) throw new Error('Resposta incompleta do servidor.');
        $('resultado-conteudos').textContent = String(retorno.resultado);
        const lista = $('etapas-conteudos'); lista.replaceChildren();
        retorno.etapas.forEach(etapa => {const li = document.createElement('li'); li.textContent = String(etapa); lista.appendChild(li);});
        const obs = $('observacao-conteudos'); obs.textContent = retorno.observacao || ''; obs.hidden = !retorno.observacao;
        $('estado-inicial-conteudos').hidden = true; $('erro-conteudos').hidden = true;
        $('conteudo-conteudos').hidden = false;
        textoCopiar = `${tipo.options[tipo.selectedIndex].text}: ${retorno.resultado}\n${retorno.etapas.map((e,i)=>`${i+1}. ${e}`).join('\n')}`;
        copiar.disabled = false; aviso.textContent = 'Cálculo concluído.';
      } catch (erro) {
        $('estado-inicial-conteudos').hidden = true; $('conteudo-conteudos').hidden = true;
        $('erro-conteudos').hidden = false; $('texto-erro-conteudos').textContent = erro.message;
        aviso.textContent = erro.message; copiar.disabled = true;
      } finally { enviar.disabled = false; }
    });
    copiar.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(textoCopiar); aviso.textContent = 'Resolução copiada.'; }
      catch { aviso.textContent = 'Não foi possível copiar.'; }
    });
  }

  // Científica: interface e requisições. Os cálculos permanecem no Python.
  const formCientifica = document.getElementById('form-cientifica');
  if (formCientifica) {
    const el = id => document.getElementById(id);
    const operacao = el('operacao-cientifica');
    const campos = el('campos-cientifica');
    const modoCampo = el('modo-cientifica-campo');
    const botao = el('calcular-cientifica');
    const aviso = el('mensagem-cientifica');
    const copiar = el('copiar-cientifica');
    let textoCopiar = '';
    const trig = new Set(['sen','cos','tan','arcsen','arccos','arctan']);
    const modelos = {
      sen: [['valor','Ângulo','30']], cos: [['valor','Ângulo','60']], tan: [['valor','Ângulo','45']],
      arcsen: [['valor','Valor do seno (-1 a 1)','0,5']], arccos: [['valor','Valor do cosseno (-1 a 1)','0,5']], arctan: [['valor','Valor da tangente','1']],
      log: [['valor','Número (maior que zero)','100'],['base','Base (positiva e diferente de 1)','10']],
      ln: [['valor','Número (maior que zero)','2,71828']], exp: [['valor','Expoente de e','2']],
      potencia: [['base','Base','2'],['expoente','Expoente','5']], raiz: [['valor','Radicando','81'],['indice','Índice da raiz','4']],
      fatorial: [['valor','Inteiro de 0 a 170','5']], abs: [['valor','Número','-12']],
      notacao: [['valor','Número a converter','125000']], potencia10: [['valor','Expoente de 10','3']]
    };
    function desenhar() {
      campos.replaceChildren();
      modoCampo.hidden = !trig.has(operacao.value);
      for (const [nome, rotulo, exemplo] of modelos[operacao.value]) {
        const div = document.createElement('div'); div.className = 'fraction-field';
        const label = document.createElement('label'); label.htmlFor = `cientifica-${nome}`; label.textContent = rotulo;
        const input = document.createElement('input'); input.id = label.htmlFor; input.name = nome;
        input.type = 'text'; input.inputMode = 'decimal'; input.required = true; input.maxLength = 120;
        input.placeholder = `Ex.: ${exemplo}`; input.value = exemplo;
        div.append(label, input); campos.appendChild(div);
      }
      el('estado-inicial-cientifica').hidden = false;
      el('conteudo-cientifica').hidden = true;
      el('erro-cientifica').hidden = true;
      copiar.disabled = true; textoCopiar = ''; aviso.textContent = '';
    }
    operacao.addEventListener('change', desenhar);
    desenhar();
    formCientifica.addEventListener('submit', async event => {
      event.preventDefault();
      const dados = {operacao: operacao.value};
      if (trig.has(operacao.value)) dados.modo = el('modo-cientifica').value;
      for (const input of campos.querySelectorAll('input')) {
        const valor = input.value.trim();
        if (!/^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?$/.test(valor)) {
          aviso.textContent = 'Digite um número válido em cada campo.'; input.focus(); return;
        }
        dados[input.name] = valor.replace(',', '.');
      }
      botao.disabled = true; aviso.textContent = 'Calculando...';
      try {
        const resposta = await fetch('/api/cientifica', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(dados)});
        const retorno = await resposta.json();
        if (!resposta.ok || retorno.erro) throw new Error(retorno.erro || 'Não foi possível calcular.');
        if (retorno.resultado == null || !Array.isArray(retorno.etapas)) throw new Error('Resposta incompleta do servidor.');
        el('resultado-cientifica').textContent = String(retorno.resultado);
        const lista = el('etapas-cientifica'); lista.replaceChildren();
        retorno.etapas.forEach(etapa => { const li = document.createElement('li'); li.textContent = String(etapa); lista.appendChild(li); });
        const obs = el('observacao-cientifica'); obs.textContent = retorno.observacao || ''; obs.hidden = !retorno.observacao;
        el('estado-inicial-cientifica').hidden = true; el('erro-cientifica').hidden = true; el('conteudo-cientifica').hidden = false;
        textoCopiar = `${operacao.options[operacao.selectedIndex].text}: ${retorno.resultado}\n${retorno.etapas.join('\n')}${retorno.observacao ? '\n' + retorno.observacao : ''}`;
        copiar.disabled = false; aviso.textContent = 'Cálculo concluído.';
      } catch (erro) {
        el('estado-inicial-cientifica').hidden = true; el('conteudo-cientifica').hidden = true; el('erro-cientifica').hidden = false;
        el('texto-erro-cientifica').textContent = erro.message; aviso.textContent = erro.message; copiar.disabled = true;
      } finally { botao.disabled = false; }
    });
    copiar.addEventListener('click', async () => {
      if (!textoCopiar) return;
      try { await navigator.clipboard.writeText(textoCopiar); aviso.textContent = 'Explicação copiada!'; }
      catch { aviso.textContent = 'Não foi possível copiar.'; }
    });
  }

});
