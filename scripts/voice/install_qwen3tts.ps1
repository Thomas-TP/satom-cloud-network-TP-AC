# Installe Qwen3-TTS (clonage de voix local, Apache 2.0) dans un environnement isole C:\Perso\voice\venv (hors du depot).
# Paquets : PyTorch (CUDA 12.8, necessaire pour les RTX 50xx), qwen-tts (QwenLM/Qwen3-TTS), faster-whisper (transcription), soundfile.
$ErrorActionPreference = 'Stop'
$py = "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
$root = 'C:\Perso\voice'; $venv = "$root\venv"
New-Item -ItemType Directory -Force $root | Out-Null
if (-not (Test-Path "$venv\Scripts\python.exe")) { & $py -m venv $venv }
$vpy = "$venv\Scripts\python.exe"
& $vpy -m pip install --upgrade pip 2>&1 | Select-Object -Last 1
& $vpy -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128 2>&1 | Select-Object -Last 3
& $vpy -m pip install -U qwen-tts faster-whisper soundfile huggingface_hub 2>&1 | Select-Object -Last 3
& $vpy -c "import torch; print('torch', torch.__version__, '| CUDA dispo :', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')"
& $vpy -c "import qwen_tts; print('qwen_tts OK')"
