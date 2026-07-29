import { useEffect, useMemo, useRef, useState } from 'react';
import { toPng } from 'html-to-image';
import { BrandMark, RegistrationMark } from './components/BrandMark';
import { LinePeople } from './components/LinePeople';
import { AxisScale } from './components/AxisScale';
import { ShareCard } from './components/ShareCard';
import { CoverStudio } from './components/CoverStudio';
import { axes, questions } from './data/questions';
import { axisNotes, resultTypes } from './data/results';
import { calculateScores, getBand, getResultKey, isComplete } from './lib/scoring';

const STORAGE_KEY = 'relationship-manual-v02';

function readSavedAnswers() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch {
    return {};
  }
}

function downloadUrl(url, filename) {
  const link = document.createElement('a');
  link.download = filename;
  link.href = url;
  link.click();
}

function StartScreen({ onStart, onAbout, hasProgress }) {
  return (
    <main className="app-shell start-screen">
      <header className="app-header"><BrandMark /><RegistrationMark /></header>
      <LinePeople />
      <section className="start-screen__copy">
        <h1>给关系一份<br />说得明白的说明书</h1>
        <p>不是判断你属于哪一类人。只是把你在冲突里常见的反应，翻成对方听得懂的话。</p>
      </section>
      <div className="start-screen__actions">
        <button className="button button--primary" data-testid="start-quiz" onClick={onStart}>{hasProgress ? '继续上次答题' : '开始，约 4 分钟'}</button>
        <button className="text-button" onClick={onAbout}>先看看它测什么</button>
      </div>
      <footer className="fact-line"><span>24 个关系场景</span><i /><span>不收集姓名</span><i /><span>不是心理诊断</span></footer>
    </main>
  );
}

function AboutScreen({ onBack, onStart }) {
  return (
    <main className="app-shell about-screen">
      <header className="app-header"><BrandMark compact /><button className="header-action" onClick={onBack}>返回</button></header>
      <section className="about-screen__intro">
        <h1>它不测谁更成熟。<br />只看四种节奏。</h1>
        <p>请按最近半年更常见的反应作答。关系不同、事情不同，答案也可能变化。</p>
      </section>
      <div className="axis-explainer">
        {Object.values(axes).map((axis, index) => (
          <div key={axis.name}>
            <span>0{index + 1}</span>
            <strong>{axis.name}</strong>
            <p>{axis.left} <i /> {axis.right}</p>
          </div>
        ))}
      </div>
      <section className="about-screen__note">
        <h2>先说清边界</h2>
        <p>这份问卷借鉴关系、沟通与情绪调节研究中的问题，但不是已发表量表，也没有人群常模。结果不会判断该不该分手，也不会替你诊断伴侣。</p>
      </section>
      <button className="button button--primary" onClick={onStart}>我知道了，开始</button>
    </main>
  );
}

