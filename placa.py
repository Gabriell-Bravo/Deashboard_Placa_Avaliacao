"""Gera a arte da plaquinha com QR dinâmico embutido."""

from __future__ import annotations

import hashlib
import io
import os
import threading
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H

ASSETS = Path(__file__).resolve().parent / "assets"
TEMPLATE_PATH = ASSETS / "placa_template.png"
GOOGLE_G_PATH = ASSETS / "google_g.png"

# Coordenadas no template renderizado (1258 x 1787)
QR_BOX_INNER = (701, 1168, 1195, 1536)
PDF_PAGE_SIZE = (419.25, 595.5)  # pontos do PDF original

_lock = threading.Lock()
_template_rgb: Image.Image | None = None
_logo_rgba: Image.Image | None = None


def _cache_dir() -> Path:
    base = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent / "data"))
    path = base / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_key(public_url: str, code: str, kind: str, width: int | None = None) -> str:
    raw = f"{public_url}|{code}|{kind}|{width or 0}|{TEMPLATE_PATH.stat().st_mtime_ns}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _font(size: int, bold: bool = True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf" if bold else "C:/Windows/Fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _get_template() -> Image.Image:
    global _template_rgb
    with _lock:
        if _template_rgb is None:
            _template_rgb = Image.open(TEMPLATE_PATH).convert("RGB")
        return _template_rgb.copy()


def _get_logo() -> Image.Image | None:
    global _logo_rgba
    if not GOOGLE_G_PATH.exists():
        return None
    with _lock:
        if _logo_rgba is None:
            _logo_rgba = Image.open(GOOGLE_G_PATH).convert("RGBA")
        return _logo_rgba.copy()


def _make_qr_with_logo(payload: str, size: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)

    logo = _get_logo()
    if logo is not None:
        logo_size = max(40, size // 4)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.BILINEAR)
        pad = Image.new("RGBA", (logo_size + 10, logo_size + 10), (0, 0, 0, 0))
        mask = Image.new("L", pad.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, pad.size[0] - 1, pad.size[1] - 1), fill=255)
        white = Image.new("RGBA", pad.size, (255, 255, 255, 255))
        pad.paste(white, (0, 0), mask)
        pad.paste(logo, (5, 5), logo)
        pos = ((size - pad.size[0]) // 2, (size - pad.size[1]) // 2)
        qr_img.paste(pad, pos, pad)

    return qr_img


def build_placa_image(public_url: str, code: str = "") -> Image.Image:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Template não encontrado: {TEMPLATE_PATH}. "
            "Coloque placa_template.png em assets/."
        )

    base = _get_template().convert("RGBA")
    left, top, right, bottom = QR_BOX_INNER
    area_w = right - left
    area_h = bottom - top
    qr_size = min(area_w, area_h) - 24

    qr_img = _make_qr_with_logo(public_url, qr_size)
    x = left + (area_w - qr_size) // 2
    y = top + (area_h - qr_size) // 2
    base.paste(qr_img, (x, y), qr_img)

    if code:
        draw = ImageDraw.Draw(base)
        font = _font(28, bold=True)
        bbox = draw.textbbox((0, 0), code, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (base.width - tw) // 2
        ty = 1715
        pad = 10
        draw.rounded_rectangle(
            (tx - pad, ty - 4, tx + tw + pad, ty + th + 8),
            radius=8,
            fill=(255, 255, 255, 255),
        )
        draw.text((tx, ty), code, fill=(17, 24, 39, 255), font=font)

    return base.convert("RGB")


def placa_png_bytes(
    public_url: str,
    code: str = "",
    max_width: int | None = None,
    fmt: str = "PNG",
) -> bytes:
    key = _cache_key(public_url, code, f"img-{fmt.lower()}", max_width)
    ext = "jpg" if fmt.upper() == "JPEG" else "png"
    cache_path = _cache_dir() / f"{key}.{ext}"
    if cache_path.exists():
        return cache_path.read_bytes()

    img = build_placa_image(public_url, code=code)
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        img = img.resize(
            (max_width, max(1, int(img.height * ratio))),
            Image.Resampling.BILINEAR,
        )

    buf = io.BytesIO()
    if fmt.upper() == "JPEG":
        img = img.convert("RGB")
        img.save(buf, format="JPEG", quality=82, optimize=True)
    else:
        img.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    cache_path.write_bytes(data)
    return data


def placa_pdf_bytes(public_url: str, code: str = "") -> bytes:
    import pymupdf

    key = _cache_key(public_url, code, "pdf")
    cache_path = _cache_dir() / f"{key}.pdf"
    if cache_path.exists():
        return cache_path.read_bytes()

    # Reaproveita JPEG em cache / gera uma vez
    jpg = placa_png_bytes(public_url, code=code, fmt="JPEG")

    page_w, page_h = PDF_PAGE_SIZE
    doc = pymupdf.open()
    page = doc.new_page(width=page_w, height=page_h)
    page.insert_image(page.rect, stream=jpg)
    pdf_buf = io.BytesIO()
    doc.save(pdf_buf, deflate=True, garbage=4)
    doc.close()
    data = pdf_buf.getvalue()
    cache_path.write_bytes(data)
    return data
