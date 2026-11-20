"""Apply a subtle powder-pink grade to the original champagne silk, without regeneration."""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = Image.open(ROOT / 'assets/venus-silk-background.png').convert('RGB')
pixels = np.asarray(source, dtype=np.float32)
# Keep the original folds and highlights; gently reduce yellow and add blush.
pixels[:, :, 0] += 2.0
pixels[:, :, 1] -= 7.0
pixels[:, :, 2] += 2.0
Image.fromarray(np.clip(pixels, 0, 255).astype('uint8')).save(
    ROOT / 'assets/venus-silk-background.jpg', quality=94
)
