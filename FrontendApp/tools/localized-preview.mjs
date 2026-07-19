import { createReadStream, existsSync, statSync } from 'node:fs';
import { createServer } from 'node:http';
import { extname, join, normalize, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const currentDirectory = fileURLToPath(new URL('.', import.meta.url));
const rootDirectory = resolve(
  currentDirectory,
  '..',
  'dist',
  'FrontendApp',
  'browser',
);
const port = Number(process.argv[2] ?? process.env.PORT ?? 4200);
const locales = new Set(['fr', 'de']);

const contentTypes = new Map([
  ['.css', 'text/css; charset=utf-8'],
  ['.html', 'text/html; charset=utf-8'],
  ['.ico', 'image/x-icon'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml; charset=utf-8'],
]);

const server = createServer((request, response) => {
  const requestedPath = decodeURIComponent(
    new URL(request.url ?? '/', `http://${request.headers.host}`).pathname,
  );
  const filePath = resolveFilePath(requestedPath);

  if (!filePath.startsWith(rootDirectory + sep) && filePath !== rootDirectory) {
    response.writeHead(403);
    response.end('Forbidden');
    return;
  }

  response.writeHead(200, {
    'Content-Type':
      contentTypes.get(extname(filePath)) ?? 'application/octet-stream',
  });

  createReadStream(filePath)
    .on('error', () => {
      response.writeHead(500);
      response.end('Unable to read file');
    })
    .pipe(response);
});

server.listen(port, () => {
  console.log(`Localized preview running at http://localhost:${port}`);
});

function resolveFilePath(requestedPath) {
  const cleanPath = normalize(requestedPath).replace(/^([/\\])+/, '');
  const directPath = join(rootDirectory, cleanPath);

  if (existsSync(directPath) && statSync(directPath).isFile()) {
    return directPath;
  }

  const [locale] = cleanPath.split(/[\\/]/);

  if (locales.has(locale)) {
    return join(rootDirectory, locale, 'index.html');
  }

  return join(rootDirectory, 'index.html');
}
