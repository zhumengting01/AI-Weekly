/** Return a public asset path unchanged. Public assets are served as authored. */
export function optimizeImagePath(path: string): string {
  if (!path) return '';
  return path;
}
