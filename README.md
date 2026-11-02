# Луна в знаках зодиака

PDF-буклет в голубой перламутровой палитре с округлыми перламутровыми ракушками и жемчугом: обложка и 12 страниц знаков, формат A4.

Готовый файл: `documents/Луна в знаках зодиака.pdf`.

Текст: `assets/content.json`. Слова исходного текста сохранены; нормализованы Unicode и типографские тире, выделены абзацы.

## Сборка

Требуется Python 3.11+ и системный шрифт `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` (пакет fonts-dejavu-core в Debian). Cormorant Garamond включён с лицензией OFL.

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/make_pdf.py
```

Ракушка в `assets/soft-shell.png` сгенерирована ИИ; версия с прозрачным фоном — `assets/soft-shell-cutout.png`.
