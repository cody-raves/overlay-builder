# Overlay Builder

![Preview](https://i.ibb.co/r2n8YXrw/preview.png)

📥 **[Download for Windows (EXE)](https://github.com/cody-raves/overlay-builder/releases/download/windows/Overlaybuilder.exe)**  
📹 **[Quick Usage Demo](https://streamable.com/3bfn0n)** — short walkthrough showing how to use the tool from start to finish.

**Overlay Builder** is a Python + CustomTkinter desktop app that generates animated HTML/CSS overlays for streaming, video production, or live events.

You can:
- Select your **logo** and **banner text**
- Set **fade-in**, **hold**, and **fade-out** durations
- Adjust **slide-in distances** for text and logo
- Choose an **accent color** for the underline and logo outline
- Export a ready-to-use **HTML project** (with `assets/`)

> **Note:** There is **no in-app preview**. After generating, open the output `overlay.html` in a browser (or add it as a Browser Source in OBS).

---

## ✨ Features
- Auto-sizing banner that fits your text
- Staggered text-first, logo-second slide-in animations
- Animated accent underline behind the text
- Mask-based logo **outline** that reveals and hides vertically (top→bottom in, top→bottom out)
- Looping animation timeline

---

## 📁 Output Structure
```plaintext
<your-output-folder>/
  overlay.html
  assets/
    logo.png

