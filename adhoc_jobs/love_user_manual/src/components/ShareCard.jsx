import { axes } from '../data/questions';

export function ShareCard({ result, scores, light = false, cardRef, compact = false }) {
  const lines = Object.entries(scores).map(([axis, score]) => ({
    label: axes[axis].name,
    value: score >= 50 ? axes[axis].right : axes[axis].left,
  }));

  return (
    <div ref={cardRef} className={`share-card ${compact ? 'share-card--compact' : ''}`}>
      <div className="share-card__topline">
        <span>我的关系说明书</span>
        <span>v0.2</span>
      </div>
      <h2>{result.name}</h2>
      {light && <p className="share-card__light">倾向不强，具体场景对你的影响更大</p>}
      <p className="share-card__lead">{result.lead}</p>
      <div className="share-card__axes">
        {lines.map((line) => (
          <div key={line.label}><span>{line.label}</span><strong>{line.value}</strong></div>
        ))}
      </div>
      <div className="share-card__message">
        <span>对我有用</span>
        <p>{result.helpful}</p>
      </div>
      <p className="share-card__request">“{result.request}”</p>
      <div className="share-card__footer">
        <span>不是人格结论，只是这次回答的快照</span>
        <i aria-hidden="true" />
      </div>
    </div>
  );
}
