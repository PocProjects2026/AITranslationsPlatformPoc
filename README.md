# i18n_translate

Pipeline de traduction automatisé : **extraction → traduction IA → amélioration → réinjection**.
Supporte les fichiers **JSON** (i18n imbriqué, type `react-i18next`/`vue-i18n`) et **XLIFF** (1.2 et 2.0).

## Installation

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # si --provider anthropic (par défaut)
export DEEPL_API_KEY=xxxxxxxx:fx      # si --provider deepl (le suffixe :fx = compte free)
```

### DeepL API free

Clé disponible sur [deepl.com/pro-api](https://www.deepl.com/pro-api) (plan Free, gratuit jusqu'à
500 000 caractères/mois). Une clé free se termine toujours par `:fx` — le script détecte
automatiquement l'endpoint (`api-free.deepl.com` vs `api.deepl.com`), rien à configurer.

**Important** : DeepL est un moteur de traduction, pas un LLM. Il n'y a pas de vraie relecture
côté DeepL — `improve_batch()` renvoie le brouillon tel quel avec un avertissement. Pour une
vraie passe d'amélioration après DeepL, combine avec Claude :

```bash
python translate.py --input en.json --output fr.json \
  --source-lang en --target-lang fr \
  --provider deepl --improve --improve-provider anthropic
```

→ DeepL traduit rapidement et pas cher, Claude relit ensuite (fautes, ton, cohérence, placeholders).

Les placeholders (`{name}`, `{{var}}`, `%s`, `%1$s`, `%(name)s`) sont automatiquement protégés
avant l'envoi à DeepL (balise `<x>` + `tag_handling=xml`) puis déballés au retour, pour éviter
que DeepL ne les traduise ou les déplace.

Le `--glossary` n'est **pas** appliqué automatiquement avec DeepL (ça demanderait de créer un
glossaire DeepL via son API au préalable) — il est ignoré avec un avertissement.

## Utilisation

```bash
# JSON, traduction simple
python translate.py --input en.json --output fr.json \
  --source-lang en --target-lang fr

# XLIFF, avec passe d'amélioration (relecture IA du brouillon)
python translate.py --input strings.xlf --output strings_fr.xlf \
  --source-lang en --target-lang fr --improve

# Tester le pipeline sans clé API (provider factice)
python translate.py --input en.json --output fr.json \
  --source-lang en --target-lang fr --provider echo
```

### Options utiles

| Option | Rôle |
|---|---|
| `--improve` | Ajoute une 2e passe IA qui relit/corrige chaque traduction (fautes, ton, cohérence). |
| `--glossary glossaire.json` | Impose des traductions de termes précis, ex: `{"dashboard": "tableau de bord"}`. |
| `--batch-size 25` | Nombre de segments envoyés par appel IA (réduis si tu as des textes très longs). |
| `--dump-report report.json` | Sauvegarde source / brouillon / version finale pour chaque segment, utile pour un contrôle qualité humain après coup. |
| `--provider anthropic\|openai\|echo` | Choix du moteur de traduction. |

## Ajouter un provider (DeepL, Google Translate, etc.)

Ouvre `lib/providers.py`, copie la classe `OpenAIProvider` comme modèle, implémente
`translate_batch` et `improve_batch`, puis ajoute ta classe au dict `PROVIDERS` en bas du fichier.

## Comment ça marche

1. **Extraction** (`lib/formats.py`) : parcourt le JSON récursivement ou le XLIFF (`trans-unit`/`segment`)
   et récupère chaque chaîne traduisible avec un chemin permettant de la remettre au bon endroit.
2. **Traduction** (`lib/providers.py`) : envoie les segments par lots à l'IA, avec consigne stricte
   de préserver les placeholders (`{name}`, `%s`, `{{var}}`, balises HTML) et de répondre en JSON structuré.
3. **Amélioration** (optionnelle, `--improve`) : renvoie source + brouillon à l'IA pour une relecture
   ciblée (fautes, contresens, ton, cohérence terminologique).
4. **Réinjection** : reconstruit le fichier de sortie dans son format d'origine, structure intacte.

## Limites connues

- XLIFF : gère 1.2 et 2.0 basique (`trans-unit`/`unit>segment`). Les XLIFF avec balises inline
  complexes (`<g>`, `<x/>`) dans le texte source ne sont pas segmentées finement — à tester sur
  un vrai fichier avant mise en prod.
- JSON : les clés au format ICU pluriel (`{count, plural, ...}`) sont traduites comme du texte
  brut ; vérifie que l'IA ne casse pas la syntaxe ICU (le prompt le mentionne implicitement via
  la consigne sur les placeholders, mais ça vaut le coup de relire ces cas-là).
- Pas de cache : si tu relances sur un fichier déjà traduit, tout est re-traduit (à ajouter si
  besoin : hash du texte source → réutiliser la traduction existante).
