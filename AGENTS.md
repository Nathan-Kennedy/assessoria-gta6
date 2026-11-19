# Instruções para agentes (Claude Code, Codex, Gemini, etc.)

Este repositório tem duas partes:

1. **Niche Finder / Assessoria** (`index.html`, `ideias/`): análise dos canais de GTA 6, as oportunidades e as ideias de vídeo. O site fica em https://nathan-kennedy.github.io/assessoria-gta6/
2. **Produção** (`producao/`): como fazemos os vídeos do canal **Gangstar Games** (GTA 6), do roteiro até a postagem, com os scripts que usamos.

**Antes de fazer qualquer vídeo, leia `producao/LEIA-ME.md`.** Ele mostra o caminho completo e indica o guia de cada etapa.

## Regras rápidas

- Responda e escreva em **português do Brasil**.
- Nada de arte parada (PNG) para explicar algo dinâmico: gráfico, mapa, comparação e linha do tempo viram **motion no Remotion**.
- Nunca invente fato, número ou fonte. O que for boato aparece como boato, na fala e na tela.
- Não rode duas tarefas pesadas de GPU ao mesmo tempo (voz + whisper, ComfyUI + render). Em PC de 8 GB de VRAM, tudo trava e o PC pode desligar.
- Os scripts têm caminhos absolutos do PC original (`C:\Projetos Dev\...`, `C:\deps\...`). Ajuste os caminhos para a sua máquina antes de rodar.
- Não coloque chave de API, senha, cookie, áudio de referência de voz nem vídeo bruto neste repositório (ele é público).
