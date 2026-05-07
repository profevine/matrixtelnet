# Matrix ASCII Telnet Server 🕶️

[Português](#português) | [English](#english)

---

## Português

Inspirado no famoso `towel.blinkenlights.nl`, este projeto traz a experiência de "The Matrix" para o seu terminal. Transmissão do filme em alta velocidade (24 FPS) com cores reais (TrueColor) e o icônico efeito de "Chuva Digital" — tudo através de uma conexão Telnet e todos os os mais de 190k frames do filme em código ascii.

### 📺 Como Assistir

#### 1. No Windows (PowerShell ou CMD)
O Windows não vem com o cliente Telnet ativo por padrão. Para ativar e assistir:
1. Abra o **PowerShell como Administrador** e rode: 
   `Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient`
2. Após ativar, abra qualquer terminal e digite:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

#### 2. No Linux / macOS
1. Abra o seu terminal favorito.
2. Certifique-se de que o `telnet` está instalado (`sudo apt install telnet` no Ubuntu).
3. Conecte-se:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

### 🎮 Controles de Reprodução
Comande a Matrix usando o seu teclado em tempo real:
- **[Espaço]**: Play / Pause
- **[L]**: Avançar 10 segundos
- **[H]**: Recuar 10 segundos
- **[J]**: Avançar 1 minuto
- **[K]**: Recuar 1 minuto
- **[Q]**: Sair

---

## English

Inspired by `towel.blinkenlights.nl`, this project streams "The Matrix" experience to your terminal. It features the movie in high-speed (24 FPS) with TrueColor support and the iconic "Digital Rain" effect over a Telnet connection.

### 📺 How to Watch

#### 1. On Windows (PowerShell or CMD)
The Telnet client is disabled by default. To enable and watch:
1. Open **PowerShell as Administrator** and run:
   `Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient`
2. Once enabled, open a terminal and type:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

#### 2. On Linux / macOS
1. Open your favorite terminal.
2. Ensure `telnet` is installed (`sudo apt install telnet` on Debian/Ubuntu).
3. Connect:
   ```bash
   telnet matrix.profevine.com.br 2772
   ```

### 🎮 Playback Controls
Control the Matrix using your keyboard in real-time:
- **[Space]**: Play / Pause
- **[L]**: Fast-forward 10 seconds
- **[H]**: Rewind 10 seconds
- **[J]**: Fast-forward 1 minute
- **[K]**: Rewind 1 minute
- **[Q]**: Quit

---
*Welcome to the desert of the real.*
---

### ⚖️ Disclaimer / Aviso Legal

**Português:**
Este projeto foi desenvolvido exclusivamente para fins de estudo e aprendizado. Não possui qualquer intuito comercial. "The Matrix" é uma marca registrada da Warner Bros. Entertainment Inc.

**English:**
This project was developed strictly for educational and learning purposes. It has no commercial intent. "The Matrix" is a registered trademark of Warner Bros. Entertainment Inc.

---
