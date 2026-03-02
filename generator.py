import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

W, H = int(148/25.4*300), int(105/25.4*300)

def podzial(t, max_c=22):
    if len(t) <= max_c or " " not in t: return [t]
    m = len(t) // 2
    sp = [i for i, c in enumerate(t) if c == ' ']
    b = min(sp, key=lambda x: abs(x - m))
    return [t[:b].strip(), t[b:].strip()]

def nazwa(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.strip().replace(" ", "_")[:30]

class Apka:
    def __init__(self, r):
        self.r = r
        r.title("QR Generator A6")
        tk.Label(r, text="Wklej liste (linia=kod):").pack(pady=5)
        self.t = tk.Text(r, height=15, width=60); self.t.pack(pady=10)
        tk.Button(r, text="START", command=self.go, bg="green", fg="white").pack(pady=10)
        self.p = ttk.Progressbar(r, length=400); self.p.pack(pady=10)

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        cel = os.path.join(f, "KODY_QR_A6")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        for i, txt in enumerate(dane, 1):
            txt = txt.strip()
            if not txt: continue
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            qr = qrcode.make(txt).convert("RGB").resize((int(H*0.65), int(H*0.65)))
            img.paste(qr, ((W-qr.size[0])//2, int(H*0.05)))
            y = int(H*0.72)
            for linia in podzial(txt):
                try: fnt = ImageFont.truetype("arialbd.ttf", 85)
                except: fnt = ImageFont.load_default()
                bbox = drw.textbbox((0,0), linia, font=fnt)
                tw = bbox[2] - bbox[0]
                drw.text(((W-tw)//2, y), linia, fill="black", font=fnt)
                y += 90
            drw.rectangle([10, 10, W-10, H-10], outline="black", width=3)
            img.save(os.path.join(cel, f"{i:03d}_{nazwa(txt)}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
        messagebox.showinfo("OK", "Gotowe!")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
