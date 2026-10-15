export const PROFILE_SIZES = { 2020: 20, 3030: 30, 4040: 40 }

let nextId = 1
export const makeId = () => `beam-${Date.now().toString(36)}-${nextId++}`

export function makeBeam({ name, profile = 3030, length, position, rotation = [0, 0, 0], color = 'silver' }) {
  return { id: makeId(), name, profile, length, position, rotation, color }
}

export function makeFrame({ width = 900, depth = 500, height = 750, profile = 3030 } = {}) {
  const s = PROFILE_SIZES[profile]
  const x = width / 2 - s / 2
  const z = depth / 2 - s / 2
  const rows = []
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    rows.push(makeBeam({ name: '立柱', profile, length: height, position: [sx * x, height / 2, sz * z], rotation: [0, 0, 90] }))
  }
  for (const y of [s / 2, height - s / 2]) {
    for (const sz of [-1, 1]) rows.push(makeBeam({ name: y < height / 2 ? '底部横梁' : '顶部横梁', profile, length: width - 2 * s, position: [0, y, sz * z] }))
    for (const sx of [-1, 1]) rows.push(makeBeam({ name: y < height / 2 ? '底部纵梁' : '顶部纵梁', profile, length: depth - 2 * s, position: [sx * x, y, 0], rotation: [0, -90, 0] }))
  }
  return rows
}

export function summarizeBom(beams) {
  const groups = new Map()
  for (const beam of beams) {
    const key = `${beam.profile}-${beam.length}-${beam.color}`
    const row = groups.get(key) || { key, profile: beam.profile, length: beam.length, color: beam.color, quantity: 0 }
    row.quantity += 1
    groups.set(key, row)
  }
  return [...groups.values()].sort((a, b) => b.length - a.length || a.profile - b.profile)
}

export function validateDesign(data) {
  if (!data || !Array.isArray(data.beams)) throw new Error('文件中没有构件列表')
  const beams = data.beams.map((beam) => {
    if (!PROFILE_SIZES[beam.profile] || !Number.isFinite(beam.length) || beam.length < 50 || beam.length > 3000) throw new Error('构件规格或长度无效')
    if (!Array.isArray(beam.position) || beam.position.length !== 3 || !beam.position.every(Number.isFinite)) throw new Error('构件位置无效')
    if (!Array.isArray(beam.rotation) || beam.rotation.length !== 3 || !beam.rotation.every(Number.isFinite)) throw new Error('构件角度无效')
    return { id: makeId(), name: String(beam.name || '型材'), profile: beam.profile, length: beam.length, position: beam.position, rotation: beam.rotation, color: beam.color === 'black' ? 'black' : 'silver' }
  })
  return beams
}

export function validateFrame(frame) {
  const defaults = { width: 900, depth: 500, height: 750, profile: 3030 }
  if (!frame) return defaults
  const result = { ...defaults }
  for (const field of ['width', 'depth', 'height']) {
    if (Number.isFinite(frame[field]) && frame[field] >= 200 && frame[field] <= 2000) result[field] = frame[field]
  }
  if (PROFILE_SIZES[frame.profile]) result.profile = frame.profile
  return result
}