function QuizScreen({ answers, setAnswers, startAt, onComplete, onExit }) {
  const [index, setIndex] = useState(startAt);
  const question = questions[index];
  const selected = answers[question.id];
  const progress = ((index + 1) / questions.length) * 100;

  const select = (value) => setAnswers((current) => ({ ...current, [question.id]: value }));
  const next = () => {
    if (!Number.isFinite(selected)) return;
    if (index === questions.length - 1) onComplete();
    else {
      setIndex((current) => current + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <main className="app-shell quiz-screen">
      <header className="quiz-header">
        <button className="brand-button" onClick={onExit}>关系说明书</button>
        <span><b>{String(index + 1).padStart(2, '0')}</b> / 24</span>
      </header>
      <div className="progress"><i style={{ width: `${progress}%` }} /></div>
      <section className="question-block">
        <p className="question-block__scene">{question.scene}</p>
        <h1>{question.prompt}</h1>
        <div className="answer-list" role="radiogroup" aria-label={question.prompt}>
          {question.options.map((option) => (
            <button
              key={option.value}
              role="radio"
              aria-checked={selected === option.value}
              className={selected === option.value ? 'answer answer--selected' : 'answer'}
              data-testid={`answer-${option.value}`}
              onClick={() => select(option.value)}
            >
              <i />
              <span>{option.label}</span>
            </button>
          ))}
        </div>
        <p className="question-helper">＊选最像你的，不用选更成熟的那个</p>
      </section>
      <nav className="quiz-nav">
        <button className="button button--outline" disabled={index === 0} onClick={() => setIndex((current) => current - 1)}>上一题</button>
        <button className="button button--dark" data-testid="next-question" disabled={!Number.isFinite(selected)} onClick={next}>{index === questions.length - 1 ? '看结果' : '下一题'}</button>
      </nav>
    </main>
  );
}

function ResultScreen({ answers, onReset }) {
  const cardRef = useRef(null);
  const [showFull, setShowFull] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState('');
  const scores = useMemo(() => calculateScores(answers), [answers]);
  const resultMeta = getResultKey(scores);
  const result = resultTypes[resultMeta.key];

  const saveCard = async () => {
    if (!cardRef.current || exporting) return;
    setExporting(true);
    setExportError('');
    try {
      const dataUrl = await toPng(cardRef.current, { pixelRatio: 2, cacheBust: true, backgroundColor: '#fbf8f0' });
      downloadUrl(dataUrl, `我的关系说明书-${result.name}.png`);
    } catch {
      setExportError('这次没保存下来，请再试一次。');
    } finally {
      setExporting(false);
    }
  };

  return (
    <main className="app-shell result-screen">
      <header className="result-header"><BrandMark compact /><button className="header-action" onClick={onReset}>重新测试</button></header>
      <section className="result-hero">
        <p>你已完成 <b>24</b> 题</p>
        <h1>{result.name}</h1>
        {resultMeta.light && <span className="light-tendency">倾向较轻，具体场景影响更大</span>}
        <p className="result-hero__lead">{result.lead}</p>
      </section>

      <section className="score-section" aria-label="四个观察方向">
        {Object.entries(scores).map(([axis, score]) => <AxisScale axis={axis} score={score} key={axis} />)}
      </section>

      <section className="share-section">
        <h2>发给重要的人看</h2>
        <ShareCard result={result} scores={scores} light={resultMeta.light} cardRef={cardRef} compact />
        <button className="button button--primary" onClick={saveCard}>{exporting ? '正在生成…' : '保存分享卡'}</button>
        {exportError && <p className="export-error" role="alert">{exportError}</p>}
        <button className="button button--outline" onClick={() => setShowFull((current) => !current)}>{showFull ? '收起完整说明书' : '看看完整说明书'}</button>
      </section>

      {showFull && (
        <section className="full-report">
          <article><span>你已经会的</span><h2>{result.strength}</h2></article>
          <article><span>容易卡住的地方</span><h2>{result.friction}</h2></article>
          <article><span>可以直接说</span><blockquote>“{result.request}”</blockquote></article>
          <article><span>这周只练一件事</span><h2>{result.practice}</h2></article>
          <div className="axis-notes">
            <h2>四个方向，分别怎么看</h2>
            {Object.entries(scores).map(([axis, score]) => (
              <p key={axis}><strong>{axes[axis].name}</strong>{axisNotes[axis][getBand(score)]}</p>
            ))}
          </div>
          <aside className="safety-note">
            <strong>这份说明书不适用于暴力和强迫控制。</strong>
            <p>如果关系里存在威胁、跟踪、限制人身自由或身体伤害，优先寻找现实中的安全支持，而不是继续练习沟通。</p>
          </aside>
        </section>
      )}

      <footer className="result-footer">这是一份最近半年关系反应的自我观察，不是人格结论，也不是心理诊断。</footer>
    </main>
  );
}

export default function App() {
  const studioMode = new URLSearchParams(window.location.search).has('studio');
  const [answers, setAnswers] = useState(readSavedAnswers);
  const [screen, setScreen] = useState(isComplete(readSavedAnswers()) ? 'result' : 'start');

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(answers));
  }, [answers]);

  if (studioMode) return <CoverStudio />;

  const firstMissing = Math.max(0, questions.findIndex((question) => !Number.isFinite(answers[question.id])));

  const reset = () => {
    setAnswers({});
    localStorage.removeItem(STORAGE_KEY);
    setScreen('start');
    window.scrollTo(0, 0);
  };

  if (screen === 'about') return <AboutScreen onBack={() => setScreen('start')} onStart={() => setScreen('quiz')} />;
  if (screen === 'quiz') return <QuizScreen answers={answers} setAnswers={setAnswers} startAt={firstMissing} onComplete={() => setScreen('result')} onExit={() => setScreen('start')} />;
  if (screen === 'result') return <ResultScreen answers={answers} onReset={reset} />;
  return <StartScreen onStart={() => setScreen('quiz')} onAbout={() => setScreen('about')} hasProgress={Object.keys(answers).length > 0} />;
}
