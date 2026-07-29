import { posts } from '../data/posts';
import { ShareCard } from './ShareCard';
import { resultTypes } from '../data/results';

const sampleScores = {
  recovery_high: { recovery: 84, expression: 56, clarity: 72, repair: 61 },
  recovery_low: { recovery: 18, expression: 48, clarity: 36, repair: 42 },
  expression_high: { recovery: 52, expression: 88, clarity: 65, repair: 72 },
  expression_low: { recovery: 55, expression: 22, clarity: 58, repair: 39 },
  clarity_high: { recovery: 64, expression: 54, clarity: 91, repair: 57 },
  clarity_low: { recovery: 42, expression: 61, clarity: 16, repair: 58 },
  repair_high: { recovery: 68, expression: 59, clarity: 48, repair: 93 },
  repair_low: { recovery: 38, expression: 44, clarity: 63, repair: 14 },
};

export function CoverStudio() {
  return (
    <main className="studio">
      <section className="studio__covers">
        {posts.map((post, index) => (
          <article className={`xhs-cover xhs-cover--${index % 4}`} data-cover={post.id} key={post.id}>
            <div className="xhs-cover__header">
              <span>关系说明书</span>
              <span>{post.id} / 10</span>
            </div>
            <div className="xhs-cover__motif" aria-hidden="true"><i /><i /></div>
            <div className="xhs-cover__copy">
              <span>{post.cover[0]}</span>
              <strong>{post.cover[1]}</strong>
            </div>
            <div className="xhs-cover__footer">
              <span>{post.formula.replace(/^#[0-9]+\s*/, '')}</span>
              <i />
              <span>关系里，说得明白一点</span>
            </div>
          </article>
        ))}
      </section>

      <section className="studio__cards">
        {Object.entries(resultTypes).map(([key, result]) => (
          <div data-share-card={key} key={key} className="studio__share-frame">
            <ShareCard result={result} scores={sampleScores[key]} />
          </div>
        ))}
      </section>
    </main>
  );
}
