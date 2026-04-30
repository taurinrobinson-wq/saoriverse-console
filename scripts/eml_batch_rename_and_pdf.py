#!/usr/bin/env python3
"""
Batch process .eml files:
1) Rename each email file based on sender, sent date/time, and subject snippet.
2) Build one combined PDF per email including email body and attachment content where possible.

Dependencies:
- reportlab
- pypdf

Optional dependency:
- Pillow (improves image format support)

Install example:
    pip install reportlab pypdf Pillow

Usage:
    python scripts/eml_batch_rename_and_pdf.py --input-dir path/to/eml
    python scripts/eml_batch_rename_and_pdf.py --input-dir path/to/eml --output-dir path/to/pdfs --recursive
"""

from __future__ import annotations

import argparse
import html
import os
import re
import tempfile
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr
from pathlib import Path
from typing import Iterable, Iterator, Optional

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def sanitize_filename_component(value: str, max_len: int = 40) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9._-]", "", cleaned)
    cleaned = cleaned.strip("._-")
    if not cleaned:
        cleaned = "unknown"
    return cleaned[:max_len]


def short_subject(subject: str, max_chars: int = 36) -> str:
    subject = re.sub(r"\s+", " ", subject or "").strip()
    if len(subject) <= max_chars:
        return subject
    return subject[:max_chars].rsplit(" ", 1)[0] or subject[:max_chars]


def html_to_text(value: str) -> str:
    # Basic HTML to plain text conversion suitable for email body extraction.
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", value, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/\s*p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def iter_eml_files(input_dir: Path, recursive: bool) -> Iterator[Path]:
    pattern = "**/*.eml" if recursive else "*.eml"
    for path in sorted(input_dir.glob(pattern)):
        if path.is_file():
            yield path


def parse_email(eml_path: Path):
    with eml_path.open("rb") as f:
        return BytesParser(policy=policy.default).parse(f)


def extract_sender(msg) -> str:
    _, sender_email = parseaddr(msg.get("From", ""))
    sender_email = sender_email or "unknown"
    if "@" in sender_email:
        sender_part = sender_email.split("@", 1)[0]
    else:
        sender_part = sender_email
    return sanitize_filename_component(sender_part, max_len=30)


def extract_sent_datetime(msg) -> datetime:
    date_header = msg.get("Date")
    if date_header:
        try:
            dt = parsedate_to_datetime(date_header)
            if dt is not None:
                return dt
        except Exception:
            pass
    return datetime.now()


def extract_subject(msg) -> str:
    subject = msg.get("Subject", "") or "no_subject"
    return sanitize_filename_component(short_subject(subject), max_len=40)


def build_new_eml_name(msg) -> str:
    sender = extract_sender(msg)
    dt = extract_sent_datetime(msg)
    subject = extract_subject(msg)
    return f"{dt:%Y-%m-%d}_{dt:%H%M%S}_{sender}_{subject}.eml"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    idx = 1
    while True:
        candidate = parent / f"{stem}_{idx}{suffix}"
        if not candidate.exists():
            return candidate
        idx += 1


def get_best_body_text(msg) -> str:
    if msg.is_multipart():
        plain_parts = []
        html_parts = []
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            try:
                payload = part.get_content()
            except Exception:
                continue
            if content_type == "text/plain" and isinstance(payload, str):
                plain_parts.append(payload)
            elif content_type == "text/html" and isinstance(payload, str):
                html_parts.append(payload)

        if plain_parts:
            return "\n\n".join(plain_parts).strip()
        if html_parts:
            return html_to_text("\n\n".join(html_parts))
        return ""

    payload = msg.get_content()
    if isinstance(payload, str):
        if msg.get_content_type() == "text/html":
            return html_to_text(payload)
        return payload
    return ""


def make_email_pdf(email_msg, output_pdf: Path) -> None:
    styles = getSampleStyleSheet()
    body_text = get_best_body_text(email_msg) or "(No message body found)"

    story = [
        Paragraph("Email Content", styles["Title"]),
        Spacer(1, 0.2 * inch),
    ]

    headers = [
        ["From", str(email_msg.get("From", ""))],
        ["To", str(email_msg.get("To", ""))],
        ["Cc", str(email_msg.get("Cc", ""))],
        ["Date", str(email_msg.get("Date", ""))],
        ["Subject", str(email_msg.get("Subject", ""))],
    ]

    table = Table(headers, colWidths=[1.2 * inch, 6.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Body", styles["Heading2"]))
    story.append(Preformatted(body_text, styles["Code"]))

    doc = SimpleDocTemplate(str(output_pdf), pagesize=LETTER)
    doc.build(story)


def attachment_to_text_pdf(
    title: str,
    content_text: str,
    output_pdf: Path,
) -> None:
    styles = getSampleStyleSheet()
    story = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 0.2 * inch),
        Preformatted(content_text, styles["Code"]),
    ]
    doc = SimpleDocTemplate(str(output_pdf), pagesize=LETTER)
    doc.build(story)


def attachment_image_to_pdf(image_path: Path, output_pdf: Path, name: str) -> None:
    from reportlab.platypus import Image

    styles = getSampleStyleSheet()
    img = Image(str(image_path))
    max_w = 7.2 * inch
    max_h = 9.0 * inch
    img.drawWidth, img.drawHeight = fit_in_box(img.imageWidth, img.imageHeight, max_w, max_h)

    story = [
        Paragraph(f"Attachment Image: {name}", styles["Title"]),
        Spacer(1, 0.2 * inch),
        img,
    ]
    doc = SimpleDocTemplate(str(output_pdf), pagesize=LETTER)
    doc.build(story)


