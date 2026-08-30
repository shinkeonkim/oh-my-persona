import Link from "next/link"

import type { ServiceGroup } from "@/data/aif-service-map"

type ServiceMapProps = {
  readonly certCode: string
  readonly groups: readonly ServiceGroup[]
  readonly compact?: boolean
}

export function ServiceMap({ certCode, groups, compact = false }: ServiceMapProps) {
  return (
    <ol className="smap" data-compact={compact} aria-label="서비스 흐름">
      {groups.map((group, i) => (
        <li className="smap-stage" key={group.id}>
          <div className="smap-stage-head">
            <span className="smap-stage-num">{i + 1}</span>
            <span className="smap-stage-title">{group.title}</span>
          </div>
          <ul className="smap-nodes">
            {group.nodes.map((node) => (
              <li key={node.id}>
                <Link className="smap-node" href={`/${certCode}/study/${node.studySlug}`}>
                  <strong className="smap-node-label">{node.label}</strong>
                  {!compact ? <span className="smap-node-desc">{node.description}</span> : null}
                </Link>
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ol>
  )
}
