import os
import polib

locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
for lang in ['en', 'fr', 'de']:
    po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
    mo_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.mo')
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        po.save_as_mofile(mo_path)
        print(f"Compiled {mo_path}")
