# 2. Voz

Há três caminhos, e todos terminam no mesmo formato: **um áudio por fala** (`linha_XX.wav`), mais `falas.json` (início e fim de cada fala) e `palavras.json` (tempo de cada palavra). A montagem, as legendas e os motions dependem desses tempos.

## A) A nossa própria voz (o preferido)

O público gosta de voz humana, e o canal não usa selo de IA.

1. Grave seguindo o `ROTEIRO_PARA_NARRAR.txt`, **um arquivo por bloco**. Celular ou microfone a um palmo da boca, em lugar silencioso.
2. Errou? Não recomece o bloco: espere 2 s em silêncio e repita só a frase. O script fica com a **última** tentativa.
3. Pode mandar por WhatsApp (o vídeo 02 foi narrado assim, por blocos, e a edição começou antes de chegar tudo).
4. Monte a narração:
   - `ferramentas/audio/transcrever.py`: faster-whisper (medium, int8). Use `condition_on_previous_text=False` + VAD para não alucinar.
   - `ferramentas/audio/alinhar_palavras.py`: alinhamento forçado (MMS_FA). O whisper marca o início da palavra cedo demais, e a legenda apareceria antes da fala. Use os tempos do alinhador quando concordarem com o whisper (±0,6 s).
   - `ferramentas/edicao/monta_narracao_v2.py`: corta e junta. **Nunca corte pelo tempo do whisper**: corte só em silêncio real (RMS abaixo de p95 −32 dB por pelo menos 70 ms).
5. Procure repetições na narração montada (n-gramas repetidos na transcrição). O whisper "junta" tentativas repetidas, e elas passam despercebidas.
6. Improviso bom fica. Comentário ("pera, de novo") sai.

## B) Voz clonada no PC (VoxCPM2)

Serve para narração-guia, para corrigir uma palavra errada na gravação real, para vinheta ou para o CTA.

- Modelo: **VoxCPM2** (licença Apache, 48 kHz). Precisa de ~6 GB de VRAM e roda ~1,8× mais devagar que o tempo real. Scripts em `ferramentas/voz/`:
  - `gerar_voxcpm.py roteiro.txt ref_16k.wav ref.txt saida.wav`: clona a voz da referência;
  - `gerar_linhas_voxcpm.py`: uma fala por arquivo;
  - `gerar_voxcpm_design.py`: cria uma voz nova a partir de uma descrição ("(narrador jovem brasileiro, animado)texto") e depois a clona no roteiro todo.
- **Receita aprovada (ficou natural):**
  1. A referência é um trecho de **conversa** de 10 a 15 s, não de narração lida. Pegue de um vídeo já gravado, converta para 16 kHz mono e escreva o texto exato no `.txt`.
  2. Gere **3 takes por fala** (rode 3 vezes em pastas `_a`, `_b`, `_c`).
  3. `escolher.py`: dá nota a cada take pela semelhança no whisper e penaliza take que começa ou termina cortado.
  4. `montar_outro.py`: corte suave, com trim só abaixo de −50 dB, 80 ms de folga e fade de 12 ms. O trim em −38 dB comia o começo e o fim das palavras.
- Para trocar uma palavra na gravação real, use a palavra da voz clonada com o volume igualado, e confira com o whisper no contexto. Recortar a mesma palavra de outro trecho da pessoa soou errado.
- Alternativas instaladas: Qwen3-TTS (`gerar_qwen.py`; use language "Auto", porque "Portuguese" sai com sotaque de Portugal) e Chatterbox (`gerar_chatterbox.py` + `pronuncia_ptbr.py` para nomes em inglês).
- **Só clone a voz de quem autorizou.** As referências de voz não vão para o repositório.

## C) DarkPlanner (site pago, ~R$ 50/mês)

O jeito mais rápido quando ninguém pode gravar. Gera a narração inteira com uma voz da biblioteca ou com a sua voz clonada lá.

1. Para clonar a sua voz no DarkPlanner, grave o texto de `modelos/roteiro/TEXTO_PARA_GRAVAR_darkplanner.txt` (~1 min, com entusiasmo de verdade) e envie na área de clonagem do site.
2. Cole o roteiro **só com as falas** (sem números, marcações nem linhas de ANIMAÇÃO), uma fala por parágrafo. Isso também dá para fazer pelo navegador (ver `06_THUMB_E_POSTAGEM.md`, seção CDP): `dpfill.js` preenche o texto, `dpb.js`/`dpc.js` buscam a voz na biblioteca, `dpgen.js` clica em "Gerar Áudio" e `dpaud.js` acha o link do mp3.
3. Baixe o **mp3** e a legenda **SRT sincronizada por palavra**.
4. `ferramentas/voz/cortar_darkplanner.py`: corta o mp3 em uma fala por linha usando o SRT por palavra. Gera `linhas/linha_XX.wav` + `linhas.json`. Os nomes dos arquivos de entrada estão no fim do script; ajuste para os seus.
5. Para corrigir falas, gere só as falas erradas no DarkPlanner (`correcoes_ids.txt` com os números) e rode o script de novo: ele substitui só essas.

## Depois da voz

- Normalize em −14 LUFS no fim da mixagem (`loudnorm`), não em cada fala.
- Alvo de ritmo: 170 a 200 palavras por minuto.
- Não rode a voz (VoxCPM) junto com o whisper ou com o ComfyUI: 8 GB de VRAM lotam e tudo trava.
