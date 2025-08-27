import zipfile
import os
import io
from PIL import Image

# --- Configurazioni ---
INPUT_ZIP = "/Users/gabrieletrusgnich/Downloads/x sito.zip"          # Zip di input
OUTPUT_ZIP = "/Users/gabrieletrusgnich/Downloads/x_sito_compressed.zip"  # Zip di output
EXTRACT_DIR = "extracted_images"  # Cartella temporanea estrazione
OUTPUT_DIR = "processed_images"    # Cartella temporanea output

MAX_PREVIEW_SIZE = 300 * 1024      # 300 KB
MAX_EXPANDED_SIZE = 1500 * 1024    # 1.5 MB
STEP_QUALITY = 5                    # decremento qualità per il loop

# --- Funzione di compressione ---
def compress_image(input_path, output_path, max_size_bytes, step=STEP_QUALITY):
    img = Image.open(input_path)

    # Converti in RGB per JPEG, mantieni PNG se necessario
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    quality = 95
    buffer = io.BytesIO()

    while quality > 5:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size = buffer.tell()
        if size <= max_size_bytes:
            with open(output_path, "wb") as f:
                f.write(buffer.getvalue())
            return
        quality -= step

    # fallback: salva comunque l'ultima versione
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

# --- 1. Estrai lo zip ---
with zipfile.ZipFile(INPUT_ZIP, 'r') as zip_ref:
    zip_ref.extractall(EXTRACT_DIR)

# --- 2. Processa immagini ---
for root, dirs, files in os.walk(EXTRACT_DIR):
    # Ignora cartelle macOS speciali
    if "__MACOSX" in root:
        continue

    for file in files:
        # Ignora file macOS speciali
        if file.startswith("._"):
            continue

        if not file.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        rel_path = os.path.relpath(root, EXTRACT_DIR)
        input_path = os.path.join(root, file)

        # Crea le cartelle di output
        preview_dir = os.path.join(OUTPUT_DIR, "anteprime", rel_path)
        expanded_dir = os.path.join(OUTPUT_DIR, "espansioni", rel_path)
        os.makedirs(preview_dir, exist_ok=True)
        os.makedirs(expanded_dir, exist_ok=True)

        preview_path = os.path.join(preview_dir, file)
        expanded_path = os.path.join(expanded_dir, file)

        # Compressione
        compress_image(input_path, preview_path, MAX_PREVIEW_SIZE)
        compress_image(input_path, expanded_path, MAX_EXPANDED_SIZE)

# --- 3. Crea zip finale ---
with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, OUTPUT_DIR)
            zipf.write(abs_path, rel_path)

print(f"Compressione completata! File generato: {OUTPUT_ZIP}")
