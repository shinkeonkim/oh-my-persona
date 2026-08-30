/**
 * Deterministic file checksum using SHA-256.
 * Used to track source identity without persisting file contents.
 */

export async function computeFileChecksum(filePath: string): Promise<string> {
  const bytes = await Bun.file(filePath).arrayBuffer()
  const hasher = new Bun.CryptoHasher("sha256")
  hasher.update(new Uint8Array(bytes))
  return hasher.digest("hex")
}
