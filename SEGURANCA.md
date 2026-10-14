# Segurança do PitaMath

Esta versão mantém a lógica matemática e as rotas da aplicação, adicionando proteções HTTP:

- Flask com `debug=False` e host local `127.0.0.1` para desenvolvimento.
- JSON obrigatório nas rotas de cálculo, corpo limitado a 8 KB.
- Limite simples de 60 requisições por minuto por IP, em memória.
- CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy e Permissions-Policy.
- Respostas de API sem cache; erros internos não mostram detalhes ao visitante.
- Nenhum `eval()` de entrada do usuário; o módulo básico usa AST restrita.

## Para publicar na internet

Não use `python app.py` como servidor de produção. Use um servidor WSGI como Gunicorn em Linux (ex.: `gunicorn app:app --bind 0.0.0.0:$PORT`) e HTTPS pela plataforma de hospedagem. Configure limites de requisição também no proxy/plataforma. O limitador em memória não funciona de forma global em múltiplos processos, não resiste a reinicializações e pode agrupar usuários que compartilham IP. Para produção com tráfego real, substitua por Redis + Flask-Limiter (ou limitação no proxy). Não ative debug no ambiente público. Mantenha Flask e dependências atualizados.

Este endurecimento não é auditoria ou garantia de invulnerabilidade. Antes da publicação, rode todos os testes, revise logs, dependências, deploy, HTTPS e tratamento de dados.
