# 5. Montagem e render final

Fluxo: **EDL (lista de cortes) gerada por script → montagem no EffectCraft → render final no FilmCraft.**

- **EffectCraft** (compositor estilo After Effects): monta o corpo do vídeo com cenas, legendas 2.5D, cards 3D, pins, notícias e motions.
- **FilmCraft** (editor de timeline estilo Premiere): junta as partes, o áudio mixado, os memes e as correções finais, e **exporta o vídeo final**.
- **Remotion** (etapa 4): só os motions, que entram como `.mov` ou `.mp4`.

## Instalação (Windows)

- EffectCraft 0.16 e FilmCraft 0.14 portáteis em `C:\deps\effectcraft\` e `C:\deps\filmcraft\`.
- **Abra o FilmCraft sempre pelo `C:\deps\filmcraft\abrir_filmcraft.cmd`.** Ele tira o VOICEVOX do PATH, porque o `dxcompiler.dll` dele derruba o app (erro 0xc000001d).
- Fontes do canal: Anton, Bebas Neue e Montserrat, instaladas no usuário. No EffectCraft, rode `list_fonts` com rescan depois de instalar.
- ffmpeg no PATH.

## Passo a passo

### 1. Plano de cenas
`scripts/plano.json`: para cada fala, a cena (trecho do trailer, notícia, motion, mapa, IA), os cards e os pins. Use uma lista **CUES (frase → plano)**: quando a fala cita o letreiro VICE, o letreiro aparece na tela. Dividir o tempo da fala em partes iguais não funciona.

### 2. EDL
`ferramentas/edicao/build_edl.py` lê `falas.json`, `palavras.json` e o plano e gera `edl.json` com clipes, legendas, cards (pelo menos 10 s entre um e outro), pins, whips, flashes e o mistério. Também escreve `motion/src/tempos.json`.
- Ele usa as frases como âncoras. Quando a narração é re-transcrita, o texto muda um pouco: use alternativas `"a|b"` (as exatas primeiro), barre inserções maiores que 15 s e **confira os quadros antes de renderizar**. Uma âncora errada já deixou uma notícia na tela por 4 minutos.
- Não acelere um clipe acima de 160% (fica slow-mo ou fast-mo feio): o script coloca um filler.

### 3. Projeto do EffectCraft
- O `.ecproj` é JSON. `ferramentas/edicao/gerar_projeto.py` clona camadas-modelo (legenda, card, pin...) a partir do `edl.json`. É bem mais rápido do que mandar milhares de comandos.
- Antes, importe os assets no EffectCraft e salve (`importa.py`).
- Rode `confere_enquadramento.py`: a âncora tem que ser o centro real da mídia e a escala tem que cobrir 1920×1080, senão aparecem faixas pretas em mídia 2560×1440 ou em foto.
- Legendas: uma camada só, com expressão em `text/sourceText` (arrays de tempo), em vez de 50 camadas.
- Pelo MCP do EffectCraft, `run_script` fica bloqueado. Use `command_run`, `command_batch`, `set_property` e `add_keyframe`. Só dá para salvar e renderizar dentro de `C:\Projetos Dev`.

### 4. Render das partes (EffectCraft CLI)
Render longo (mais de ~6 mil quadros) acumula memória e o sistema mata o processo. Renderize em **partes de ~2 a 3 min**:
```
effectcraft-cli render --project edicao/video.ecproj --comp VIDEO --start 0 --end 125 --out render/parte1.mp4 --format h264 --bitrate 16000 --audio off
```
- `render_coop.sh` faz isso com trava (nunca duas cópias na mesma parte) e pode dividir o trabalho com uma segunda máquina: uma vai da parte 1 para a frente, a outra da última para trás. `manifesto_render.py <ecproj> <comp>` lista os arquivos que a outra máquina precisa.
- Antes de relançar um render que caiu, veja se o processo antigo ainda está vivo (`Get-CimInstance Win32_Process -Filter "Name='effectcraft-cli.exe'"`). Duas cópias = memória estourada e arquivo corrompido.
- Velocidade: ~4× o tempo real em 1080p30 na CPU.

### 5. Áudio
`ferramentas/edicao/mix.py`: narração + synthwave contínua por baixo (crossfade entre faixas, ducking sob a voz) + SFX suaves + memes nas `[PAUSA MEME]`. No fim, `loudnorm` em **−14 LUFS**.
- SFX: whooshes graves e baixos (`air woosh`, `sweep`). O "fast whoosh" agudo foi reprovado.
- O som do meme nunca fica por cima da fala.

### 6. Render final no FilmCraft
1. Abra o FilmCraft (`abrir_filmcraft.cmd`) e crie a sequência 1920×1080, 30 fps.
2. Importe as partes, na ordem, para V1, e o `mix.wav` para A1. Por linha de comando: `filmcraft-cli --project video.fcproj import render/parte*.mp4 render/mix.wav`.
3. Ajustes finais na timeline: memes, cortes de respiração e a abertura (gancho) na frente.
4. Confira um quadro: `filmcraft-cli --project video.fcproj render --seconds 120 --out check.png`.
5. Exporte:
   ```
   filmcraft-cli --project edicao/video.fcproj export render/GTA6_videoNN_FINAL.mp4 --format h264 --quality 90
   ```
   Se o app estiver aberto, pilote ao vivo: ele sobe com `--control 9876` e a variável `FILMCRAFT_CONTROL_TOKEN`; o cliente precisa do mesmo token. Comandos num arquivo `.jsonl` em UTF-8 (`filmcraft-cli --bridge 127.0.0.1:9876 run cmds.jsonl`), porque no PowerShell 5.1 as aspas quebram. `filmcraft-cli commands` lista tudo (`file.exportMedia`, `captions.import`...).
   - O export sai com código 1 se tiver mídia offline. Corrija o caminho em vez de usar `--allow-offline`.
6. Atalho sem o FilmCraft: `ffmpeg -f concat` das partes + `mix.wav` (fim do `render_coop.sh`). Use só para prévia rápida.

## Antes de dar como pronto

- [ ] Assistir o gancho inteiro e pular por 10 pontos do vídeo
- [ ] Nenhuma faixa preta, nenhum texto cortado, nenhuma legenda adiantada
- [ ] Toda notícia e todo número com a fonte na tela
- [ ] Áudio em −14 LUFS, sem pico estourado, e meme fora da fala
- [ ] Atualizar o `ESTADO_ATUAL.md`
