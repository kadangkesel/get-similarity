import os
import shutil
import logging
from PIL import Image
import torch
from torch.nn.functional import cosine_similarity
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel
import timm
import sys
import torchvision.transforms as T
import pyiqa

# --- CONFIG ---
if len(sys.argv) >= 5:
    SOURCE_DIR = sys.argv[1]
    FILTER_DIR = sys.argv[2]
    SIMILARITY_THRESHOLD = float(sys.argv[3])
    QUALITY_THRESHOLD = float(sys.argv[4]) 

else:
    SOURCE_DIR = "images"
    FILTER_DIR = "filtered"
    SIMILARITY_THRESHOLD = 0.406  # Default
    QUALITY_THRESHOLD = 70.30  # Default NIQE threshold

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- LOAD CLIP ---
clip_model_name = "openai/clip-vit-base-patch32"
clip_processor = CLIPProcessor.from_pretrained(clip_model_name)
clip_model = CLIPModel.from_pretrained(clip_model_name)
clip_model.eval()

# --- LOAD DINOv2 ---
dino_model = timm.create_model('vit_base_patch16_224_dino', pretrained=True)
dino_model.eval()

# --- DINOv2 TRANSFORM ---
dino_transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])

# --- INIT IQA ---
iqa_model = pyiqa.create_metric('musiq').to('cuda')  # atau gunakan 'musiq', 'dbcnn'

# --- SET DEVICE ---
device = 'cuda' if torch.cuda.is_available() else 'cpu'
clip_model.to(device)
dino_model.to(device)

# --- EVALUASI KUALITAS GAMBAR ---
def is_quality_acceptable(image_path, threshold=70.30):
    try:
        image = Image.open(image_path).convert("RGB")

        image.thumbnail((512, 512), Image.LANCZOS)

        try:
            score = iqa_model(image).item()
            logging.info(f"{image_path} → IQA score: {score}")
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logging.warning(f"Out Of Memory di GPU, menggunakan CPU untuk: {image_path}")
                if not hasattr(is_quality_acceptable, "iqa_model_cpu"):
                    is_quality_acceptable.iqa_model_cpu = pyiqa.create_metric('musiq').to('cpu')
                
                image = Image.open(image_path).convert("RGB")
                image.thumbnail((512, 512), Image.LANCZOS)

                with torch.no_grad():
                    with torch.inference_mode():
                        score = is_quality_acceptable.iqa_model_cpu(image).item()
            else:
                raise e

        return score <= threshold
    except Exception as e:
        logging.warning(f"Gagal evaluasi kualitas gambar {image_path}: {e}")
        return False

# --- GET CLIP EMBEDDING ---
def get_clip_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = clip_model.get_image_features(**inputs)
        return outputs / outputs.norm(p=2, dim=-1, keepdim=True)

# --- GET DINOv2 EMBEDDING ---
def get_dino_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    image_tensor = dino_transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        features = dino_model.forward_features(image_tensor)
        return features / features.norm(p=2, dim=-1, keepdim=True)

# --- COMBINED EMBEDDING ---
def get_combined_embedding(image_path):
    try:
        clip_emb = get_clip_embedding(image_path)
        dino_emb = get_dino_embedding(image_path)
        clip_emb = clip_emb.view(1, -1)
        dino_emb = dino_emb.view(1, -1)
        combined = torch.cat([clip_emb, dino_emb], dim=-1)
        return combined / combined.norm(p=2, dim=-1, keepdim=True)
    except Exception as e:
        logging.warning(f"⚠️ Gagal generate embedding untuk {image_path}: {e}")
        return None

# --- BUAT FOLDER TUJUAN ---
os.makedirs(FILTER_DIR, exist_ok=True)
logging.info(f"Similarity threshold: {SIMILARITY_THRESHOLD}")
logging.info(f"IQA threshold: {QUALITY_THRESHOLD}")

# --- LOAD SEMUA GAMBAR ---
image_paths = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
logging.info(f"{len(image_paths)} gambar ditemukan di folder '{SOURCE_DIR}'")

# --- FILTER GAMBAR BERDASARKAN KUALITAS IQA ---
filtered_paths = []
total = len(image_paths)

for idx, path in enumerate(image_paths, 1):
    if is_quality_acceptable(path, threshold=QUALITY_THRESHOLD):
        filtered_paths.append(path)

    if idx % max(1, total // 100) == 0 or idx == total:
        percent = (idx / total) * 100
        logging.info(f"Evaluasi kualitas: {idx}/{total} gambar ({percent:.1f}%)")

image_paths = filtered_paths
logging.info(f"{len(image_paths)} gambar lolos evaluasi kualitas")

# --- GENERATE EMBEDDING SEMUA GAMBAR ---
embeddings = []
with torch.no_grad():
    for path in tqdm(image_paths, desc="Generating Embeddings"):
        emb = get_combined_embedding(path)
        if emb is not None:
            embeddings.append((path, emb))

# --- KELOMPOKKAN GAMBAR MIRIP ---
visited = set()
groups = []

for i, (path_i, emb_i) in enumerate(embeddings):
    if i in visited:
        continue
    group = [path_i]
    visited.add(i)
    for j in range(i + 1, len(embeddings)):
        if j in visited:
            continue
        _, emb_j = embeddings[j]
        sim = cosine_similarity(emb_i, emb_j).item()
        if sim > SIMILARITY_THRESHOLD:
            group.append(embeddings[j][0])
            visited.add(j)
    groups.append(group)

iqa_scores = {}

def get_cached_iqa_score(image_path):
    if image_path in iqa_scores:
        return iqa_scores[image_path]
    
    try:
        image = Image.open(image_path).convert("RGB")
        image.thumbnail((512, 512), Image.LANCZOS)

        try:
            score = iqa_model(image).item()
        except RuntimeError as e:
            if "CUDA out of memory" in str(e):
                logging.warning(f"Out Of Memory di GPU, menggunakan CPU untuk {image_path}")
                if not hasattr(get_cached_iqa_score, "cpu_model"):
                    get_cached_iqa_score.cpu_model = pyiqa.create_metric('musiq').to('cpu')

                image = Image.open(image_path).convert("RGB")
                image.thumbnail((512, 512), Image.LANCZOS)
                score = get_cached_iqa_score.cpu_model(image).item()
            else:
                raise e

        iqa_scores[image_path] = score
        return score

    except Exception as e:
        logging.warning(f"Gagal hitung IQA {image_path}: {e}")
        iqa_scores[image_path] = float('inf') 
        return float('inf')

# --- SIMPAN GAMBAR DENGAN IQA TERBAIK DARI SETIAP GRUP ---
for group in groups:
    best_image = min(group, key=lambda p: get_cached_iqa_score(p)) 
    filename = os.path.basename(best_image)
    shutil.copy2(best_image, os.path.join(FILTER_DIR, filename))

logging.info(f"Selesai. {len(groups)} gambar dipindahkan ke folder '{FILTER_DIR}'.")