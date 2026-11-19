#!/bin/bash
# Uso: bash scripts/render_parte.sh 74-128  -> renderiza a comp VIDEO02_74_128 em pedacos de 150 s, junta e faz o mux.
set -e
P="$1"; COMP="VIDEO02_${P//-/_}"
cd "C:/Projetos Dev/Videos/2026-11-17_video02-primeiro-dia-gta6"
if powershell -NoProfile -c "Get-CimInstance Win32_Process -Filter \"Name='effectcraft-cli.exe'\" | ? { \$_.CommandLine -match ' render ' } | select -First 1" | grep -q .; then
  echo "JÁ TEM UM RENDER RODANDO: saindo sem fazer nada"; exit 1
fi
CLI="/c/deps/effectcraft/0.16.0/effectcraft-0.16.0-windows-x64-portable/effectcraft-cli.exe"
DUR=$(python -c "import json;print(json.load(open('scripts/tempos_$P.json'))['dur'])")
: > "render/${P}_lista.txt"; ini=0; n=1
while python -c "import sys; sys.exit(0 if $ini < $DUR - 1.0 else 1)"; do
  fim=$((ini+${PEDACO:-150})); out="render/${P}_parte$n.mp4"
  ENT="C:/Projetos Dev/Videos/_pacote_notebook/entrega/${P}_parte$n.mp4"
  if [ -f "render/partes_pc_${P}.txt" ] && ! grep -qx "$n" "render/partes_pc_${P}.txt"; then
    echo "parte$n fica com o notebook: esperando em entrega/"
    until [ -f "$ENT" ] && ffprobe -v error "$ENT" >/dev/null 2>&1; do sleep 30; done
    cp "$ENT" "$out"; echo "parte$n chegou do notebook"
  fi
  if [ -f "$out" ] && ffprobe -v error "$out" >/dev/null 2>&1; then echo "parte$n já existe"; else
    END=""; python -c "import sys; sys.exit(0 if $fim < $DUR else 1)" && END="--end $fim"
    for t in 1 2 3; do
      "$CLI" render --project "edicao/video02_$P.ecproj" --comp "$COMP" --start $ini $END \
        --out "$out" --format h264 --bitrate 16000 --audio off --progress 2> "render/${P}_parte${n}_progress.txt" && break
      echo "parte$n falhou (tentativa $t)"; rm -f "$out"
    done
  fi
  echo "file '${P}_parte$n.mp4'" >> "render/${P}_lista.txt"; echo "OK parte$n"
  ini=$fim; n=$((n+1))
done
ffmpeg -y -v error -f concat -safe 0 -i "render/${P}_lista.txt" -c copy "render/${P}_video.mp4"
ffmpeg -y -v error -i "render/${P}_video.mp4" -i "render/${P}_mix.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "render/GTA6_video02_falas_${P}_v2.mp4"
echo "PRONTO"; ffprobe -v error -show_entries format=duration -of csv=p=0 "render/GTA6_video02_falas_${P}_v2.mp4"
