
# Get Similarity

![cover](https://github.com/user-attachments/assets/33a28a67-c03d-43eb-ba9c-019a2b09d7fe)

Skrip Python dengan GUI untuk menyaring gambar berdasarkan kualitas (IQA) dan mengelompokkan gambar serupa menggunakan kombinasi embedding **CLIP + DINOv2**.

---

## 🚀 Fitur

* 🔎 Deteksi gambar serupa dengan cosine similarity pada gabungan fitur CLIP + DINOv2.
* 📉 Penyaringan kualitas gambar menggunakan IQA (Image Quality Assessment) berbasis **MusIQ**.
* ⚡ Proses cepat berkat pemanfaatan GPU (jika tersedia).
* 🖥️ GUI sederhana untuk pengguna non-teknis.
* 💾 Cache otomatis untuk skor kualitas (IQA) agar lebih cepat.

---

## 🛠️ Cara Pakai

### 1. Instalasi Awal

```bash
# Buat virtual environment (opsional tapi disarankan)
python -m venv venv
source venv/bin/activate  # atau .\venv\Scripts\activate di Windows

# Install dependency
pip install -r requirements.txt
```

### 2. Jalankan GUI

```bash
python app.py
```

Kamu bisa memilih folder gambar dan langsung proses lewat antarmuka grafis (GUI).

### 3. Jalankan lewat CLI (opsional)

```bash
python similarity.py <source_dir> <output_dir> <similarity_threshold> <quality_threshold>

# Contoh:
python similarity.py images filtered 0.4 75
```

* `similarity_threshold`: nilai cosine similarity (0–1) untuk menentukan seberapa mirip gambar.
* `quality_threshold`: batas maksimum nilai IQA. Nilai lebih besar = semakin ketat

---

![0603](https://github.com/user-attachments/assets/f7a438ec-5b35-4b0b-8ff2-ad4fc8fe445f)

## ⚙️ Pengaturan Threshold

* **Similarity threshold** (`0.4` disarankan):

  * Semakin rendah → lebih banyak gambar dianggap "mirip".
  * Semakin tinggi → hanya gambar yang sangat mirip yang dikelompokkan.

* **Quality threshold** (`75` disarankan untuk MUSIQ):

  * Gambar dengan nilai IQA di atas ambang ini akan diabaikan.
  * Jika terlalu banyak gambar dibuang, coba naikkan nilainya.

---

## 📁 Output

Gambar hasil akan disalin ke folder output (`similarity-generated/` secara default), hanya menyimpan satu gambar terbaik dari setiap grup (berdasarkan kualitas).

---

## 🙋 FAQ

> ❓ *Apa itu IQA?*
> Image Quality Assessment (IQA) digunakan untuk mengevaluasi kualitas gambar secara obyektif (tanpa referensi).

> ❓ *Kenapa harus pakai GPU?*
> Agar proses IQA dan embedding lebih cepat, terutama saat memproses banyak gambar.

> ❓ *Kenapa hanya satu gambar per grup yang disimpan?*
> Agar tidak menyimpan duplikat, hanya satu gambar dengan kualitas terbaik dari setiap kelompok yang disimpan.

> ❓ *Apakah bisa menonaktifkan filter IQA?*
> Bisa. Atur `quality_threshold` ke nilai yang sangat tinggi (misalnya 999) agar tidak ada gambar yang dibuang karena kualitas.

> ❓ *Apakah bisa pakai hanya CLIP atau hanya DINOv2?*
> Versi saat ini menggunakan gabungan fitur dari CLIP dan DINOv2 agar hasilnya lebih akurat. Namun kamu bisa memodifikasi skrip jika ingin hanya memakai salah satu.

> ❓ *Kenapa hasil grouping-nya tidak selalu akurat?*
> Embedding visual bukanlah representasi sempurna — meskipun CLIP + DINOv2 cukup kuat, tetap ada margin kesalahan terutama jika gambar sangat mirip secara visual tapi beda konteks.

---

## 🤖 Model Credits

* **CLIP (Contrastive Language–Image Pretraining)** by OpenAI
  [https://github.com/openai/CLIP](https://github.com/openai/CLIP)

* **DINOv2** by Meta AI
  [https://github.com/facebookresearch/dinov2](https://github.com/facebookresearch/dinov2)

* **MusIQ (Multi-scale Image Quality)** by Adobe Research
  [https://github.com/anse3832/MUSIQ](https://github.com/anse3832/MUSIQ)

Terima kasih kepada semua tim pengembang model open-source yang luar biasa ini 🙏

---

## 👨‍💻 Author

Made with 🤍 by **kadangkesel**

Silakan fork, PR, atau laporkan issue jika menemukan bug atau punya ide perbaikan! 🚀

---

Beri tahu jika ingin menambahkan opsi pengaturan lanjutan atau dokumentasi teknis internal untuk developer.
