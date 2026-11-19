# Produção dos vídeos do Gangstar Games (GTA 6)

Este é o mapa. Cada etapa tem um guia com o passo a passo, e os scripts estão em `ferramentas/`.

## O caminho de um vídeo

| # | Etapa | Ferramentas | Guia |
|---|-------|-------------|------|
| 0 | Escolher a ideia | Niche Finder (site deste repo, pasta `ideias/`) | este arquivo |
| 1 | Roteiro | Claude ou Codex, com o modelo de roteiro | [01_ROTEIRO.md](01_ROTEIRO.md) |
| 2 | Voz | a nossa voz gravada, voz clonada (VoxCPM2) ou DarkPlanner | [02_VOZ.md](02_VOZ.md) |
| 3 | Imagens e vídeos de IA | ComfyUI local (nossa config), Google Flow, ChatGPT | [03_IMAGENS_E_VIDEO_IA.md](03_IMAGENS_E_VIDEO_IA.md) |
| 4 | Motion graphics | Remotion (React) | [04_MOTION_REMOTION.md](04_MOTION_REMOTION.md) |
| 5 | Montagem e render | EffectCraft (montagem por script) e **FilmCraft (render final)** | [05_EDICAO_E_RENDER.md](05_EDICAO_E_RENDER.md) |
| 6 | Thumbnail e postagem | navegador com porta de depuração (CDP 9333) | [06_THUMB_E_POSTAGEM.md](06_THUMB_E_POSTAGEM.md) |

Não precisa usar todas as ferramentas em todo vídeo. Exemplos que funcionam:

- **Mais simples:** roteiro → voz no DarkPlanner → trechos do trailer e motion no Remotion → FilmCraft.
- **O nosso padrão:** roteiro → nossa voz (ou clonada) → motion no Remotion + cenas do trailer + notícias → montagem no EffectCraft → render final no FilmCraft.
- **Com IA visual:** igual ao padrão, mais cenas geradas no Flow (Veo) ou no ComfyUI para o que o trailer não mostra.

## Pastas de um vídeo

Cada vídeo tem uma pasta `AAAA-MM-DD_videoNN-<tema>/`:

```
ROTEIRO_PARA_NARRAR.txt   roteiro numerado (formato em 01_ROTEIRO.md)
ESTADO_ATUAL.md           o que já foi feito e o que falta; atualize sempre
BRIEF_*.md                tarefas entregues a outros agentes (Codex)
narracao_*/               áudios, falas.json e palavras.json (tempo de cada palavra)
motion/                   projeto Remotion (cópia de modelos/motion-remotion)
assets/                   trailer, notícias, memes, música, SFX
scripts/                  build_edl.py, gerar_projeto.py, mix.py
edicao/                   projetos .ecproj (EffectCraft) e .fcproj (FilmCraft)
render/                   partes renderizadas e o vídeo FINAL
publicacao/               thumb, DESCRICAO_YOUTUBE.md, corte do TikTok
```

**Regra para agentes:** ao parar, escreva no `ESTADO_ATUAL.md` o que ficou pronto, os arquivos que saíram e o próximo passo. Quem pegar o trabalho depois começa por ele.

## O que está em `ferramentas/` e `modelos/`

```
ferramentas/
  navegador/   cdp_aba.py (fala com uma aba do navegador via CDP), chatgpt_web.py, gemini_web.py
  postar/      br.py + os .js para YouTube Studio, TikTok Studio, Instagram e DarkPlanner; story.py
  flow/        flow.py, flow_gen.py, flow_up.py, flow_frame.py, flow_baixar2.py (Google Flow pelo navegador)
  comfyui/     comfy_look.py, comfy_flux3.py, comfy_moss.py (imagem), gerar_musica_ace.py (música)
  voz/         VoxCPM2 / Qwen3 / Chatterbox, cortar_darkplanner.py, escolher.py e montar_outro.py (melhor take)
  audio/       transcrever.py (whisper), alinhar_palavras.py (alinhamento forçado), legendas_curtas.py
  edicao/      build_edl.py, gerar_projeto.py, mix.py, monta_narracao_v2.py, confere_enquadramento.py,
               render_coop.sh / render_parte.sh, print_noticia.py, gera_mapa_svg.py
modelos/
  roteiro/          exemplos de roteiro (vídeos 02 e 03), BRIEF_ROTEIRO/REVISAO/MOTION, texto para gravar a voz
  motion-remotion/  projeto Remotion do vídeo 02 (src/ com Barras, Fuso, Dinheiro, Split, Crime...)
```

## Máquina de referência

RTX 3060 Ti (8 GB) e 16 GB de RAM, Windows 11. Python 3.11, Node 20, ffmpeg no PATH. Com uma máquina mais fraca, use modelos menores e nunca rode duas cargas de GPU juntas: picos de GPU já desligaram o PC por falta de energia.

## Economizar tokens

Tarefas longas e bem definidas (roteiro, revisão, componentes de motion, plano de cenas) podem ir para o **Codex** com um `BRIEF_*.md`:

```
codex exec --skip-git-repo-check -s workspace-write -C <pasta_do_video> "Leia BRIEF_ROTEIRO.md e faça a tarefa" < /dev/null
```

O sandbox do Codex não abre o Chrome nem o esbuild. Por isso o bundle e o render do Remotion ficam com o agente principal. Revise o que o Codex entregar: ele já citou canal concorrente no roteiro e encheu o texto de ressalvas.
