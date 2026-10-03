"""Gera a arte da plaquinha com QR dinâmico embutido."""

from __future__ import annotations

import io
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


def _font(size: int, bold: bool = True):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _make_qr_with_logo(payload: str, size: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=12,
        border=1,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)

    if GOOGLE_G_PATH.exists():
        logo = Image.open(GOOGLE_G_PATH).convert("RGBA")
        logo_size = max(48, size // 4)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # fundo branco circular atrás do G para leitura do QR
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

    base = Image.open(TEMPLATE_PATH).convert("RGBA")
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
        # entre a moldura do QR e a faixa colorida (bem perto da linha)
        tx = (base.width - tw) // 2
        ty = 1715
        # limpa fundo branco atrás do texto
        pad = 10
        draw.rounded_rectangle(
            (tx - pad, ty - 4, tx + tw + pad, ty + th + 8),
            radius=8,
            fill=(255, 255, 255, 255),
        )
        draw.text((tx, ty), code, fill=(17, 24, 39, 255), font=font)

    return base.convert("RGB")


def placa_png_bytes(public_url: str, code: str = "") -> bytes:
    img = build_placa_image(public_url, code=code)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def placa_pdf_bytes(public_url: str, code: str = "") -> bytes:
    import pymupdf

    img = build_placa_image(public_url, code=code)
    # JPEG reduz bastante o PDF sem perder qualidade de impressão prática
    jpg_buf = io.BytesIO()
    img.save(jpg_buf, format="JPEG", quality=92, optimize=True)
    jpg_buf.seek(0)

    page_w, page_h = PDF_PAGE_SIZE
    doc = pymupdf.open()
    page = doc.new_page(width=page_w, height=page_h)
    page.insert_image(page.rect, stream=jpg_buf.getvalue())
    pdf_buf = io.BytesIO()
    doc.save(pdf_buf, deflate=True, garbage=4)
    doc.close()
    return pdf_buf.getvalue()
