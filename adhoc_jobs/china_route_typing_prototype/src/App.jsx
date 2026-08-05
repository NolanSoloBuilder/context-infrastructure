import { useEffect, useMemo, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import {
  ArrowLeft,
  ArrowRight,
  ArrowsIn,
  ArrowsOut,
  CaretDown,
  CarProfile,
  ImageSquare,
  MapTrifold,
  SpeakerHigh,
  SpeakerSlash,
  X,
} from "@phosphor-icons/react";

const CITIES = [
  { name: "雅安", pinyin: "yaan", syllables: ["ya", "an"], coordinates: [103.0133, 29.9805] },
  { name: "乐山", pinyin: "leshan", syllables: ["le", "shan"], coordinates: [103.7656, 29.5521] },
  { name: "宜宾", pinyin: "yibin", syllables: ["yi", "bin"], coordinates: [104.6432, 28.7513] },
];

const ROUTE_POINTS = [
  { name: "成都", coordinates: [104.0665, 30.5728] },
  ...CITIES,
];
const ROUTE_CITY_COUNT = ROUTE_POINTS.length;
const MAP_STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
const ROUTE_DATA_URL = "/data/chengdu-yibin-route.geojson";

function lineFeature(coordinates) {
  return {
    type: "Feature",
    properties: {},
    geometry: { type: "LineString", coordinates },
  };
}

function pointFeature(name, coordinates) {
  return {
    type: "Feature",
    properties: { name },
    geometry: { type: "Point", coordinates },
  };
}

function nearestCoordinateIndex(coordinates, target) {
  let result = 0;
  let smallestDistance = Number.POSITIVE_INFINITY;
  coordinates.forEach((coordinate, index) => {
    const distance = (coordinate[0] - target[0]) ** 2 + (coordinate[1] - target[1]) ** 2;
    if (distance < smallestDistance) {
      smallestDistance = distance;
      result = index;
    }
  });
  return result;
}

function getMapJourney(cityIndex, typedProgress, routeCoordinates) {
  const segmentIndex = Math.min(cityIndex, ROUTE_POINTS.length - 2);
  const startIndex = nearestCoordinateIndex(routeCoordinates, ROUTE_POINTS[segmentIndex].coordinates);
  const endIndex = nearestCoordinateIndex(routeCoordinates, ROUTE_POINTS[segmentIndex + 1].coordinates);
  const routePosition = startIndex + Math.max(0, endIndex - startIndex) * typedProgress;
  const lowerIndex = Math.floor(routePosition);
  const upperIndex = Math.min(Math.ceil(routePosition), routeCoordinates.length - 1);
  const fraction = routePosition - lowerIndex;
  const start = routeCoordinates[lowerIndex];
  const end = routeCoordinates[upperIndex];
  const position = [
    start[0] + (end[0] - start[0]) * fraction,
    start[1] + (end[1] - start[1]) * fraction,
  ];

  return {
    completed: [...routeCoordinates.slice(0, lowerIndex + 1), position],
    position,
  };
}

function JourneyMap({ cityIndex, typedProgress }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const [routeCoordinates, setRouteCoordinates] = useState(ROUTE_POINTS.map((point) => point.coordinates));
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const journey = useMemo(
    () => getMapJourney(cityIndex, typedProgress, routeCoordinates),
    [cityIndex, routeCoordinates, typedProgress],
  );

  useEffect(() => {
    let cancelled = false;
    fetch(ROUTE_DATA_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`route data ${response.status}`);
        return response.json();
      })
      .then((route) => {
        const coordinates = route?.geometry?.coordinates;
        if (!cancelled && Array.isArray(coordinates) && coordinates.length > 2) {
          setRouteCoordinates(coordinates);
        }
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return undefined;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE_URL,
      center: [103.68, 29.76],
      zoom: 7,
      minZoom: 5,
      maxZoom: 13,
      attributionControl: false,
    });
    mapRef.current = map;

    map.on("load", () => {
      map.addSource("journey-route", {
        type: "geojson",
        data: lineFeature(routeCoordinates),
      });
      map.addSource("journey-complete", { type: "geojson", data: lineFeature(journey.completed) });
      map.addSource("journey-cities", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: ROUTE_POINTS.map((point) => pointFeature(point.name, point.coordinates)),
        },
      });
      map.addSource("journey-position", {
        type: "geojson",
        data: pointFeature("当前位置", journey.position),
      });

      map.addLayer({
        id: "route-casing",
        type: "line",
        source: "journey-route",
        paint: { "line-color": "#fffdf7", "line-width": 8, "line-opacity": 0.92 },
      });
      map.addLayer({
        id: "route-line",
        type: "line",
        source: "journey-route",
        paint: { "line-color": "#565d50", "line-width": 4, "line-opacity": 0.82 },
      });
      map.addLayer({
        id: "route-complete",
        type: "line",
        source: "journey-complete",
        paint: { "line-color": "#78bd0b", "line-width": 5 },
      });
      map.addLayer({
        id: "city-points",
        type: "circle",
        source: "journey-cities",
        paint: {
          "circle-radius": 5,
          "circle-color": "#fffdf7",
          "circle-stroke-color": "#252820",
          "circle-stroke-width": 2,
        },
      });
      map.addLayer({
        id: "city-labels",
        type: "symbol",
        source: "journey-cities",
        layout: {
          "text-field": ["get", "name"],
          "text-size": 12,
          "text-offset": [0, 1.15],
          "text-anchor": "top",
          "text-allow-overlap": true,
        },
        paint: {
          "text-color": "#20231b",
          "text-halo-color": "#fffdf7",
          "text-halo-width": 1.6,
        },
      });
      map.addLayer({
        id: "current-position",
        type: "circle",
        source: "journey-position",
        paint: {
          "circle-radius": 8,
          "circle-color": "#83cb0a",
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 3,
        },
      });
      map.fitBounds(
        ROUTE_POINTS.reduce(
          (bounds, point) => bounds.extend(point.coordinates),
          new maplibregl.LngLatBounds(ROUTE_POINTS[0].coordinates, ROUTE_POINTS[0].coordinates),
        ),
        { padding: 44, duration: 0 },
      );
      setMapReady(true);
    });
    map.on("error", (event) => {
      if (!event?.error?.message?.includes("glyph")) setMapError(true);
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!mapReady || !map) return;
    map.getSource("journey-route")?.setData(lineFeature(routeCoordinates));
    map.getSource("journey-complete")?.setData(lineFeature(journey.completed));
    map.getSource("journey-position")?.setData(pointFeature("当前位置", journey.position));
  }, [journey, mapReady, routeCoordinates]);

  useEffect(() => {
    window.setTimeout(() => mapRef.current?.resize(), 220);
  }, [expanded]);

  return (
    <aside
      className={`journey-map${expanded ? " expanded" : ""}`}
      aria-label="真实道路地图"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="map-heading">
        <div>
          <MapTrifold size={18} weight="fill" aria-hidden="true" />
          <strong>真实地图</strong>
          <span>成都 → {CITIES[cityIndex].name}</span>
        </div>
        <button
          type="button"
          aria-label={expanded ? "收起地图" : "展开地图"}
          aria-pressed={expanded}
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? <ArrowsIn size={18} /> : <ArrowsOut size={18} />}
        </button>
      </div>
      <div className="map-canvas" ref={containerRef} />
      {!mapReady && !mapError ? <span className="map-status">地图载入中…</span> : null}
      {mapError ? <span className="map-status">地图暂时不可用</span> : null}
      <div className="map-attribution">
        <a href="https://openfreemap.org/" target="_blank" rel="noreferrer">OpenFreeMap</a>
        <span>·</span>
        <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap</a>
      </div>
    </aside>
  );
}

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
  const [cityIndex, setCityIndex] = useState(0);
  const [typed, setTyped] = useState("");
  const [arriving, setArriving] = useState(false);
  const [completedCities, setCompletedCities] = useState(1);
  const [soundOn, setSoundOn] = useState(true);
  const [imagePanelOpen, setImagePanelOpen] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [imageState, setImageState] = useState("loading");

  const city = CITIES[cityIndex];
  const nextCity = CITIES[(cityIndex + 1) % CITIES.length];
  const letters = useMemo(() => getDisplayLetters(city), [city]);
  const journeyProgress = Math.min(
    100,
    ((completedCities - 1 + typed.length / city.pinyin.length) / (ROUTE_CITY_COUNT - 1)) * 100,
  );
  const typedProgress = typed.length / city.pinyin.length;

  useEffect(() => {
    inputRef.current?.focus();
    return () => window.clearTimeout(arrivalTimerRef.current);
  }, []);

  useEffect(() => {
    if (typed !== city.pinyin || arriving) return;
    setArriving(true);
    setCompletedCities((value) => Math.min(value + 1, ROUTE_CITY_COUNT));
    arrivalTimerRef.current = window.setTimeout(() => {
      setCityIndex((value) => (value + 1) % CITIES.length);
      setTyped("");
      setArriving(false);
      inputRef.current?.focus();
    }, 920);
  }, [arriving, city.pinyin, typed]);

  function handleInput(event) {
    const normalized = event.target.value.toLowerCase().replace(/[^a-z]/g, "");
    if (arriving) return;
    if (city.pinyin.startsWith(normalized)) {
      setTyped(normalized.slice(0, city.pinyin.length));
    } else {
      event.target.value = typed;
    }
  }

  function resetJourney() {
    window.clearTimeout(arrivalTimerRef.current);
    setCityIndex(0);
    setTyped("");
    setArriving(false);
    setCompletedCities(1);
    setImagePanelOpen(false);
    inputRef.current?.focus();
  }

  return (
    <main className={`journey-app${focusMode ? " focus-mode" : ""}`} onClick={() => inputRef.current?.focus()}>
      <input
        ref={inputRef}
        className="typing-capture"
        value={typed}
        onChange={handleInput}
        aria-label={`输入 ${city.name} 的拼音`}
        autoCapitalize="none"
        autoComplete="off"
        spellCheck="false"
      />

      <header className="topbar">
        <button className="back-button" type="button" aria-label="返回" onClick={resetJourney}>
          <ArrowLeft size={22} weight="regular" aria-hidden="true" />
          <span>返回</span>
        </button>

        <div className="route-name" aria-label="当前路线 川南城市线 成都到宜宾">
          <strong>川南城市线</strong>
          <span>·</span>
          <span>成都</span>
          <ArrowRight size={17} weight="regular" aria-hidden="true" />
          <span>宜宾</span>
        </div>

        <div className="route-count" aria-live="polite">
          <strong>{completedCities}</strong>
          <span>/ {ROUTE_CITY_COUNT} 城</span>
        </div>

        <div className="top-actions">
          <button
            className="icon-button"
            type="button"
            aria-label={soundOn ? "关闭声音" : "开启声音"}
            aria-pressed={!soundOn}
            onClick={() => setSoundOn((value) => !value)}
          >
            {soundOn ? <SpeakerHigh size={22} /> : <SpeakerSlash size={22} />}
          </button>
          <div className="image-control">
            <button
              className="image-button"
              type="button"
              aria-label="实景图片设置"
              aria-expanded={imagePanelOpen}
              onClick={() => setImagePanelOpen((value) => !value)}
            >
              <ImageSquare size={22} aria-hidden="true" />
              <span>实景</span>
              <CaretDown size={14} aria-hidden="true" />
            </button>
            {imagePanelOpen ? (
              <div className="image-popover" role="dialog" aria-label="实景图片设置">
                <div className="popover-heading">
                  <div>
                    <strong>碧峰峡路上 · 雅安</strong>
                    <span>真实摄影 · 2010</span>
                  </div>
                  <button type="button" aria-label="关闭图片设置" onClick={() => setImagePanelOpen(false)}>
                    <X size={17} />
                  </button>
                </div>
                <button
                  className="focus-toggle"
                  type="button"
                  aria-pressed={focusMode}
                  onClick={() => setFocusMode((value) => !value)}
                >
                  <span>低干扰显示</span>
                  <span className="switch-track" aria-hidden="true"><span /></span>
                </button>
                <p>
                  摄影：zhanyoun · CC BY-SA 3.0<br />
                  <a
                    href="https://commons.wikimedia.org/wiki/File:%E7%A2%A7%E5%B3%B0%E5%B3%A1%E8%B7%AF%E4%B8%8A_-_panoramio.jpg"
                    target="_blank"
                    rel="noreferrer"
                  >查看原图与授权</a>
                </p>
              </div>
            ) : null}
          </div>
        </div>
      </header>

      <section className="scenic-stage" aria-label="成都至雅安沿途实景">
        <img
          className="scenic-image"
          src="/assets/yaan-bifengxia-road.jpg"
          alt="雅安碧峰峡道路穿过林木和陡峭岩壁，远处有车辆行驶"
          onLoad={() => setImageState("loaded")}
          onError={() => setImageState("error")}
        />
        <div className="scenic-vignette" aria-hidden="true" />
        {imageState === "loading" ? <p className="image-status">实景载入中…</p> : null}
        {imageState === "error" ? <p className="image-status">实景暂时不可用，打字旅程仍可继续。</p> : null}

        <JourneyMap cityIndex={cityIndex} typedProgress={typedProgress} />

        <div
          className="route-progress"
          role="progressbar"
          aria-valuemin="0"
          aria-valuemax="100"
          aria-valuenow={Math.round(journeyProgress)}
          aria-label={`路线完成 ${Math.round(journeyProgress)}%`}
          style={{ "--route-progress": `${journeyProgress}%` }}
        >
          <img className="route-trace route-trace-base" src="/assets/route-trace-light.png" alt="" />
          <img className="route-trace route-trace-fill" src="/assets/route-trace-green.png" alt="" />
          <span className="vehicle-position" style={{ left: `${journeyProgress}%` }} aria-hidden="true">
            <CarProfile size={18} weight="fill" />
          </span>
        </div>

        <section className={`typing-dock${arriving ? " arrived" : ""}`} aria-live="polite">
          <div className="destination-block">
            <span>{arriving ? "已经抵达" : "正在前往"}</span>
            <strong>{city.name}</strong>
          </div>

          <div className="pinyin-block" aria-label={`${city.name}，${city.syllables.join(" ")}`}>
            <div className="pinyin-letters" aria-hidden="true">
              {letters.map((letter) => {
                if (letter.value === " ") return <span className="letter-space" key={letter.key}> </span>;
                const letterIndex = letters.slice(0, letters.indexOf(letter)).filter((item) => item.value !== " ").length;
                const state = letterIndex < typed.length ? "typed" : letterIndex === typed.length ? "active" : "pending";
                return <span className={state} key={letter.key}>{letter.value}</span>;
              })}
            </div>
            <p>{arriving ? `${city.name}已点亮，准备前往${nextCity.name}` : "输入拼音，抵达下一城"}</p>
          </div>

          <div className="next-block">
            <span>下一城</span>
            <strong>{nextCity.name}</strong>
            <ArrowRight size={28} weight="regular" aria-hidden="true" />
          </div>
        </section>
      </section>
    </main>
  );
}
