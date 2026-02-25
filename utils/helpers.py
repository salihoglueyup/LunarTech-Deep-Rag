"""
LunarTech AI - Yardımcı Fonksiyonlar
"""

import re
import tiktoken


def count_words(text: str) -> int:
    """Metindeki kelime sayısını döndürür."""
    return len(text.split())


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Metindeki token sayısını döndürür (tiktoken ile)."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def truncate_text(text: str, max_chars: int = 50000) -> str:
    """Metni belirli bir karakter sınırına kadar keser."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... [Metin kısaltıldı]"


def clean_text(text: str) -> str:
    """Metni temizler: fazla boşlukları ve özel karakterleri kaldırır."""
    # Birden fazla boşluğu tek boşluğa çevir
    text = re.sub(r" +", " ", text)
    # Birden fazla yeni satırı ikiye indir
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Baştaki ve sondaki boşlukları temizle
    text = text.strip()
    return text


def format_markdown_heading(title: str, level: int = 2) -> str:
    """Markdown başlık formatlar."""
    prefix = "#" * level
    return f"{prefix} {title}"


def estimate_reading_time(text: str, wpm: int = 200) -> int:
    """Tahmini okuma süresini dakika olarak döndürür."""
    word_count = count_words(text)
    return max(1, word_count // wpm)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Metni belirli boyutta parçalara böler.

    Args:
        text: Bölünecek metin
        chunk_size: Her parçanın karakter boyutu
        overlap: Parçalar arası örtüşme miktarı

    Returns:
        Metin parçalarının listesi
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        # Kelime sınırında kes
        if end < len(text):
            # Son boşluğu bul
            last_space = text.rfind(" ", start, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start <= 0 and len(chunks) > 0:
            break

    return chunks
