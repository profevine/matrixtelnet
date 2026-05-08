# Matrix ASCII Telnet Server 🕶️

[Português](#português) | [English](#english)

---

## Português

Inspirado no famoso `towel.blinkenlights.nl`, este projeto transmite "The Matrix" para o seu terminal a 24 FPS com cores reais (TrueColor) e o icônico efeito de Chuva Digital — tudo via Telnet, com mais de 190 mil frames em ASCII art.

### 📺 Como Assistir

#### Windows (PowerShell ou CMD)
O cliente Telnet vem desativado por padrão. Ative com uma linha:
```
Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient
```
Depois conecte:
```
telnet matrix.profevine.com.br 2772
```

#### Linux / macOS
```bash
telnet matrix.profevine.com.br 2772
```
> No Ubuntu/Debian instale com `sudo apt install telnet` se necessário.

### 🎮 Controles

| Tecla | Ação |
|-------|------|
| **Espaço** | Play / Pause |
| **L** | Avançar 10 segundos |
| **H** | Recuar 10 segundos |
| **J** | Avançar 1 minuto |
| **K** | Recuar 1 minuto |
| **Q** | Sair |

### 🖥️ Rodar você mesmo

**Requisitos:** Python 3.11+

```bash
git clone https://github.com/profevine/matrixtelnet.git
cd matrixtelnet
python3 server.py
```

**Opções disponíveis:**

| Opção | Padrão | Descrição |
|-------|--------|-----------|
| `--host` | `0.0.0.0` | Endereço de bind |
| `--port` | `2772` | Porta TCP |
| `--movie` | `frames/movie_sequence.txt` | Arquivo de frames |
| `--max-connections` | `50` | Limite de clientes simultâneos |

**Deploy no Raspberry Pi com systemd:**
```bash
bash setup_pi.sh
```

### 🎬 Converter seu próprio vídeo

```bash
pip install opencv-python numpy
python3 converter.py seu_video.mp4 frames/movie_sequence.txt 80
```

---

## English

Inspired by `towel.blinkenlights.nl`, this project streams "The Matrix" to your terminal at 24 FPS with TrueColor support and the iconic Digital Rain effect — all over a Telnet connection, with 190k+ ASCII art frames.

### 📺 How to Watch

#### Windows (PowerShell or CMD)
The Telnet client is disabled by default. Enable it with:
```
Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient
```
Then connect:
```
telnet matrix.profevine.com.br 2772
```

#### Linux / macOS
```bash
telnet matrix.profevine.com.br 2772
```
> Install with `sudo apt install telnet` on Ubuntu/Debian if needed.

### 🎮 Controls

| Key | Action |
|-----|--------|
| **Space** | Play / Pause |
| **L** | Fast-forward 10 seconds |
| **H** | Rewind 10 seconds |
| **J** | Fast-forward 1 minute |
| **K** | Rewind 1 minute |
| **Q** | Quit |

### 🖥️ Self-hosting

**Requirements:** Python 3.11+

```bash
git clone https://github.com/profevine/matrixtelnet.git
cd matrixtelnet
python3 server.py
```

**Available options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `2772` | TCP port |
| `--movie` | `frames/movie_sequence.txt` | Frames file |
| `--max-connections` | `50` | Max simultaneous clients |

**Deploy on Raspberry Pi with systemd:**
```bash
bash setup_pi.sh
```

### 🎬 Convert your own video

```bash
pip install opencv-python numpy
python3 converter.py your_video.mp4 frames/movie_sequence.txt 80
```

---

*Welcome to the desert of the real.*

---

### ⚖️ Disclaimer / Aviso Legal

**Português:**
Este projeto foi desenvolvido exclusivamente para fins de estudo e aprendizado. Não possui qualquer intuito comercial. "The Matrix" é uma marca registrada da Warner Bros. Entertainment Inc.

**English:**
This project was developed strictly for educational and learning purposes. It has no commercial intent. "The Matrix" is a registered trademark of Warner Bros. Entertainment Inc.
