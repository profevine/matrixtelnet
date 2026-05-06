# Matrix ASCII Telnet Server 🕶️

[Português](#português) | [English](#english)

---

## Português

Inspirado no famoso `towel.blinkenlights.nl`, este projeto traz a experiência de "The Matrix" para o seu terminal. Ele transmite uma versão ASCII da história do filme, seguida por sequências de vídeo em alta velocidade (24 FPS) e termina com o icônico efeito de "Chuva Digital" — tudo através de uma conexão TCP (Telnet).

### ✨ Funcionalidades
- **Modo História:** Cenas clássicas em ASCII art estilizado.
- **Reprodução de Vídeo:** Suporte para sequências de vídeo em 24 FPS com cores reais (TrueColor).
- **Chuva Digital Infinita:** O efeito clássico de código caindo.
- **Controles Interativos:** Play, Pause e saltos no tempo via teclado.
- **Conversor Integrado:** Ferramenta para transformar qualquer `.mp4` em arte ASCII colorida.

### 📺 Como Assistir

#### No Windows (PowerShell ou CMD)
1. O Windows não vem com o cliente Telnet ativo por padrão. Para ativar:
   - Abra o PowerShell como Administrador e rode: `Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient`
2. Após ativar, abra um terminal e digite:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

#### No Linux / macOS
1. Abra o seu terminal favorito.
2. Certifique-se de que o `telnet` está instalado (`sudo apt install telnet` no Ubuntu).
3. Conecte-se:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

### 🎮 Controles de Reprodução
- **[Espaço]**: Play / Pause
- **[L]**: Avançar 10 segundos
- **[H]**: Recuar 10 segundos
- **[J]**: Avançar 1 minuto
- **[K]**: Recuar 1 minuto
- **[Q]**: Sair

---

## English

Inspired by `towel.blinkenlights.nl`, this project streams "The Matrix" experience to your terminal. It features an ASCII story mode, high-speed video sequences (24 FPS) with TrueColor support, and the iconic infinite "Digital Rain" effect over a Telnet connection.

### ✨ Features
- **Story Mode:** Classic scenes in stylized ASCII art.
- **Video Playback:** High-fidelity 24 FPS video sequences with original colors.
- **Infinite Matrix Rain:** The classic falling code effect.
- **Interactive Controls:** Play, Pause, and Seeking via keyboard.
- **Video-to-ASCII Converter:** Transform any `.mp4` into vibrant ASCII art.

### 📺 How to Watch

#### On Windows (PowerShell or CMD)
1. The Telnet client is disabled by default. To enable it:
   - Open PowerShell as Administrator and run: `Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient`
2. Once enabled, open a terminal and type:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

#### On Linux / macOS
1. Open your favorite terminal.
2. Ensure `telnet` is installed (`sudo apt install telnet` on Debian/Ubuntu).
3. Connect:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

### 🎮 Playback Controls
- **[Space]**: Play / Pause
- **[L]**: Fast-forward 10 seconds
- **[H]**: Rewind 10 seconds
- **[J]**: Fast-forward 1 minute
- **[K]**: Rewind 1 minute
- **[Q]**: Quit

---

## 🛠️ Setup & Deployment (Admin Only)

### Local Conversion
To convert a new video:
```bash
python3 converter.py input.mp4 frames/movie_sequence.txt 80
```

### Raspberry Pi Service
```bash
chmod +x setup_pi.sh
./setup_pi.sh
```

*Welcome to the desert of the real.*
