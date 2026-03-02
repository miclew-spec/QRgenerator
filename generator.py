import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

W, H = int(148/25.4*300), int(105/25.4*300)

def podzial(txt):
    if len(txt) < 25 or " " not in txt: return [txt]
    m = len(txt) // 2
    sp = [i for i, c in enumerate(txt) if c == ' ']
    b = min(sp, key=lambda x: abs(x - m))
    return [txt[:b].strip(), txt[b:].strip()]

class Apka:
    def __init__(self, r):
        self.r = r
        r.title("QR Gen")
        tk.Label(r, text="Wklej liste (linia=kod):").pack()
        self.t = tk.Text(r, height=15); self.t.pack()
        tk.Button(r, text="START", command=self.go, bg="green").pack()
        self.p = ttk.Progressbar(r, length=300); self.p.pack()

    def go(self):
        dane = self.t.get("1.0", "end").strip().split('\n')
        f = filedialog.askdirectory()
        if not f or not dane: return
        cel = os.path.join(f, "KODY_QR")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        for i, txt in enumerate(dane, 1):
            img = Image.new("RGB", (W, H), "white")
            drw = ImageDraw.Draw(img)
            qr = qrcode.make(txt).convert("RGB").resize((int(H*0.65), int(H*0.65)))
            img.paste(qr, ((W-qr.size[0])//2, 50))
            y = int(H*0.75)
            for linia in podzial(txt):
                drw.text((100, y), linia, fill="black")
                y += 60
            drw.rectangle([5, 5, W-5, H-5], outline="black", width=3)
            img.save(os.path.join(cel, f"{i:03d}.png"), dpi=(300,300))
            self.p["value"] = i; self.r.update()
        messagebox.showinfo("OK", "Gotowe!")

if __name__ == "__main__":
    root = tk.Tk(); Apka(root); root.mainloop()
