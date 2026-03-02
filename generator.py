import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

DPI = 300
W_PX, H_PX = int(148/25.4*DPI), int(105/25.4*DPI)

def split_text(text):
    if len(text) <= 25 or " " not in text:
        return
    mid = len(text) // 2
    spaces =
    best = min(spaces, key=lambda x: abs(x - mid))
    return.strip(), text[best:].strip()]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Generator QR")
        root.geometry("500x500")
        tk.Label(root, text="Wklej liste (linia = kod):").pack()
        self.txt = tk.Text(root, height=15)
        self.txt.pack()
        tk.Button(root, text="GENERUJ", command=self.run, bg="green").pack()
        self.pb = ttk.Progressbar(root, length=400)
        self.pb.pack()

    def run(self):
        raw = self.txt.get("1.0", tk.END).strip()
        if not raw: return
        lines = [l.strip() for l in raw.split('\n') if l.strip()]
        fout = filedialog.askdirectory()
        if not fout: return
        target = os.path.join(fout, "KODY_QR")
        os.makedirs(target, exist_ok=True)
        self.pb["maximum"] = len(lines)
        for i, t in enumerate(lines, 1):
            canvas = Image.new("RGB", (W_PX, H_PX), "white")
            draw = ImageDraw.Draw(canvas)
            qr = qrcode.make(t).convert("RGB").resize((int(H_PX*0.65), int(H_PX*0.65)))
            canvas.paste(qr, ((W_PX-qr.size[0])//2, 50))
            y = int(H_PX*0.75)
            for p in split_text(t):
                f = ImageFont.load_default()
                draw.text((50, y), p, fill="black", font=f)
                y += 50
            draw.rectangle([5, 5, W_PX-5, H_PX-5], outline="black", width=3)
            canvas.save(os.path.join(target, f"{i:03d}.png"), dpi=(300,300))
            self.pb["value"] = i
            self.root.update()
        messagebox.showinfo("OK", "Gotowe")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
