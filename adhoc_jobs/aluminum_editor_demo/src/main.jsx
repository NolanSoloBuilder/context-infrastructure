import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Canvas, useThree } from '@react-three/fiber'
import { Html, OrbitControls, TransformControls } from '@react-three/drei'
import { Box, Check, ChevronDown, Copy, Download, FileUp, Focus, Grid2X2, Layers3, Move3D, Plus, Redo2, Rotate3D, Save, Trash2, Undo2 } from 'lucide-react'
import { makeBeam, makeFrame, PROFILE_SIZES, summarizeBom, validateDesign, validateFrame } from './model'
import './style.css'

const DEFAULT_FRAME = { width: 900, depth: 500, height: 750, profile: 3030 }
const deg = (value) => value * Math.PI / 180
const rad = (value) => Math.round(value * 180 / Math.PI)

function ProfileMesh({ beam, selected }) {
  const size = PROFILE_SIZES[beam.profile]
  const isBlack = beam.color === 'black'
  const face = isBlack ? '#3b4651' : '#c8d0d7'
  const rim = isBlack ? '#202831' : '#e4e9ec'
  const groove = isBlack ? '#121a22' : '#647480'
  const strip = Math.max(2.5, size * 0.15)
  return (
    <group>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[beam.length, size, size]} />
        <meshStandardMaterial color={selected ? '#b5dfe1' : face} metalness={0.68} roughness={0.31} />
      </mesh>
      {[-1, 1].map((side) => (
        <React.Fragment key={side}>
          <mesh position={[0, side * (size / 2 + 0.14), 0]}>
            <boxGeometry args={[beam.length + 0.2, 0.25, strip]} />
            <meshStandardMaterial color={groove} metalness={0.25} roughness={0.6} />
          </mesh>
          <mesh position={[0, 0, side * (size / 2 + 0.14)]}>
            <boxGeometry args={[beam.length + 0.2, strip, 0.25]} />
            <meshStandardMaterial color={groove} metalness={0.25} roughness={0.6} />
          </mesh>
        </React.Fragment>
      ))}
      {[-1, 1].map((end) => (
        <mesh key={end} position={[end * (beam.length / 2 + 0.2), 0, 0]}>
          <boxGeometry args={[0.4, size - 1, size - 1]} />
          <meshStandardMaterial color={rim} metalness={0.63} roughness={0.4} />
        </mesh>
      ))}
    </group>
  )
}

function Beam3D({ beam, selected, onSelect }) {
  const ref = useRef()
  return (
    <group ref={ref} position={beam.position} rotation={beam.rotation.map(deg)} onClick={(event) => { event.stopPropagation(); onSelect(beam.id, ref.current) }}>
      <ProfileMesh beam={beam} selected={selected} />
      {selected && <Html position={[0, PROFILE_SIZES[beam.profile] / 2 + 38, 0]} center distanceFactor={550} style={{ pointerEvents: 'none' }}><span className="dimension-label">{beam.length} mm</span></Html>}
    </group>
  )
}

function CameraFraming() {
  const { camera, size } = useThree()
  useEffect(() => {
    const aspect = size.width / Math.max(size.height, 1)
    const factor = Math.max(1, 0.95 / aspect)
    camera.position.set(1200 * factor, 1040 * factor, 1320 * factor)
    camera.updateProjectionMatrix()
  }, [camera, size.width, size.height])
  return null
}

function WorkScene({ beams, selectedId, setSelected, mode, onTransform }) {
  const [selectedObject, setSelectedObject] = useState(null)
  const [draggingHandle, setDraggingHandle] = useState(false)
  const activeObject = selectedObject?.userData?.beamId === selectedId ? selectedObject : null
  return (
    <Canvas shadows camera={{ position: [1200, 1040, 1320], fov: 38, near: 1, far: 7000 }} onPointerMissed={() => { setSelected(null); setSelectedObject(null) }}>
      <CameraFraming />
      <color attach="background" args={['#f1f5f6']} />
      <ambientLight intensity={1.25} />
      <directionalLight position={[600, 1200, 800]} intensity={2.1} castShadow shadow-mapSize={[2048, 2048]} shadow-camera-left={-1700} shadow-camera-right={1700} shadow-camera-top={1700} shadow-camera-bottom={-1700} />
      <hemisphereLight args={['#ffffff', '#afbec4', 1.15]} />
      <gridHelper args={[3000, 60, '#c4d2d6', '#dde6e9']} position={[0, -0.8, 0]} />
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.5, 0]}>
        <planeGeometry args={[3000, 3000]} />
        <shadowMaterial transparent opacity={0.13} />
      </mesh>
      <axesHelper args={[110]} position={[-600, 2, -400]} />
      {beams.map((beam) => <Beam3D key={beam.id} beam={beam} selected={selectedId === beam.id} onSelect={(id, object) => { object.userData.beamId = id; setSelected(id); setSelectedObject(object) }} />)}
      {activeObject && <TransformControls object={activeObject} mode={mode} showX showY showZ size={1.15} translationSnap={10} rotationSnap={Math.PI / 12} onMouseDown={() => setDraggingHandle(true)} onMouseUp={() => { setDraggingHandle(false); onTransform(selectedId, activeObject) }} />}
      <OrbitControls makeDefault enabled={!draggingHandle} target={[0, 360, 0]} minDistance={250} maxDistance={4200} maxPolarAngle={Math.PI / 2.02} />
    </Canvas>
  )
}

