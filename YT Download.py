import customtkinter as ctk
import yt_dlp
import os
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO

# === PENGATURAN ===
ctk.set_appearance_mode("gelap")
ctk.set_default_color_theme("blue") 
class PengunduhYouTubePRO(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pengunduh YouTube USU PRO")
        self.geometry("750x680")
        self.resizable(False, False)

        # Variabel
        self.folder_unduhan = os.path.join(os.getcwd(), "unduhan")
        os.makedirs(self.folder_unduhan, exist_ok=True)

        self.gambar_kecil = None
        self.format_pilihan = ctk.StringVar(value="Video (MP4)")
        self.kualitas_pilihan = ctk.StringVar(value="720p")
        self.tema_pilihan = ctk.StringVar(value="Gelap")

        self.nama_file_saat_ini = ""
        self.buat_tampilan()

    def buat_tampilan(self):
        # === JUDUL ===
        judul = ctk.CTkLabel(self, text="Pengunduh YouTube USU PRO", font=ctk.CTkFont(size=26, weight="bold"))
        judul.pack(pady=15)

        # === KOTAK URL ===
        kotak_url = ctk.CTkFrame(self)
        kotak_url.pack(pady=10, padx=40, fill="x")

        self.kolom_url = ctk.CTkEntry(
            kotak_url,
            placeholder_text="Tempel URL YouTube di sini",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.kolom_url.pack(pady=12, padx=20, fill="x")
        self.kolom_url.bind("<FocusOut>", lambda e: self.ambil_gambar_kecil_setelah_tempel())
        self.kolom_url.bind("<Return>", lambda e: self.mulai_unduh_di_thread())

        # === GAMBAR KECIL ===
        self.gambar_kecil = ctk.CTkLabel(
            self,
            text="Tempel URL lalu klik di luar kotak...",
            width=300,
            height=180,
            fg_color="gray20",
            corner_radius=10
        )
        self.gambar_kecil.pack(pady=10)

        # === PILIHAN ===
        kotak_pilihan = ctk.CTkFrame(self)
        kotak_pilihan.pack(pady=10, padx=40, fill="x")
        for i in range(5):
            kotak_pilihan.grid_columnconfigure(i, weight=1)

        # Format
        ctk.CTkLabel(kotak_pilihan, text="Format:").grid(row=0, column=0, padx=(10, 5), pady=10, sticky="e")
        pilih_format = ctk.CTkComboBox(
            kotak_pilihan,
            values=["Video (MP4)", "Audio (MP3)"],
            variable=self.format_pilihan,
            width=130
        )
        pilih_format.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        pilih_format.configure(command=self.perbarui_pilihan_kualitas)

        # Kualitas
        ctk.CTkLabel(kotak_pilihan, text="Kualitas:").grid(row=0, column=2, padx=(10, 5), pady=10, sticky="e")
        self.pilih_kualitas = ctk.CTkComboBox(
            kotak_pilihan,
            values=["480p", "720p", "1080p", "Terbaik"],
            variable=self.kualitas_pilihan,
            width=130
        )
        self.pilih_kualitas.grid(row=0, column=3, padx=5, pady=10, sticky="w")

        # Folder
        ctk.CTkButton(kotak_pilihan, text="Pilih Folder", width=100, command=self.pilih_folder)\
            .grid(row=0, column=4, padx=(10, 10), pady=10, sticky="e")

        self.label_folder = ctk.CTkLabel(
            self,
            text=f"Folder: {self.folder_unduhan}",
            font=ctk.CTkFont(size=10),
            text_color="gray50",
            wraplength=700
        )
        self.label_folder.pack(pady=(0, 5), padx=40, fill="x")

        # === TOMBOL UNDUH ===
        self.tombol_unduh = ctk.CTkButton(
            self,
            text="UNDUH",
            height=50,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self.mulai_unduh_di_thread
        )
        self.tombol_unduh.pack(pady=15, fill="x", padx=120)

        # === PROGRESS BAR ===
        self.baris_kemajuan = ctk.CTkProgressBar(self, width=550)
        self.baris_kemajuan.pack(pady=5)
        self.baris_kemajuan.set(0)

        self.label_status = ctk.CTkLabel(self, text="Tempel URL untuk mulai...", font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=5)

        # Label nama file
        self.label_nama_file = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            wraplength=700
        )
        self.label_nama_file.pack(pady=(0, 10), padx=40)

        # === BARIS BAWAH ===
        baris_bawah = ctk.CTkFrame(self)
        baris_bawah.pack(pady=10, fill="x", padx=40)

        ctk.CTkButton(baris_bawah, text="Buka Folder", command=lambda: os.startfile(self.folder_unduhan))\
            .pack(side="left", padx=10)
        ctk.CTkButton(baris_bawah, text="Hapus Info", command=self.hapus_info)\
            .pack(side="left", padx=5)
        ctk.CTkComboBox(
            baris_bawah,
            values=["Gelap", "Terang", "Sistem"],
            variable=self.tema_pilihan,
            width=100,
            command=self.ganti_tema
        ).pack(side="right", padx=10)

    def perbarui_pilihan_kualitas(self, pilihan):
        if pilihan == "Audio (MP3)":
            self.pilih_kualitas.configure(state="disabled")
            self.kualitas_pilihan.set("Tidak Berlaku")
        else:
            self.pilih_kualitas.configure(state="normal")
            self.kualitas_pilihan.set("720p")

    def ambil_gambar_kecil_setelah_tempel(self):
        url = self.kolom_url.get().strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            self.gambar_kecil.configure(text="Memuat gambar kecil...", image=None)
            self.gambar_kecil.image = None
            threading.Thread(target=self._ambil_gambar_kecil, args=(url,), daemon=True).start()

    def _ambil_gambar_kecil(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                url_gambar = info.get('thumbnail')

                if url_gambar:
                    respons = requests.get(url_gambar, timeout=10)
                    data_gambar = BytesIO(respons.content)
                    gambar = Image.open(data_gambar)
                    gambar = gambar.resize((300, 180), Image.Resampling.LANCZOS)
                    foto = ImageTk.PhotoImage(gambar)

                    def perbarui_tampilan():
                        self.gambar_kecil.configure(image=foto, text="")
                        self.gambar_kecil.image = foto
                    self.after(0, perbarui_tampilan)
                else:
                    self.after(0, lambda: self.gambar_kecil.configure(text="Gambar kecil tidak ditemukan", image=None))
        except Exception as e:
            print(f"Gagal ambil gambar kecil: {e}")
            self.after(0, lambda: self.gambar_kecil.configure(text="Gagal memuat gambar kecil", image=None))

    def hapus_info(self):
        self.kolom_url.delete(0, 'end')
        self.gambar_kecil.configure(image=None, text="Tempel URL lalu klik di luar kotak...")
        self.gambar_kecil.image = None
        self.label_status.configure(text="Tempel URL untuk mulai...")
        self.baris_kemajuan.set(0)
        self.label_nama_file.configure(text="")
        self.nama_file_saat_ini = ""

    def pilih_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_unduhan)
        if folder:
            self.folder_unduhan = folder
            self.label_folder.configure(text=f"Folder: {folder}")

    def ganti_tema(self, mode):
        ctk.set_appearance_mode(mode.lower())

    def ambil_format_kualitas(self):
        kualitas = self.kualitas_pilihan.get()
        peta = {
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "Terbaik": "bestvideo+bestaudio/best"
        }
        return peta.get(kualitas, "bestvideo[height<=720]+bestaudio/best[height<=720]")

    def mulai_unduh_di_thread(self):
        threading.Thread(target=self.proses_unduhan, daemon=True).start()

    def proses_unduhan(self):
        url = self.kolom_url.get().strip()
        if not url:
            self.after(0, lambda: messagebox.showwarning("Peringatan", "URL tidak boleh kosong!"))
            return

        def siapkan_tampilan():
            self.tombol_unduh.configure(state="disabled")
            self.label_status.configure(text="Memulai unduh...")
            self.baris_kemajuan.set(0)
            self.label_nama_file.configure(text="")
            self.nama_file_saat_ini = ""
        self.after(0, siapkan_tampilan)

        opsi_yt = {
            'outtmpl': f'{self.folder_unduhan}/%(title)s.%(ext)s',
            'progress_hooks': [self.hook_kemajuan_aman],
            'ignoreerrors': True,
            'no_warnings': True,
        }

        if self.format_pilihan.get() == "Audio (MP3)":
            opsi_yt['format'] = 'bestaudio/best'
            opsi_yt['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opsi_yt['format'] = self.ambil_format_kualitas()
            opsi_yt['merge_output_format'] = 'mp4'

        try:
            with yt_dlp.YoutubeDL(opsi_yt) as ydl:
                info = ydl.extract_info(url, download=True)
                self.nama_file_saat_ini = info.get('title', 'File tidak diketahui')

            def saat_sukses():
                self.label_status.configure(text="SUKSES! File tersimpan!")
                self.label_nama_file.configure(text=f"File: {self.nama_file_saat_ini}")
                messagebox.showinfo("Sukses!", f"Unduh selesai!\nFile: {self.folder_unduhan}")
                os.startfile(self.folder_unduhan)
            self.after(0, saat_sukses)

        except Exception as e:
            pesan_error = str(e)
            print(f"Gagal unduh: {pesan_error}")
            def saat_gagal():
                self.label_status.configure(text="GAGAL!")
                messagebox.showerror("Error", f"Gagal unduh:\n{pesan_error}")
            self.after(0, saat_gagal)

        finally:
            def reset_tampilan():
                self.tombol_unduh.configure(state="normal")
                self.baris_kemajuan.set(0)
            self.after(0, reset_tampilan)

    def hook_kemajuan_aman(self, data):
        if data['status'] == 'downloading':
            try:
                persen_str = data.get('_percent_str', '0.0%').replace('%', '').strip()
                persen_float = float(persen_str) / 100
                kecepatan = data.get('speed')
                kecepatan_str = f"{kecepatan / (1024*1024):.1f} MB/s" if kecepatan else "..."
                teks_status = f"Mengunduh... {persen_str}% ({kecepatan_str})"

                def perbarui():
                    self.baris_kemajuan.set(persen_float)
                    self.label_status.configure(text=teks_status)
                self.after(0, perbarui)
            except Exception as e:
                print(f"Error progress: {e}")
        elif data['status'] == 'finished':
            self.after(0, lambda: self.label_status.configure(text="Memproses file..."))

# === JALANKAN APLIKASI ===
if __name__ == "__main__":
    aplikasi = PengunduhYouTubePRO()
    aplikasi.mainloop()
