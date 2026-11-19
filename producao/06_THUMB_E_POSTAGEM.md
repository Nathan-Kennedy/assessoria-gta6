# 6. Thumbnail e postagem (YouTube, TikTok e Instagram)

O agente pode postar sozinho, controlando o navegador em que as contas já estão logadas pela **porta de depuração remota (CDP)**. Não precisa de API, extensão nem senha: ele usa a sessão do navegador.

## Abrir o navegador com a porta 9333

Usamos o Opera GX, mas Chrome ou Edge funcionam igual.

1. **Feche o navegador por completo**, inclusive na bandeja. Se ele já estiver aberto, a flag é ignorada.
2. Abra com a porta:
   ```powershell
   & "$env:LOCALAPPDATA\Programs\Opera GX\opera.exe" --remote-debugging-port=9333
   # Chrome: & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9333 --user-data-dir="$env:LOCALAPPDATA\Google\Chrome\User Data"
   ```
3. Teste: `curl http://127.0.0.1:9333/json/list` lista as abas.
4. Use a 9333. A 9222 costuma estar ocupada por outros programas.

Por segurança, a porta só escuta em `127.0.0.1`. Não exponha na rede: quem acessa a porta controla todas as contas logadas.

## Como os scripts falam com a aba

- `ferramentas/navegador/cdp_aba.py`: `abas("dominio")` lista as abas com aquele endereço, e `Aba(t).cmd(metodo, **params)` / `.js(codigo)` mandam comandos CDP. Precisa de `pip install websockets`.
- `ferramentas/postar/br.py`: o "controle remoto". Escolha a aba pela variável `ABA` (um pedaço da URL):

```
ABA=studio.youtube.com python br.py shot tela.png          # print da aba (sempre olhe antes de clicar)
ABA=studio.youtube.com python br.py js ftit.js             # roda um .js na página
ABA=studio.youtube.com python br.py type ftit.js titulo.txt   # foca o campo do .js e digita o texto do arquivo
ABA=studio.youtube.com python br.py file "input[type=file]" C:\...\video.mp4   # envia um arquivo
ABA=studio.youtube.com python br.py click 812 440          # clique real (Input.dispatchMouseEvent)
ABA=studio.youtube.com python br.py tags tags.txt          # tags separadas por vírgula, uma a uma com Enter
ABA=... python br.py enter | nav <url> | fullshot
```

Princípios:
- **Print antes e depois de cada passo.** A interface muda, então confira na imagem em vez de confiar no seletor.
- Upload: `DOM.setFileInputFiles` no `input[type=file]`. Quando o site abre o seletor do Windows, intercepte com `Page.setInterceptFileChooserDialog` (exemplo em `ferramentas/flow/flow_up.py`).
- Dropdown e menu: clique real com coordenadas (`click x y`). O `.click()` em JavaScript muitas vezes não abre.
- Texto em campo `contenteditable`: foque o campo e use `Input.insertText` (o `type` do br.py).
- Se a aba travar num diálogo "sair da página?", feche-a com `http://127.0.0.1:9333/json/close/<id>` e abra outra com `/json/new?<url>`.

## Thumbnail

Ganha clique (dados do Niche Finder):
- **Comparação lado a lado jogo × vida real** (4× mais que a média dos canais BR). Cena clara, ângulos parecidos, "GTA 6" / "VIDA REAL", "VS" no meio, pouco texto e logo pequena num canto.
- Mapa também funciona. Thumb escura (cena noturna) foi mal.
- Personagem (Lucia) só em vídeo de história ou personagem, não em comparação de lugar. Na dúvida, use o **Teste A/B do YouTube Studio** em vez de opinião.
- 1280×720, JPG < 2 MB. Monte por script (Pillow), com o recorte do personagem via `rembg` (isnet) e a logo oficial com alfa por luminância.
- O canal precisa estar **verificado por telefone** para aceitar thumbnail personalizada. O dono do canal faz isso (código por SMS).

## YouTube (Studio)

⚠️ **Confira o canal.** A conta Google pode ter mais de um canal, e um vídeo já foi publicado no canal pessoal por engano. Navegue direto para o Studio do canal certo: `https://studio.youtube.com/channel/<ID_DO_CANAL>/videos/upload?d=ud`. Na tela deve aparecer o nome do canal certo antes de enviar.

1. `br.py file 'input[type=file]' video.mp4`
2. Título: `br.py type ftit.js titulo.txt`. Descrição: `br.py type fdesc.js desc.txt` (com capítulos 0:00, fontes e créditos).
3. Thumb: `br.py file 'input[accept*=image]' thumb.jpg` (use `th2.js`/`thq.js` para conferir).
4. `aud.js`: "não é conteúdo para crianças". `rad.js`: opções do formulário. `lang.js`: idioma.
5. "Mostrar mais" → tags: `br.py tags tags.txt`.
6. Tela final: "Adicionar" → modelo "1 vídeo, 1 botão de inscrição".
7. `nx.js` 3 vezes (Avançar). **Espere "Verificações concluídas"** (`ytchk.js`): por causa dos trailers, a checagem de direitos autorais precisa terminar.
8. Visibilidade: publicar agora (`pub.js`) ou programar, com fuso **(GMT-03:00) São Paulo**, porque o público é de Brasília. Depois `done.js`, e `lnk.js` pega o link.
9. Horários bons para o nicho: final da manhã ou início da noite (Brasília). Veja em Analytics → Público → "quando seus espectadores estão no YouTube".

## TikTok (TikTok Studio web)

1. Corte vertical 1080×1920 de 30 a 60 s (o gancho do vídeo costuma funcionar sozinho), com chamada final para o canal.
2. Aba `tiktok.com/tiktokstudio/upload`: `ABA=tiktokstudio python br.py file 'input[type=file]' corte.mp4`.
3. Legenda: `tk12.js` seleciona o campo, e `type` digita a legenda com hashtags.
4. **A privacidade padrão veio "Somente eu".** Troque para **Todos** antes de publicar, ou depois, na lista de Conteúdo.
5. `tkpub.js` publica. O agendamento usa o fuso do PC.
6. A web do TikTok bloqueia a leitura de perfis ("Algo deu errado"). Para pesquisar, use a busca de vídeos.

## Instagram (web)

- **Reels e posts:** "+" (Criar) → `br.py file 'input[type=file]' arquivo 2` (o input de índice 2) → recorte (Original ou 4:5) → `ig8.js` 2 vezes (Avançar) → `ig13.js` + `type legenda.txt` → `ig11.js` (Compartilhar).
- **Stories:** `ferramentas/postar/story.py <imagem> <prefixo>` simula um iPhone (a web só deixa postar story no modo celular). Precisa de `screenOrientation` em retrato, senão aparece "Gire seu dispositivo". Pela web não dá para pôr adesivo de link.
- O que dá resultado no nicho: contagem regressiva (1,8× a média), comparação em carrossel e reels. Meme isolado rende menos.

## Depois de postar

- Guardar o link no `ESTADO_ATUAL.md` do vídeo.
- Postar o corte do TikTok ~30 min depois do YouTube e o story com a thumb.
- Responder os primeiros comentários na primeira hora.
