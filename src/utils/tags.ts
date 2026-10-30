const NON_DISCOVERY_TAGS = new Set(['AI', '周刊']);

/** Tags used for navigation should describe a subject, not the publication itself. */
export function getDiscoveryTags(tags: string[] = []) {
  return tags.filter((tag) => !NON_DISCOVERY_TAGS.has(tag));
}