function ToolButton({ icon: Icon, title, active, disabled, onClick }) {
  return <button type="button" title={title} aria-label={title} className={`icon-button ${active ? 'is-active' : ''}`} disabled={disabled} onClick={onClick}><Icon size={17} strokeWidth={1.9} /></button>
}

function NumberField({ label, value, onChange, min = -3000, max = 3000, unit = 'mm' }) {
  const [draft, setDraft] = useState(String(Math.round(value)))
  const [focused, setFocused] = useState(false)
  useEffect(() => { if (!focused) setDraft(String(Math.round(value))) }, [value, focused])
  return <label className="number-field"><span>{label}</span><span className="input-wrap"><input type="number" min={min} max={max} step="1" value={draft} onFocus={() => setFocused(true)} onChange={(event) => { setDraft(event.target.value); if (event.target.value !== '') onChange(Number(event.target.value)) }} onBlur={() => { setFocused(false); if (draft !== '' && Number.isFinite(Number(draft))) onChange(Number(draft)); else setDraft(String(Math.round(value))) }} onKeyDown={(event) => { if (event.key === 'Enter') event.currentTarget.blur() }} /><small>{unit}</small></span></label>
}

function App() {
  const [initialDesign] = useState(() => {
    try {
      const saved = localStorage.getItem('aluminum-editor-demo-v1')
      if (saved) {
        const data = JSON.parse(saved)
        return { beams: validateDesign(data), frame: validateFrame(data.frame) }
      }
    } catch { /* start with the sample frame if saved data is invalid */ }
    return { beams: makeFrame(DEFAULT_FRAME), frame: DEFAULT_FRAME }
  })
  const [beams, setBeams] = useState(initialDesign.beams)
  const [selectedId, setSelectedId] = useState(null)
  const [frame, setFrame] = useState(initialDesign.frame)
  const [mode, setMode] = useState('translate')
  const [toast, setToast] = useState('')
  const [showBom, setShowBom] = useState(true)
  const [revision, setRevision] = useState(1)
  const undoStack = useRef([])
  const redoStack = useRef([])
  const upload = useRef()
  const selected = beams.find((item) => item.id === selectedId)
  const bom = useMemo(() => summarizeBom(beams), [beams])
  const totalLength = beams.reduce((sum, beam) => sum + beam.length, 0)

  function flash(message) { setToast(message); window.setTimeout(() => setToast(''), 2800) }
  function commit(next) {
    undoStack.current.push(beams)
    if (undoStack.current.length > 40) undoStack.current.shift()
    redoStack.current = []
    setBeams(next)
    setRevision((n) => n + 1)
  }
  function updateBeam(patch) {
    if (!selected) return
    commit(beams.map((beam) => beam.id === selectedId ? { ...beam, ...patch } : beam))
  }
  function changeNumber(field, value) {
    if (!Number.isFinite(value)) return
    const next = field === 'length' ? Math.max(50, Math.min(3000, value)) : value
    updateBeam({ [field]: next })
  }
  function addBeam() {
    const beam = makeBeam({ name: '新增型材', profile: frame.profile, length: 600, position: [0, 460, 0] })
    commit([...beams, beam]); setSelectedId(beam.id); flash('已添加型材')
  }
  function undo() {
    if (!undoStack.current.length) return
    redoStack.current.push(beams); setBeams(undoStack.current.pop()); setSelectedId(null); setRevision((n) => n + 1)
  }
  function redo() {
    if (!redoStack.current.length) return
    undoStack.current.push(beams); setBeams(redoStack.current.pop()); setSelectedId(null); setRevision((n) => n + 1)
  }
  function save() { localStorage.setItem('aluminum-editor-demo-v1', JSON.stringify({ beams, frame })); flash('方案已保存到当前浏览器') }
  function exportJson() {
    const blob = new Blob([JSON.stringify({ version: 1, beams, frame }, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a'); link.href = url; link.download = 'aluminum-design.json'; link.click()
    URL.revokeObjectURL(url)
    flash('已导出 JSON 方案')
  }
  async function importJson(file) {
    if (!file) return
    try { const data = JSON.parse(await file.text()); const next = validateDesign(data); commit(next); setFrame(validateFrame(data.frame)); setSelectedId(null); flash(`已导入 ${next.length} 根型材`) }
    catch (error) { flash(`导入失败：${error.message}`) }
    if (upload.current) upload.current.value = ''
  }
  function transformBeam(id, object) {
    if (!id || !object) return
    const current = beams.find((beam) => beam.id === id)
    if (!current) return
    const position = object.position.toArray().map((n) => Math.round(n))
    const rotation = [rad(object.rotation.x), rad(object.rotation.y), rad(object.rotation.z)]
    if (position.every((n, i) => n === current.position[i]) && rotation.every((n, i) => n === current.rotation[i])) return
    commit(beams.map((beam) => beam.id === id ? { ...beam, position, rotation } : beam))
  }

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand"><div className="brand-mark"><Box size={19} strokeWidth={2.3} /></div><div><strong>型构 <em>Studio</em></strong><small>铝型材 3D 编辑实验</small></div></div>
      <div className="project-title"><span className="live-dot" /> 工作台框架方案 <ChevronDown size={14} /></div>
      <div className="top-actions"><span className="saved-hint">本地设计 · 第 {revision} 版</span><button className="secondary-button" onClick={exportJson}><Download size={15} /> 导出 JSON</button><button className="primary-button" onClick={save}><Save size={15} /> 保存方案</button></div>
    </header>
    <div className="workspace">
      <aside className="left-panel">
        <div className="panel-header"><span className="section-kicker">构件库</span><h2>从型材开始搭建</h2><p>先生成标准框架，再逐根调整尺寸与位置。</p></div>
        <div className="section-heading"><span>快捷操作</span></div>
        <button className="add-button" onClick={addBeam}><Plus size={18} /> 添加单根型材 <span>+</span></button>
        <div className="section-heading section-spaced"><span>框架模板</span><span className="section-note">单位 mm</span></div>
        <div className="template-preview"><div className="mini-cube"><span /><span /><span /></div><div><strong>矩形工作台</strong><small>12 根型材 · 标准四角框架</small></div></div>
        <div className="frame-fields"><NumberField label="宽度" value={frame.width} min={200} max={2000} onChange={(value) => setFrame({ ...frame, width: value })} /><NumberField label="深度" value={frame.depth} min={200} max={2000} onChange={(value) => setFrame({ ...frame, depth: value })} /><NumberField label="高度" value={frame.height} min={200} max={2000} onChange={(value) => setFrame({ ...frame, height: value })} /></div>
        <label className="select-row"><span>型材规格</span><select value={frame.profile} onChange={(event) => setFrame({ ...frame, profile: Number(event.target.value) })}><option value={2020}>2020 · 轻型</option><option value={3030}>3030 · 标准</option><option value={4040}>4040 · 加强</option></select></label>
        <button className="template-button" onClick={() => { if ([frame.width, frame.depth, frame.height].some((n) => !Number.isFinite(n) || n < 200 || n > 2000)) { flash('模板尺寸需在 200–2000 mm 之间'); return } commit(makeFrame(frame)); setSelectedId(null); flash('框架已重新生成') }}><Grid2X2 size={16} /> 生成框架</button>
        <div className="left-bottom"><div className="tip-icon"><Focus size={17} /></div><div><strong>画布操作</strong><p>左键旋转视角，滚轮缩放；点击型材后可拖拽坐标轴。</p></div></div>
      </aside>
      <main className="canvas-area">
        <div className="canvas-top"><div className="canvas-title"><span className="view-indicator" /> 透视视图 <span className="canvas-separator">/</span> 设计画布</div><div className="canvas-tools"><ToolButton icon={Undo2} title="撤销" onClick={undo} /><ToolButton icon={Redo2} title="重做" onClick={redo} /><span className="tool-divider" /><ToolButton icon={Move3D} title="移动构件" active={mode === 'translate'} onClick={() => setMode('translate')} /><ToolButton icon={Rotate3D} title="旋转构件" active={mode === 'rotate'} onClick={() => setMode('rotate')} /></div></div>
        <div className="canvas-stage"><WorkScene beams={beams} selectedId={selectedId} setSelected={setSelectedId} mode={mode} onTransform={transformBeam} /><div className="viewport-badge"><span className="badge-dot" /> 实时 3D 预览</div><div className="axis-legend"><span className="axis-x">X</span><span className="axis-y">Y</span><span className="axis-z">Z</span></div></div>
        <div className="statusbar"><span><span className="status-dot" /> 编辑就绪</span><span>{beams.length} 个构件</span><span>世界坐标 · mm</span><span className="statusbar-right">拖拽坐标轴移动选中构件</span></div>
      </main>
      <aside className="right-panel"><div className="right-header"><span className="section-kicker">属性检查器</span><h2>{selected ? selected.name : '选择一个构件'}</h2><p>{selected ? `${selected.profile} 欧标铝型材 · ${selected.id.slice(-5)}` : '在画布上点击一根型材，编辑它的参数。'}</p></div>
        {selected ? <div className="inspector"><div className="selection-chip"><span className="selection-swatch" /> 已选择 · {selected.name}<Check size={15} /></div><div className="section-heading"><span>基本参数</span></div><label className="select-row"><span>规格</span><select value={selected.profile} onChange={(event) => updateBeam({ profile: Number(event.target.value) })}><option value={2020}>2020 欧标</option><option value={3030}>3030 欧标</option><option value={4040}>4040 欧标</option></select></label><NumberField label="长度" value={selected.length} min={50} max={3000} onChange={(value) => changeNumber('length', value)} /><label className="select-row"><span>表面处理</span><select value={selected.color} onChange={(event) => updateBeam({ color: event.target.value })}><option value="silver">银色阳极氧化</option><option value="black">黑色阳极氧化</option></select></label><div className="section-heading section-spaced"><span>位置</span><span className="section-note">中心点</span></div><div className="coordinate-grid">{['X', 'Y', 'Z'].map((axis, i) => <NumberField key={axis} label={axis} value={selected.position[i]} onChange={(value) => updateBeam({ position: selected.position.map((n, j) => j === i ? value : n) })} />)}</div><div className="section-heading section-spaced"><span>旋转</span></div><div className="coordinate-grid">{['X', 'Y', 'Z'].map((axis, i) => <NumberField key={axis} label={axis} unit="°" min={-360} max={360} value={selected.rotation[i]} onChange={(value) => updateBeam({ rotation: selected.rotation.map((n, j) => j === i ? value : n) })} />)}</div><div className="item-actions"><button onClick={() => { const clone = { ...selected, id: `beam-${Date.now().toString(36)}`, name: `${selected.name} 副本`, position: [selected.position[0] + 80, selected.position[1], selected.position[2] + 80] }; commit([...beams, clone]); setSelectedId(clone.id) }}><Copy size={15} /> 复制</button><button className="danger" onClick={() => { commit(beams.filter((item) => item.id !== selectedId)); setSelectedId(null) }}><Trash2 size={15} /> 删除</button></div></div> : <div className="empty-selection"><Layers3 size={30} strokeWidth={1.2} /><span>点击 3D 构件以查看属性</span></div>}
        <div className="bom-panel"><button className="bom-heading" onClick={() => setShowBom(!showBom)}><span><Layers3 size={17} /> 材料清单</span><span>{bom.length} 类 <ChevronDown className={showBom ? '' : 'rotated'} size={15} /></span></button>{showBom && <><div className="bom-list">{bom.map((row) => <div className="bom-row" key={row.key}><div><strong>{row.profile} 型材</strong><small>{row.length} mm · {row.color === 'black' ? '黑色' : '银色'}</small></div><span>× {row.quantity}</span></div>)}</div><div className="bom-summary"><span>型材总长</span><strong>{(totalLength / 1000).toFixed(2)} m</strong></div></>}</div>
        <div className="import-row"><input ref={upload} type="file" accept="application/json,.json" hidden onChange={(event) => importJson(event.target.files?.[0])} /><button onClick={() => upload.current?.click()}><FileUp size={15} /> 导入 JSON 方案</button></div>
      </aside>
    </div>
    {toast && <div className="toast" role="status"><Check size={16} />{toast}</div>}
  </div>
}

createRoot(document.getElementById('root')).render(<App />)
