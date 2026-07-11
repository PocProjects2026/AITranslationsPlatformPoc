# FrontendApp

Angular application that demonstrates native Angular localization with XLIFF source files.

## Local development

Requires Node.js 22.12 or later.

```powershell
npm install
npm start
```

Run unit tests and create a production build:

```powershell
npm test
npm run build
```

## Localization workflow

Extract source messages from the templates:

```powershell
npm run extract-i18n
```

This writes `src/locale/messages.xlf`. The TranslationService will later supply
`messages.fr.xlf` and `messages.de.xlf` in the same directory. Once those files are
available, use `npm run build -- --localize` to build every configured locale.

The language selector is deliberately local to this first screen. Runtime language
switching will be decided after the initial localized builds are working.
