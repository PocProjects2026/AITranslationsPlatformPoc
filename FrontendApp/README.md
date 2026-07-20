# FrontendApp

Angular application that demonstrates native Angular localization with XLIFF source files.

## Local development

Requires Node.js 22.12 or later.

```powershell
npm install
npm start
```

`npm start` builds all configured locales and serves the localized output on
`http://localhost:4300`. Angular native i18n with XLIFF does not translate the
already-running application in memory. The language selector changes the browser
location to the locale-specific application build:

- English: `/`
- French: `/fr/`
- German: `/de/`

To work against one translated locale during development, run one of:

```powershell
npm run start:dev
npm run start:fr
npm run start:de
```

To test the language selector end to end explicitly, serve the localized
production output:

```powershell
npm run preview:localized
```

Then open `http://localhost:4300`. The dropdown will navigate between the
English root app, the French app under `/fr/`, and the German app under `/de/`.

Run unit tests and create a production build:

```powershell
npm test
npm run build
npm run build:localized
```

## Localization workflow

Extract source messages from the templates:

```powershell
npm run extract-i18n
```

This writes `src/locale/messages.xlf`. The TranslationService will later supply
`messages.fr.xlf` and `messages.de.xlf` in the same directory. Once those files are
available, use `npm run build -- --localize` to build every configured locale.

The localized production build creates separate Angular applications under
`dist/FrontendApp/browser`, with English at the root and translated versions in
`fr` and `de` folders. The hosting layer must serve those folders and route
deep links back to the matching `index.html`.
