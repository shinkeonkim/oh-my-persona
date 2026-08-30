import { fileURLToPath } from "node:url"

import type { ContentSourcePaths } from "../types"

export const PROJECT_ROOT = fileURLToPath(new URL("../../../../", import.meta.url)).replace(
  /\/$/,
  "",
)

export function contentSourcePaths(root: string): ContentSourcePaths {
  return {
    saa: `${root}/content-sources/aws-saa-sutdy-notes`,
    clf: `${root}/content-sources/clf-c02-study-notes`,
    aif: `${root}/content-sources/study-aif-site`,
  }
}
