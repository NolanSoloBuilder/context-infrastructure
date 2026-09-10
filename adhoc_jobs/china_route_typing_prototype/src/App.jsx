import { useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowRight,
  Books,
  CarProfile,
  CheckCircle,
  Clover,
  Coins,
  Compass,
  ImageSquare,
  Lightning,
  Lightbulb,
  LockSimple,
  Ranking,
  RoadHorizon,
  SpeakerHigh,
  SpeakerSlash,
  SuitcaseRolling,
  Ticket,
  X,
} from "@phosphor-icons/react";
import { JourneyMap } from "./components/JourneyMap";
import { CITIES, ROUTE_POINTS, SCENES } from "./data/journey";
import { FORK_EVENT, LEVELS } from "./data/levels";
import {
  applyForkChoice,
  getLevelProgress,
  INITIAL_RESOURCES,
  isHiddenRouteUnlocked,
  shouldTriggerFork,
} from "./lib/levelGame";

function getDisplayLetters(city) {
  const letters = [];
  city.syllables.forEach((syllable, syllableIndex) => {
    if (syllableIndex > 0) letters.push({ value: " ", key: `space-${syllableIndex}` });
    [...syllable].forEach((value, letterIndex) => {
      letters.push({ value, key: `${syllableIndex}-${letterIndex}` });
    });
  });
  return letters;
}

