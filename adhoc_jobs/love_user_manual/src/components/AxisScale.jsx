import { axes } from '../data/questions';

export function AxisScale({ axis, score }) {
  const info = axes[axis];
  return (
    <div className="axis-scale">
      <div className="axis-scale__labels">
        <span>{info.left}</span>
        <strong>{info.name}</strong>
        <span>{info.right}</span>
      </div>
      <div className="axis-scale__track" aria-label={`${info.name}：${score}分`}>
        <i className="axis-scale__mid" />
        <i className="axis-scale__dot" style={{ left: `${score}%` }} />
      </div>
    </div>
  );
}
