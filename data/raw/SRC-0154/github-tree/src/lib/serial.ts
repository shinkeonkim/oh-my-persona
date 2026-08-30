export function generateSerial(name: string, os: string, date: string): string {
  let hash = 0;
  const str = `${name}:${os}:${date}:worksonmine`;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  const hex = Math.abs(hash).toString(16).toUpperCase().padStart(8, '0');
  return `WOM-${hex.slice(0, 4)}-${hex.slice(4, 8)}-${Date.now().toString(36).toUpperCase().slice(-4)}`;
}
