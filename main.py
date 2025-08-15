import os
from pathlib import Path
from jinja2 import Template
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser

def render_overlay(logo_path,
                   output_dir,
                   brand_text,
                   tagline_text,
                   show_tagline,
                   in_duration,
                   sustain_duration,
                   out_duration,
                   text_in_anim,
                   logo_in_anim,
                   text_in_px,
                   logo_in_px,
                   text_out_px,
                   logo_out_px,
                   accent_color,
                   text_color,
                   muted_color,
                   brand_size_css,
                   container_max_w,
                   stroke_scale,
                   stroke_reveal_seconds,
                   stroke_hide_seconds):
    total_duration = in_duration + sustain_duration + out_duration
    p_in_end = (in_duration / total_duration) * 100.0
    p_hold_end = ((in_duration + sustain_duration) / total_duration) * 100.0
    p_text_in_end = (text_in_anim / total_duration) * 100.0
    logo_in_start_sec = text_in_anim
    logo_in_end_sec = min(in_duration, text_in_anim + logo_in_anim)
    p_logo_in_start = (logo_in_start_sec / total_duration) * 100.0
    p_logo_in_end = (logo_in_end_sec / total_duration) * 100.0
    stroke_reveal_end_sec = min(total_duration, logo_in_end_sec + stroke_reveal_seconds)
    p_stroke_reveal_start = p_logo_in_end
    p_stroke_reveal_end = (stroke_reveal_end_sec / total_duration) * 100.0
    stroke_hide_start_sec = max(0.0, in_duration + sustain_duration - stroke_hide_seconds)
    p_stroke_hide_start = (stroke_hide_start_sec / total_duration) * 100.0
    p_stroke_hide_end = p_hold_end

    html_template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <title>Overlay</title>
  <style>
    html, body { height: 100%; }
    body {
      margin: 0;
      background: transparent;
      overflow: hidden;
      font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Inter, Arial, "Noto Sans", "Helvetica Neue", sans-serif;
      color: {{ text_color }};
    }
    .stage { position: fixed; inset: 0; display: grid; place-items: center; pointer-events: none; }
    .banner {
      --brand-size: {{ brand_size_css }};
      --pad-y: calc(var(--brand-size) * 0.30);
      --pad-x: calc(var(--brand-size) * 0.55);
      --radius: calc(var(--brand-size) * 0.25);
      --logo-h: calc(var(--brand-size) * 1.0);
      --uline: max(2px, calc(var(--brand-size) * 0.05));
      position: relative;
      display: inline-grid;
      grid-auto-flow: column;
      grid-auto-columns: max-content;
      grid-template-columns: max-content max-content;
      align-items: center;
      column-gap: calc(var(--brand-size) * 0.45);
      width: max-content;
      max-width: {{ container_max_w }};
      padding: var(--pad-y) var(--pad-x);
      border-radius: var(--radius);
      background: rgba(0, 0, 0, 0.18);
      backdrop-filter: blur(2px);
      -webkit-backdrop-filter: blur(2px);
      animation: bannerCycle {{ total_duration }}s cubic-bezier(.2,.7,0,1) infinite;
      will-change: transform, opacity, filter;
    }
    .textblock { display: grid; row-gap: calc(var(--brand-size) * 0.18); animation: textCycle {{ total_duration }}s cubic-bezier(.2,.7,0,1) infinite; will-change: transform, opacity, filter; }
    .brandwrap { position: relative; display: inline-block; }
    .brand { position: relative; z-index: 1; font-weight: 700; letter-spacing: 0.02em; font-size: var(--brand-size); line-height: 1.05; }
    .underline { position: absolute; left: 0; right: 0; bottom: -0.08em; height: var(--uline); background: {{ accent_color }}; transform-origin: left center; z-index: 0; pointer-events: none; animation: underlineCycle {{ total_duration }}s cubic-bezier(.2,.7,0,1) infinite; will-change: transform, opacity; }
    .tagline { font-weight: 500; letter-spacing: 0.02em; font-size: clamp(12px, calc(var(--brand-size) * 0.42), 24px); color: {{ muted_color }}; max-width: calc(var(--brand-size) * 20); overflow-wrap: anywhere; }
    .logoWrap { position: relative; display: inline-grid; place-items: center; }
    .logoStroke {
      position: absolute; inset: 0; z-index: 0; background: {{ accent_color }}; transform: scale({{ stroke_scale }});
      -webkit-mask-image: url('assets/logo.png'); mask-image: url('assets/logo.png');
      -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat;
      -webkit-mask-position: center; mask-position: center;
      -webkit-mask-size: contain; mask-size: contain;
      pointer-events: none;
      animation: strokeCycle {{ total_duration }}s linear infinite;
    }
    .logo { position: relative; z-index: 1; height: var(--logo-h); width: auto; max-width: calc(var(--brand-size) * 6); object-fit: contain; animation: logoCycle {{ total_duration }}s cubic-bezier(.2,.7,0,1) infinite; will-change: transform, opacity, filter; }
    @keyframes bannerCycle {
      0% { transform: translate3d(0, -{{ logo_out_px }}px, 0) scale(0.985); opacity: 0; filter: blur(8px); }
      {{ p_text_in_end|round(4) }}% { transform: translate3d(0, 0, 0) scale(1); opacity: 1; filter: blur(0); }
      {{ p_hold_end|round(4) }}% { transform: translate3d(0, 0, 0) scale(1); opacity: 1; filter: blur(0); }
      100% { transform: translate3d(0, -{{ logo_out_px }}px, 0) scale(0.985); opacity: 0; filter: blur(8px); }
    }
    @keyframes textCycle {
      0% { transform: translate3d(-{{ text_in_px }}px, 0, 0); opacity: 0; filter: blur(10px); }
      {{ p_text_in_end|round(4) }}% { transform: translate3d(0, 0, 0); opacity: 1; filter: blur(0); }
      {{ p_hold_end|round(4) }}% { transform: translate3d(0, 0, 0); opacity: 1; filter: blur(0); }
      100% { transform: translate3d(0, -{{ text_out_px }}px, 0); opacity: 0; filter: blur(8px); }
    }
    @keyframes underlineCycle {
      0% { transform: scaleX(0); opacity: 0; }
      {{ p_text_in_end|round(4) }}% { transform: scaleX(1); opacity: 1; }
      {{ p_hold_end|round(4) }}% { transform: scaleX(1); opacity: 1; }
      100% { transform: scaleX(0); opacity: 0; transform-origin: right center; }
    }
    @keyframes logoCycle {
      0% { transform: translate3d({{ logo_in_px }}px, 0, 0) scale(0.985); opacity: 0; filter: blur(10px); }
      {{ p_logo_in_start|round(4) }}% { transform: translate3d({{ logo_in_px }}px, 0, 0) scale(0.985); opacity: 0; filter: blur(10px); }
      {{ p_logo_in_end|round(4) }}% { transform: translate3d(0, 0, 0) scale(1); opacity: 1; filter: blur(0); }
      {{ p_hold_end|round(4) }}% { transform: translate3d(0, 0, 0) scale(1); opacity: 1; filter: blur(0); }
      100% { transform: translate3d(0, -{{ logo_out_px }}px, 0) scale(0.985); opacity: 0; filter: blur(8px); }
    }
    @keyframes strokeCycle {
      0% { opacity: 0; clip-path: inset(100% 0 0 0); }
      {{ (p_stroke_reveal_start)|round(4) - 0.01 }}% { opacity: 0; clip-path: inset(100% 0 0 0); }
      {{ p_stroke_reveal_start|round(4) }}% { opacity: 1; clip-path: inset(100% 0 0 0); }
      {{ p_stroke_reveal_end|round(4) }}% { opacity: 1; clip-path: inset(0 0 0 0); }
      {{ (p_stroke_hide_start)|round(4) - 0.01 }}% { opacity: 1; clip-path: inset(0 0 0 0); }
      {{ p_stroke_hide_start|round(4) }}% { opacity: 1; clip-path: inset(0 0 0 0); }
      {{ p_stroke_hide_end|round(4) }}% { opacity: 0; clip-path: inset(100% 0 0 0); }
      100% { opacity: 0; clip-path: inset(100% 0 0 0); }
    }
    @media (max-width: 720px) { .banner { --brand-size: clamp(18px, 5.5vmin, 56px); } }
  </style>
