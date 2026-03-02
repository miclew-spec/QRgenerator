import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode
import subprocess

DPI = 300
W_PX, H_PX = int(148/25.4*DPI), int(105/25.4*DPI)

def split_text(text, max_chars=28):
    if len(text) <= max_chars or " " not in text:
        return
    mid = len(text) // 2
    spaces =
    if not spaces:
        return
    best_space = min(spaces, key=lambda x: abs(x - mid))
    return.strip(), text[best_space:].strip()]

def sanitize(s):
    return re.sub(r'[\\/*?:"<>|]', "_", s)[:50]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Generator QR A6")
        root.geometry("600x550")
        tk.Label(root, text="Wklej listę (każda linia = jeden kod):").pack(pady=5)
        self.txt_input = tk.Text(root, height=15, width=70)
        self.txt_input.pack(pady=10, padx=20)
        self.btn = tk.Button(root, text="GENERUJ KODY QR", command=self.run, bg="green", fg="white")
        self.btn.pack(pady=10)
        self.pb = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.pb.pack(pady=10)

    def run(self):
        raw = self.txt_input.get("1.0", tk.END).strip()
        if not raw: return
        lines = [l.strip() for l in raw.split('\n') if l.strip()]
        fout = filedialog.askdirectory()
        if not fout: return
        target = os.path.join(fout, "KODY_QR_A6")
        os.makedirs(target, exist_ok=True)
        self.pb["maximum"] = len(lines)
        for i, txt in enumerate(lines, 1):
            canvas = Image.new("RGB", (W_PX, H_PX), "white")
            draw = ImageDraw.Draw(canvas)
            qr = qrcode.make(txt).convert("RGB").resize((int(H_PX*0.65), int(H_PX*0.65)))
            canvas.paste(qr, ((W_PX-qr.size[0])//2, int(H_PX*0.05)))
            parts = split_text(txt)
            y_pos = int(H_PX*0.72)
            for p in parts:
                f = ImageFont.load_default()
                tw = draw.textbbox((0,0), p, font=f)[2]
                draw.text(((W_PX-tw)//2, y_pos), p, fill="black", font=f)
                y_pos += 40
            draw.rectangle([5, 5, W_PX-5, H_PX-5], outline="black", width=3)
            canvas.save(os.path.join(target, f"{i:03d}_{sanitize(txt)}.png"), dpi=(300,300))
            self.pb["value"] = i
            self.root.update()
        messagebox.showinfo("Sukces", "Gotowe!")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