export function App() {
  const inputRef = useRef(null);
  const arrivalTimerRef = useRef(null);
  const noticeTimerRef = useRef(null);
  const [cityIndex, setCityIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const [arriving, setArriving] = useState(false);
  const [completedCities, setCompletedCities] = useState(1);
  const [soundOn, setSoundOn] = useState(true);
  const [sceneOpen, setSceneOpen] = useState(false);
  const [is3d, setIs3d] = useState(true);
  const [mapFullscreen, setMapFullscreen] = useState(false);
  const [forkOpen, setForkOpen] = useState(false);
  const [forkResolved, setForkResolved] = useState(false);
  const [routeChoice, setRouteChoice] = useState(null);
  const [resources, setResources] = useState(INITIAL_RESOURCES);
  const [totalCorrectLetters, setTotalCorrectLetters] = useState(0);
  const [notice, setNotice] = useState("");
  const hiddenRouteUnlocked = isHiddenRouteUnlocked(totalCorrectLetters);

  const city = CITIES[cityIndex];
  const nextCity = CITIES[(cityIndex + 1) % CITIES.length];
  const scene = SCENES[cityIndex];
  const letters = useMemo(() => getDisplayLetters(city), [city]);
  const typedProgress = typed.length / city.pinyin.length;
  const journeyProgress = getLevelProgress(cityIndex, typedProgress, ROUTE_POINTS.length);

  useEffect(() => {
    inputRef.current?.focus();
    return () => {
      window.clearTimeout(arrivalTimerRef.current);
      window.clearTimeout(noticeTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (typed !== city.pinyin || arriving) return;
    setArriving(true);
    setCompletedCities((value) => Math.min(value + 1, ROUTE_POINTS.length));
    setResources((value) => ({
      ...value,
      money: value.money + 120,
      stamina: Math.max(0, value.stamina - 3),
    }));
    arrivalTimerRef.current = window.setTimeout(() => {
      setCityIndex((value) => (value + 1) % CITIES.length);
      setTyped("");
      setArriving(false);
      inputRef.current?.focus();
    }, 920);
  }, [arriving, city.pinyin, typed]);

  useEffect(() => {
    if (!hiddenRouteUnlocked) return;
    showNotice("隐藏路线条件已达成：熊猫古镇支线已点亮");
  }, [hiddenRouteUnlocked]);

  function showNotice(message) {
    window.clearTimeout(noticeTimerRef.current);
    setNotice(message);
    noticeTimerRef.current = window.setTimeout(() => setNotice(""), 3200);
  }

  function handleInput(event) {
    const normalized = event.target.value.toLowerCase().replace(/[^a-z]/g, "");
    if (arriving || forkOpen) return;
    if (!city.pinyin.startsWith(normalized)) {
      event.target.value = typed;
      return;
    }

    const nextTyped = normalized.slice(0, city.pinyin.length);
    const increment = Math.max(0, nextTyped.length - typed.length);
    if (increment) setTotalCorrectLetters((value) => value + increment);

    if (shouldTriggerFork({ cityIndex, typedLength: nextTyped.length, resolved: forkResolved })) {
      setTyped(nextTyped.slice(0, FORK_EVENT.triggerLetters));
      setForkOpen(true);
      return;
    }
    setTyped(nextTyped);
  }

  function chooseFork(choice) {
    setResources((value) => applyForkChoice(value, choice));
    setRouteChoice(choice.id);
    setForkResolved(true);
    setForkOpen(false);
    showNotice(`${choice.title}已选择 · ${choice.detail}`);
    window.setTimeout(() => inputRef.current?.focus(), 0);
  }

  function resetJourney() {
    window.clearTimeout(arrivalTimerRef.current);
    setCityIndex(0);
    setTyped("");
    setArriving(false);
    setCompletedCities(1);
    setResources(INITIAL_RESOURCES);
    setTotalCorrectLetters(0);
    setForkOpen(false);
    setForkResolved(false);
    setRouteChoice(null);
    setSceneOpen(false);
    setMapFullscreen(false);
    showNotice("第一关已重新开始");
    inputRef.current?.focus();
  }

  return (
    <main
      className={`journey-app branching-game${mapFullscreen ? " map-fullscreen" : ""}`}
      onClick={() => !forkOpen && inputRef.current?.focus()}
    >
      <input
        ref={inputRef}
        className="typing-capture"
        value={typed}
        onChange={handleInput}
        aria-label={`输入 ${city.name} 的拼音`}
        disabled={forkOpen}
        autoCapitalize="none"
        autoComplete="off"
        spellCheck="false"
      />

      <header className="game-header">
        <button className="brand" type="button" onClick={resetJourney}>打字游中国</button>
        <nav className="main-nav" aria-label="主要功能">
          <button type="button" className="active"><Compass size={19} />分岔奇遇</button>
          <button type="button" onClick={() => showNotice("城市图鉴将在收集第一枚城市章后开放")}><Books size={19} />城市图鉴</button>
          <button type="button" onClick={() => showNotice("旅途记录会在本关结束后生成")}><SuitcaseRolling size={19} />我的旅途</button>
          <button type="button" onClick={() => showNotice("完成第一关后进入路线排行榜")}><Ranking size={19} />排行榜</button>
        </nav>

        <div className="resource-bar" aria-label="旅行资源">
          <span><Coins size={19} weight="fill" />旅费 <strong>{resources.money.toLocaleString()}</strong></span>
          <span><Lightning size={20} weight="fill" />体力 <strong>{resources.stamina}/60</strong></span>
          <span><Clover size={20} weight="fill" />幸运值 <strong>{resources.luck}</strong></span>
        </div>

        <div className="header-actions">
          <button type="button" aria-label={soundOn ? "关闭声音" : "开启声音"} onClick={() => setSoundOn((value) => !value)}>
            {soundOn ? <SpeakerHigh size={21} /> : <SpeakerSlash size={21} />}
          </button>
          <button type="button" aria-label="查看当前实景" aria-expanded={sceneOpen} onClick={() => setSceneOpen((value) => !value)}>
            <ImageSquare size={21} />
          </button>
        </div>
      </header>

      <section className="map-stage" aria-label="川南城市线第一关">
        <JourneyMap
          cityIndex={cityIndex}
          typedProgress={typedProgress}
          arriving={arriving}
          is3d={is3d}
          onToggle3d={() => setIs3d((value) => !value)}
          fullscreen={mapFullscreen}
          onToggleFullscreen={() => setMapFullscreen((value) => !value)}
          hiddenRouteUnlocked={hiddenRouteUnlocked}
        />

        <div className="level-selector" aria-label="路线关卡">
          {LEVELS.map((level) => (
            <button
              key={level.id}
              type="button"
              className={level.status}
              aria-current={level.status === "active" ? "step" : undefined}
              onClick={() => level.status === "locked" && showNotice(`${level.name}：通关第一关后解锁`)}
            >
              <span className="level-number">{level.number}</span>
              <span><strong>第{["一", "二", "三"][level.number - 1]}关　{level.name}</strong><small>{level.summary}</small></span>
              {level.status === "locked" ? <LockSimple size={16} weight="fill" /> : null}
            </button>
          ))}
        </div>

        <section className="level-progress" aria-label={`当前进度 ${Math.round(journeyProgress)}%`}>
          <span>当前进度</span>
          <strong>{Math.round(journeyProgress)}%</strong>
          <div className="progress-track" style={{ "--progress": `${journeyProgress}%` }}>
            <span />
            <CarProfile size={25} weight="fill" style={{ left: `${journeyProgress}%` }} />
          </div>
          <div className="progress-cities">
            {ROUTE_POINTS.map((point, index) => (
              <span className={index <= cityIndex ? "reached" : ""} key={point.name}>{point.name}</span>
            ))}
          </div>
        </section>

        {forkOpen ? (
          <section className="fork-event" role="dialog" aria-modal="true" aria-labelledby="fork-title" onClick={(event) => event.stopPropagation()}>
            <div className="event-title">
              <span><Compass size={25} weight="fill" /></span>
              <div><strong id="fork-title">{FORK_EVENT.title}</strong><i /></div>
              <button type="button" aria-label="暂时关闭奇遇" onClick={() => setForkOpen(false)}><X size={18} /></button>
            </div>
            <p>{FORK_EVENT.description}</p>
            <div className="fork-choices">
              {FORK_EVENT.choices.map((choice) => (
                <button type="button" key={choice.id} onClick={() => chooseFork(choice)}>
                  <span><RoadHorizon size={28} weight={choice.id === "national-road" ? "regular" : "fill"} /></span>
                  <span><strong>{choice.title}</strong><small>{choice.detail}</small></span>
                  <ArrowRight size={23} />
                </button>
              ))}
            </div>
            <div className={`hidden-condition${hiddenRouteUnlocked ? " unlocked" : ""}`}>
              {hiddenRouteUnlocked ? <CheckCircle size={20} weight="fill" /> : <Lightbulb size={20} />}
              {hiddenRouteUnlocked ? "隐藏路线已触发" : "连续正确 12 次可触发隐藏路线"}
            </div>
          </section>
        ) : null}

        {routeChoice ? (
          <span className="route-choice-chip">
            <Ticket size={17} weight="fill" />{routeChoice === "national-road" ? "国道支线" : "高速路线"}
          </span>
        ) : null}

        {sceneOpen ? (
          <aside className="scene-popover" onClick={(event) => event.stopPropagation()}>
            <img src={scene.src} alt={scene.alt} />
            <div><strong>{scene.title} · {scene.city}</strong><span>摄影：{scene.photographer} · {scene.license}</span><a href={scene.sourceUrl} target="_blank" rel="noreferrer">查看实景来源</a></div>
          </aside>
        ) : null}

        <section className={`typing-dock${arriving ? " arrived" : ""}${forkOpen ? " paused" : ""}`} aria-live="polite">
          <div className="destination-block">
            <span>{forkOpen ? "奇遇触发" : arriving ? "已经抵达" : "正在前往"}</span>
            <strong>{city.name}</strong>
          </div>
          <div className="pinyin-block" aria-label={`${city.name}，${city.syllables.join(" ")}`}>
            <div className="pinyin-letters" aria-hidden="true">
              {letters.map((letter, displayIndex) => {
                if (letter.value === " ") return <span className="letter-space" key={letter.key}> </span>;
                const letterIndex = letters.slice(0, displayIndex).filter((item) => item.value !== " ").length;
                const state = letterIndex < typed.length ? "typed" : letterIndex === typed.length ? "active" : "pending";
                return <span className={state} key={letter.key}>{letter.value}</span>;
              })}
            </div>
            <p>{forkOpen ? "选择一条路线，继续旅程" : "输入拼音，抵达下一城"}</p>
          </div>
          <div className="next-block">
            <span>下一城</span><strong>{nextCity.name}</strong><ArrowRight size={28} />
          </div>
        </section>
      </section>

      {notice ? <div className="game-notice" role="status">{notice}</div> : null}
    </main>
  );
}
