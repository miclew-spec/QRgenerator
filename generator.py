import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import qrcode

# Parametry A6 300 DPI
W_PX, H_PX = int(148/25.4*300), int(105/25.4*300)

def split_text(text, max_chars=22):
    if len(text) <= max_chars or " " not in text: return
    mid = len(text) // 2
    spaces =
    best = min(spaces, key=lambda x: abs(x - mid))
    return.strip(), text[best:].strip()]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Generator QR A6 - Final")
        root.geometry("500x550")
        tk.Label(root, text="Wklej listę (linia = jeden kod):", font=("Arial", 10)).pack(pady=5)
        self.txt_input = tk.Text(root, height=15, width=60); self.txt_input.pack(pady=10)
        tk.Button(root, text="GENERUJ KODY QR", command=self.run, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10).pack(pady=10)
        self.pb = ttk.Progressbar(root, length=400, mode="determinate"); self.pb.pack(pady=10)

    def run(self):
        content = self.txt_input.get("1.0", tk.END).strip()
        if not content: return
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        fout = filedialog.askdirectory()
        if not fout: return
        target = os.path.join(fout, "KODY_QR_FINAL")
        os.makedirs(target, exist_ok=True)
        self.pb["maximum"] = len(lines)

        for i, txt in enumerate(lines, 1):
            canvas = Image.new("RGB", (W_PX, H_PX), "white")
            draw = ImageDraw.Draw(canvas)
            
            # 1. QR Code - powiększony do ok. 65% wysokości
            qr = qrcode.QRCode(border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(txt); qr.make(fit=True)
            qr_img = qr.make_image().convert("RGB")
            qr_size = int(H_PX * 0.65)
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            canvas.paste(qr_img, ((W_PX - qr_size)//2, int(H_PX * 0.05)))

            # 2. Tekst pod kodem - Pogrubiony i wyśrodkowany
            parts = split_text(txt)
            y_pos = int(H_PX * 0.05) + qr_size + 10
            for p in parts:
                f_size = 80 # Duża czcionka jak na zdjęciu
                while True:
                    try: font = ImageFont.truetype("arialbd.ttf", f_size) # Pogrubiony Arial
                    except: font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), p, font=font)
                    tw = bbox[2] - bbox[0]
                    if tw <= (W_PX - 100) or f_size <= 25: break
                    f_size -= 2
                draw.text(((W_PX - tw)//2, y_pos), p, fill="black", font=font)
                y_pos += f_size + 5

            # 3. Ramka cięcia
            draw.rectangle([10, 10, W_PX-10, H_PX-10], outline="black", width=2)
            
            safe_name = re.sub(r'[\\/*?:"<>|]', "_", txt)[:30]
            canvas.save(os.path.join(target, f"{i:03d}_{safe_name}.png"), dpi=(300,300))
            self.pb["value"] = i; self.root.update()

        messagebox.showinfo("Sukces", "Kody wygenerowane!")

if __name__ == "__main__":
    root = tk.Tk(); App(root); root.mainloop()
