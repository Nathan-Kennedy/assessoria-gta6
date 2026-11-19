# 3. Imagens e vídeos de IA

Use IA para o que o trailer não mostra: cenas de "e se...", personagens antigos (CJ, Tommy) em Leonida, fundos e ilustrações. A base do vídeo continua sendo material real: trailers oficiais em trechos curtos com comentário, notícias e mapas.

## Fontes que não são IA (use primeiro)

- **Trailers oficiais da Rockstar**: trechos curtos, sempre com narração por cima (uso transformativo). Faça um catálogo de cenas por segundo (`CATALOGO_CENAS.md`) para achar rápido o plano certo.
- **Notícia real**: `ferramentas/edicao/print_noticia.py URL "trecho" saida.png` tira o print da matéria (Edge headless, sem cookies e anúncios) com o trecho grifado em amarelo.
- **Mixkit**: vídeo, música e SFX grátis para o YouTube.
- **Wikimedia Commons**: domínio público ou CC0. Para CC BY, dê crédito na descrição.
- **Memes curtos** (vine boom, Ratinho etc.): pelo menos 1 por vídeo, sempre numa `[PAUSA MEME]`, nunca por cima da fala.

## A) ComfyUI local (nossa config)

Usamos o **ComfyUI Desktop**, com a API em `http://127.0.0.1:8188`. Os scripts mandam o workflow pronto por HTTP (`/prompt`), esperam em `/history/<id>` e copiam a saída. Não é preciso montar nós na interface.

Modelos que usamos (todos em `ComfyUI-Shared/models/`; lista completa em `ferramentas/comfyui/MODELOS.md`):

| Uso | Script | Modelo | VRAM / observação |
|-----|--------|--------|-------------------|
| Editar ou compor imagem com até 4 referências | `comfy_flux3.py saida.png prompt.txt img1 [img2..4] --w 960 --h 1200 --passos 16` | FLUX 3 Klein int8 + Qwen3-VL 4B | licença FLUX Kommunity: não use a saída para treinar outra IA |
| Editar imagem (licença livre) | `comfy_moss.py saida.png prompt.txt img1 [..] --ref-mp 0.5` | MOSS-Image SFT int8 + LoRA de edição | Apache-2.0. Com `--ref-mp 1.0` e 3 referências estoura 8 GB |
| Edição rápida com pessoa/objeto de referência | `comfy_look.py saida.png prompt.txt base.png ref.png` | Qwen-Image-Edit 2511 GGUF Q3/Q4 + Lightning 4 passos | `--lora nenhuma` dá qualidade máxima, porém mais lento |
| Música instrumental de fundo | `gerar_musica_ace.py saida.flac segundos bpm "tom" seed "tags"` | ACE-Step 1.5 Turbo | Apache-2.0, uso comercial ok |
| Foto realista simples | interface do ComfyUI | RealVisXL V5 | SDXL |
| Ampliar | interface | 4x-UltraSharp / RealESRGAN x2 | |
| Recortar fundo | interface | BiRefNet | ou `rembg` (isnet) no Python |

Proteções que já estão nos scripts (`comfy_look.py` exporta para os outros):

- param se a memória livre (commit) cair abaixo de 6 GB ou se a GPU passar de 85 °C;
- tempo máximo de 40 min por imagem.

Não rode o ComfyUI junto com voz, whisper ou render. Uma imagem por vez.

Música: para synthwave de fundo, ACE com `tags` tipo `"synthwave, retro 80s, driving bass, neon, instrumental"`, 100–110 bpm. Se não ficar bom, use Mixkit. Suno grátis **não** pode ser usado comercialmente.

## B) Google Flow (Veo para vídeo, Nano Banana para imagem)

Conta PRO logada em `flow.google.com` no navegador. Tudo pelo CDP (veja como abrir o navegador com a porta 9333 em `06_THUMB_E_POSTAGEM.md`). Scripts em `ferramentas/flow/`:

1. Abra um projeto no Flow numa aba do navegador com a porta 9333.
2. Se quiser animar uma imagem (imagem → vídeo): `python flow_frame.py imagem.png` coloca a imagem como primeiro quadro.
3. `python flow_gen.py prompt.txt saida.mp4`: digita o prompt, clica em gerar, espera até 10 min e baixa. Se o Flow recusar por política, o aviso aparece no terminal.
4. Para baixar vários vídeos da galeria: `python flow_baixar2.py <pasta> nome0.mp4 nome1.mp4 ...` (vai do mais novo para o mais antigo).
5. `flow_up.py` tem a função `enviar_arquivo`, que intercepta o seletor de arquivos do navegador e serve para qualquer upload.

Dicas de prompt (Veo):
- Descreva câmera e movimento: "low angle tracking shot, slow push-in, golden hour, Miami-like beach, GTA style".
- Para personagem antigo em low-poly dentro do GTA 6, gere primeiro a imagem (Nano Banana ou ComfyUI) e depois anime com ela como primeiro quadro.
- Planos de 5 a 8 s. Use como inserto curto, não como base do vídeo.

## C) ChatGPT (GPT Image) e Gemini pelo navegador

`ferramentas/navegador/chatgpt_web.py saida.png prompt.txt [anexos...]` abre um chat novo por imagem e baixa o resultado. Gere **um estilo por vez**: em paralelo, o ChatGPT puxou o estilo da primeira conversa para as outras.

## Cuidados

- Nada de IA imitando uma pessoa real ou uma notícia falsa.
- A imagem de IA não pode parecer material oficial da Rockstar. Se der margem para confusão, coloque "conceito" ou "ilustração" no canto.