def fit_in_box(width: float, height: float, max_w: float, max_h: float):
    if width <= 0 or height <= 0:
        return max_w, max_h
    ratio = min(max_w / width, max_h / height)
    return width * ratio, height * ratio


def append_pdf(writer: PdfWriter, pdf_path: Path) -> None:
    reader = PdfReader(str(pdf_path))
    for page in reader.pages:
        writer.add_page(page)


def build_combined_pdf(email_msg, output_pdf: Path) -> list[str]:
    notes: list[str] = []
    writer = PdfWriter()

    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)

        email_pdf = temp_dir / "email_body.pdf"
        make_email_pdf(email_msg, email_pdf)
        append_pdf(writer, email_pdf)

        attach_index = 0
        for part in email_msg.iter_attachments():
            attach_index += 1
            filename = part.get_filename() or f"attachment_{attach_index}"
            content_type = part.get_content_type()
            raw = part.get_payload(decode=True) or b""
            safe_name = sanitize_filename_component(filename, max_len=60)
            ext = Path(filename).suffix.lower()

            raw_path = temp_dir / f"raw_{attach_index}_{safe_name}{ext}"
            raw_path.write_bytes(raw)

            if content_type == "application/pdf" or ext == ".pdf":
                append_pdf(writer, raw_path)
                notes.append(f"Included PDF attachment: {filename}")
                continue

            if content_type.startswith("image/") or ext in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff"}:
                img_pdf = temp_dir / f"attachment_{attach_index}.pdf"
                try:
                    attachment_image_to_pdf(raw_path, img_pdf, filename)
                    append_pdf(writer, img_pdf)
                    notes.append(f"Included image attachment: {filename}")
                except Exception as ex:
                    info_pdf = temp_dir / f"attachment_{attach_index}_info.pdf"
                    attachment_to_text_pdf(
                        f"Attachment: {filename}",
                        f"Could not render image attachment ({content_type}).\nReason: {ex}",
                        info_pdf,
                    )
                    append_pdf(writer, info_pdf)
                    notes.append(f"Attachment image render failed: {filename}")
                continue

            if content_type.startswith("text/") or ext in {".txt", ".csv", ".json", ".xml", ".md", ".log"}:
                text_pdf = temp_dir / f"attachment_{attach_index}.pdf"
                try:
                    text_content = raw.decode("utf-8", errors="replace")
                except Exception:
                    text_content = str(raw)
                attachment_to_text_pdf(f"Attachment Text: {filename}", text_content, text_pdf)
                append_pdf(writer, text_pdf)
                notes.append(f"Included text attachment: {filename}")
                continue

            info_pdf = temp_dir / f"attachment_{attach_index}_info.pdf"
            attachment_to_text_pdf(
                f"Attachment Metadata: {filename}",
                "\n".join(
                    [
                        f"Filename: {filename}",
                        f"Content-Type: {content_type}",
                        f"Size: {len(raw)} bytes",
                        "This file type was attached but not converted inline.",
                    ]
                ),
                info_pdf,
            )
            append_pdf(writer, info_pdf)
            notes.append(f"Added metadata page for unsupported attachment: {filename}")

    with output_pdf.open("wb") as f:
        writer.write(f)

    return notes


def process_email_file(eml_path: Path, output_dir: Path, rename_only: bool = False) -> tuple[Path, Optional[Path], list[str]]:
    msg = parse_email(eml_path)

    new_name = build_new_eml_name(msg)
    target_eml = unique_path(eml_path.with_name(new_name))

    if target_eml != eml_path:
        eml_path.rename(target_eml)

    output_pdf = None
    notes: list[str] = []

    if not rename_only:
        output_pdf = unique_path(output_dir / f"{target_eml.stem}.pdf")
        notes = build_combined_pdf(msg, output_pdf)

    return target_eml, output_pdf, notes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch rename .eml files and build combined PDFs.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--input-dir", type=Path, help="Directory containing .eml files")
    source_group.add_argument("--input-file", type=Path, help="Single .eml file to process")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Where to write PDFs (default: <input-dir>/pdf_output)",
    )
    parser.add_argument("--recursive", action="store_true", help="Include .eml files in subfolders")
    parser.add_argument("--rename-only", action="store_true", help="Rename .eml files without creating PDFs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.input_file:
        input_file: Path = args.input_file
        if not input_file.exists() or not input_file.is_file():
            raise SystemExit(f"Input file does not exist or is not a file: {input_file}")
        if input_file.suffix.lower() != ".eml":
            raise SystemExit(f"Input file must be a .eml file: {input_file}")
        base_dir = input_file.parent
        eml_files = [input_file]
    else:
        input_dir: Path = args.input_dir
        if not input_dir.exists() or not input_dir.is_dir():
            raise SystemExit(f"Input directory does not exist or is not a directory: {input_dir}")
        base_dir = input_dir
        eml_files = list(iter_eml_files(input_dir, recursive=args.recursive))

    output_dir: Path = args.output_dir or (base_dir / "pdf_output")

    if not args.rename_only:
        output_dir.mkdir(parents=True, exist_ok=True)

    if not eml_files:
        print("No .eml files found.")
        return

    print(f"Found {len(eml_files)} .eml files")

    success = 0
    failures = 0
    for eml_path in eml_files:
        try:
            renamed_path, pdf_path, notes = process_email_file(
                eml_path,
                output_dir=output_dir,
                rename_only=args.rename_only,
            )
            success += 1
            print(f"[OK] {eml_path.name} -> {renamed_path.name}")
            if pdf_path:
                print(f"     PDF: {pdf_path}")
            for note in notes:
                print(f"     - {note}")
        except Exception as ex:
            failures += 1
            print(f"[ERR] {eml_path}: {ex}")

    print(f"Done. Success: {success}, Failures: {failures}")


if __name__ == "__main__":
    main()