</head>
<body>
  <div class="stage">
    <div class="banner" role="img" aria-label="{{ brand_text }} {{ ('— ' + tagline_text) if (tagline_text and show_tagline) else '' }}">
      <div class="textblock">
        <div class="brandwrap">
          <div class="brand">{{ brand_text }}</div>
          <div class="underline"></div>
        </div>
        {% if show_tagline and tagline_text %}
        <div class="tagline">{{ tagline_text }}</div>
        {% endif %}
      </div>
      <div class="logoWrap">
        <div class="logoStroke"></div>
        <img class="logo" src="assets/logo.png" alt="Logo">
      </div>
    </div>
  </div>
</body>
</html>
"""
    output_dir = Path(output_dir)
    assets = output_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    if not Path(logo_path).exists():
        raise FileNotFoundError(str(Path(logo_path).resolve()))
    shutil.copy(logo_path, assets / "logo.png")
    html = Template(html_template).render(
        brand_text=brand_text,
        tagline_text=tagline_text,
        show_tagline=show_tagline,
        text_color=text_color,
        muted_color=muted_color,
        accent_color=accent_color,
        container_max_w=container_max_w,
        brand_size_css=brand_size_css,
        stroke_scale=stroke_scale,
        stroke_reveal_seconds=stroke_reveal_seconds,
        stroke_hide_seconds=stroke_hide_seconds,
        total_duration=total_duration,
        p_in_end=p_in_end,
        p_hold_end=p_hold_end,
        p_text_in_end=p_text_in_end,
        p_logo_in_start=p_logo_in_start,
        p_logo_in_end=p_logo_in_end,
        p_stroke_reveal_start=p_stroke_reveal_start,
        p_stroke_reveal_end=p_stroke_reveal_end,
        p_stroke_hide_start=p_stroke_hide_start,
        p_stroke_hide_end=p_stroke_hide_end,
        text_in_px=text_in_px,
        logo_in_px=logo_in_px,
        text_out_px=text_out_px,
        logo_out_px=logo_out_px
    )
    (output_dir / "overlay.html").write_text(html, encoding="utf-8")
    return str(output_dir.resolve())

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Overlay Builder")
        self.geometry("980x660")

        self.logo_path = ctk.StringVar(value="")
        self.output_dir = ctk.StringVar(value="overlay_project_gui")
        self.brand_text = ctk.StringVar(value="cody raves")
        self.tagline_text = ctk.StringVar(value="twitch.tv/cody_raves")
        self.show_tagline = ctk.BooleanVar(value=True)

        self.in_duration = ctk.DoubleVar(value=4.0)
        self.sustain_duration = ctk.DoubleVar(value=10.0)
        self.out_duration = ctk.DoubleVar(value=4.0)

        self.text_in_anim = ctk.DoubleVar(value=1.6)
        self.logo_in_anim = ctk.DoubleVar(value=1.2)

        self.text_in_px = ctk.IntVar(value=280)
        self.logo_in_px = ctk.IntVar(value=280)
        self.text_out_px = ctk.IntVar(value=140)
        self.logo_out_px = ctk.IntVar(value=140)

        self.accent_color = ctk.StringVar(value="#00C2FF")
        self.text_color = ctk.StringVar(value="#FFFFFF")
        self.muted_color = ctk.StringVar(value="rgba(255,255,255,0.75)")

        self.brand_size_css = ctk.StringVar(value="clamp(20px, 5.2vmin, 64px)")
        self.container_max_w = ctk.StringVar(value="92vmin")

        self.stroke_scale = ctk.DoubleVar(value=1.18)
        self.stroke_reveal_seconds = ctk.DoubleVar(value=0.6)
        self.stroke_hide_seconds = ctk.DoubleVar(value=0.6)

        self.columnconfigure((0,1,2,3), weight=1, uniform="a")

        pad = {"padx":12, "pady":8}

        ctk.CTkLabel(self, text="Logo").grid(row=0, column=0, sticky="e", **pad)
        self.logo_entry = ctk.CTkEntry(self, textvariable=self.logo_path, width=520)
        self.logo_entry.grid(row=0, column=1, columnspan=2, sticky="we", **pad)
        ctk.CTkButton(self, text="Browse", command=self.pick_logo).grid(row=0, column=3, sticky="w", **pad)

        ctk.CTkLabel(self, text="Output Folder").grid(row=1, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.output_dir).grid(row=1, column=1, columnspan=2, sticky="we", **pad)
        ctk.CTkButton(self, text="Choose", command=self.pick_output).grid(row=1, column=3, sticky="w", **pad)

        ctk.CTkLabel(self, text="Brand Text").grid(row=2, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.brand_text).grid(row=2, column=1, columnspan=2, sticky="we", **pad)

        ctk.CTkLabel(self, text="Tagline").grid(row=3, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.tagline_text).grid(row=3, column=1, sticky="we", **pad)
        ctk.CTkCheckBox(self, text="Show Tagline", variable=self.show_tagline).grid(row=3, column=2, sticky="w", **pad)

        ctk.CTkLabel(self, text="Fade In (s)").grid(row=4, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.in_duration, width=120).grid(row=4, column=1, sticky="w", **pad)
        ctk.CTkLabel(self, text="Hold (s)").grid(row=4, column=1, sticky="e", padx=(220,12), pady=8)
        ctk.CTkEntry(self, textvariable=self.sustain_duration, width=120).grid(row=4, column=1, sticky="e", padx=(0,12), pady=8)
        ctk.CTkLabel(self, text="Fade Out (s)").grid(row=4, column=2, sticky="w", **pad)
        ctk.CTkEntry(self, textvariable=self.out_duration, width=120).grid(row=4, column=2, sticky="e", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Text In Anim (s)").grid(row=5, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.text_in_anim, width=120).grid(row=5, column=1, sticky="w", **pad)
        ctk.CTkLabel(self, text="Logo In Anim (s)").grid(row=5, column=2, sticky="w", **pad)
        ctk.CTkEntry(self, textvariable=self.logo_in_anim, width=120).grid(row=5, column=2, sticky="e", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Accent Color (Outline/Underline)").grid(row=6, column=0, sticky="e", **pad)
        self.accent_entry = ctk.CTkEntry(self, textvariable=self.accent_color)
        self.accent_entry.grid(row=6, column=1, sticky="we", **pad)
        ctk.CTkButton(self, text="Pick", command=self.pick_accent_color).grid(row=6, column=2, sticky="w", **pad)

        ctk.CTkLabel(self, text="Text Color").grid(row=6, column=2, sticky="e", padx=(220,12), pady=8)
        ctk.CTkEntry(self, textvariable=self.text_color, width=140).grid(row=6, column=3, sticky="we", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Muted Color").grid(row=7, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.muted_color).grid(row=7, column=1, sticky="we", **pad)

        ctk.CTkLabel(self, text="Stroke Scale").grid(row=7, column=2, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.stroke_scale, width=120).grid(row=7, column=3, sticky="we", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Stroke Reveal (s)").grid(row=8, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.stroke_reveal_seconds, width=120).grid(row=8, column=1, sticky="w", **pad)
        ctk.CTkLabel(self, text="Stroke Hide (s)").grid(row=8, column=2, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.stroke_hide_seconds, width=120).grid(row=8, column=3, sticky="we", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Brand Size CSS").grid(row=9, column=0, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.brand_size_css).grid(row=9, column=1, sticky="we", **pad)

        ctk.CTkLabel(self, text="Container Max Width").grid(row=9, column=2, sticky="e", **pad)
        ctk.CTkEntry(self, textvariable=self.container_max_w, width=160).grid(row=9, column=3, sticky="we", padx=(0,24), pady=8)

        ctk.CTkLabel(self, text="Slide Distances (px) — TextIn, LogoIn, TextOut, LogoOut").grid(row=10, column=0, columnspan=4, sticky="w", padx=12, pady=(14,6))
        f = ctk.CTkFrame(self)
        f.grid(row=11, column=0, columnspan=4, sticky="we", padx=12, pady=(0,12))
        f.columnconfigure((0,1,2,3), weight=1)
        ctk.CTkEntry(f, textvariable=self.text_in_px, width=100).grid(row=0, column=0, padx=6, pady=10)
        ctk.CTkEntry(f, textvariable=self.logo_in_px, width=100).grid(row=0, column=1, padx=6, pady=10)
        ctk.CTkEntry(f, textvariable=self.text_out_px, width=100).grid(row=0, column=2, padx=6, pady=10)
        ctk.CTkEntry(f, textvariable=self.logo_out_px, width=100).grid(row=0, column=3, padx=6, pady=10)

        ctk.CTkButton(self, text="Generate Overlay", command=self.generate).grid(row=12, column=0, columnspan=4, pady=16)

    def pick_logo(self):
        p = filedialog.askopenfilename(title="Select logo", filetypes=[("Images","*.png;*.jpg;*.jpeg;*.webp;*.gif"),("All files","*.*")])
        if p:
            self.logo_path.set(p)

    def pick_output(self):
        p = filedialog.askdirectory(title="Choose output folder")
        if p:
            self.output_dir.set(p)

    def pick_accent_color(self):
        initial = self.accent_color.get() if self.accent_color.get() else "#00C2FF"
        rgb, hexval = colorchooser.askcolor(title="Choose Accent/Outline Color", initialcolor=initial)
        if hexval:
            self.accent_color.set(hexval)
            self.accent_entry.delete(0, "end")
            self.accent_entry.insert(0, hexval)

    def generate(self):
        try:
            if not self.logo_path.get():
                messagebox.showerror("Error", "Select a logo file")
                return
            outdir = Path(self.output_dir.get()) if self.output_dir.get() else Path("overlay_project_gui")
            path = render_overlay(
                logo_path=self.logo_path.get(),
                output_dir=outdir,
                brand_text=self.brand_text.get(),
                tagline_text=self.tagline_text.get(),
                show_tagline=self.show_tagline.get(),
                in_duration=float(self.in_duration.get()),
                sustain_duration=float(self.sustain_duration.get()),
                out_duration=float(self.out_duration.get()),
                text_in_anim=float(self.text_in_anim.get()),
                logo_in_anim=float(self.logo_in_anim.get()),
                text_in_px=int(self.text_in_px.get()),
                logo_in_px=int(self.logo_in_px.get()),
                text_out_px=int(self.text_out_px.get()),
                logo_out_px=int(self.logo_out_px.get()),
                accent_color=self.accent_color.get(),
                text_color=self.text_color.get(),
                muted_color=self.muted_color.get(),
                brand_size_css=self.brand_size_css.get(),
                container_max_w=self.container_max_w.get(),
                stroke_scale=float(self.stroke_scale.get()),
                stroke_reveal_seconds=float(self.stroke_reveal_seconds.get()),
                stroke_hide_seconds=float(self.stroke_hide_seconds.get()),
            )
            messagebox.showinfo("Done", f"Overlay generated at:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    App().mainloop()
