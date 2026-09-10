import { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import maplibregl from "maplibre-gl";
import {
  ArrowsIn,
  ArrowsOut,
  CarProfile,
  Cube,
  MapTrifold,
  Mountains,
} from "@phosphor-icons/react";
import { CITIES, ROUTE_DATA_URL, ROUTE_POINTS } from "../data/journey";
import { MAP_EVENTS } from "../data/levels";
import {
  buildRouteNodeGeoJson,
  getJourneyCursor,
  getRouteJourney,
  lineFeature,
} from "../lib/routeJourney";

const MAP_STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
const TERRAIN_URL = "https://tiles.mapterhorn.com/tilejson.json";
const SATELLITE_TILES =
  "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2025_3857/default/g/{z}/{y}/{x}.jpg";

function styleTerrainBasemap(map) {
  const paint = (layerId, property, value) => {
    if (map.getLayer(layerId)) map.setPaintProperty(layerId, property, value);
  };

  paint("background", "background-color", "#26382a");
  paint("natural_earth", "raster-opacity", 1);
  paint("natural_earth", "raster-saturation", -0.08);
  paint("natural_earth", "raster-contrast", 0.2);
  paint("natural_earth", "raster-brightness-min", 0.08);
  paint("natural_earth", "raster-brightness-max", 0.7);
  paint("water", "fill-color", "#416d73");
  paint("water", "fill-opacity", 0.78);
  paint("park", "fill-color", "#486344");
  paint("park", "fill-opacity", 0.66);
  paint("landcover_wood", "fill-color", "#38513b");
  paint("landcover_wood", "fill-opacity", 0.74);
  paint("landcover_grass", "fill-color", "#60704c");
  paint("landcover_grass", "fill-opacity", 0.52);
  paint("landuse_residential", "fill-color", "#7d765f");
  paint("landuse_residential", "fill-opacity", 0.26);

  ["road_motorway", "road_trunk_primary", "road_secondary_tertiary"].forEach((id) => {
    paint(id, "line-color", id === "road_motorway" ? "#e0b66d" : "#d8d0b5");
    paint(id, "line-opacity", 0.9);
  });
  ["road_motorway_casing", "road_trunk_primary_casing", "road_secondary_tertiary_casing"].forEach((id) => {
    paint(id, "line-color", "#3b3328");
    paint(id, "line-opacity", 0.78);
  });
}

function addTerrain(map) {
  const firstLabel = map
    .getStyle()
    .layers.find((layer) => layer.type === "symbol" && layer.layout?.["text-field"]);

  map.addSource("sentinel-imagery", {
    type: "raster",
    tiles: [SATELLITE_TILES],
    tileSize: 256,
    maxzoom: 14,
    attribution: "EOxCloudless © EOX IT Services GmbH · modified Copernicus Sentinel data 2025",
  });
  map.addLayer(
    {
      id: "sentinel-imagery",
      type: "raster",
      source: "sentinel-imagery",
      paint: {
        "raster-opacity": 0.93,
        "raster-saturation": -0.08,
        "raster-contrast": 0.16,
        "raster-brightness-min": 0.05,
        "raster-brightness-max": 0.82,
      },
    },
    firstLabel?.id,
  );

  map.addSource("terrain-dem", {
    type: "raster-dem",
    url: TERRAIN_URL,
    tileSize: 256,
  });
  map.addSource("hillshade-dem", {
    type: "raster-dem",
    url: TERRAIN_URL,
    tileSize: 256,
  });
  map.setTerrain({ source: "terrain-dem", exaggeration: 1.18 });
  map.addLayer(
    {
      id: "terrain-hillshade",
      type: "hillshade",
      source: "hillshade-dem",
      paint: {
        "hillshade-shadow-color": "#101810",
        "hillshade-highlight-color": "#d5dfc8",
        "hillshade-accent-color": "#1d2b20",
        "hillshade-exaggeration": 0.5,
      },
    },
    firstLabel?.id,
  );
}

function addJourneyLayers(map, routeCoordinates, journey, nodes) {
  map.addSource("journey-route", { type: "geojson", data: lineFeature(routeCoordinates) });
  map.addSource("journey-progress", { type: "geojson", data: lineFeature(journey.completed) });
  map.addSource("journey-nodes", { type: "geojson", data: nodes });

  map.addLayer({
    id: "route-shadow",
    type: "line",
    source: "journey-route",
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": "#12150f", "line-width": 13, "line-opacity": 0.66, "line-blur": 2 },
  });
  map.addLayer({
    id: "route-casing",
    type: "line",
    source: "journey-route",
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": "#fffdf7", "line-width": 8.5, "line-opacity": 0.96 },
  });
  map.addLayer({
    id: "route-line",
    type: "line",
    source: "journey-route",
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": "#6f776a", "line-width": 3.5, "line-opacity": 0.88 },
  });
  map.addLayer({
    id: "route-progress",
    type: "line",
    source: "journey-progress",
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": "#8bd11b", "line-width": 5.5 },
  });
  map.addLayer({
    id: "route-nodes",
    type: "circle",
    source: "journey-nodes",
    paint: {
      "circle-radius": ["match", ["get", "state"], "current", 9, "arrived", 9, 7],
      "circle-color": [
        "match",
        ["get", "state"],
        "passed", "#8bd11b",
        "arrived", "#8bd11b",
        "current", "#fffdf7",
        "#c6c9c0",
      ],
      "circle-stroke-color": ["match", ["get", "state"], "current", "#8bd11b", "#fffdf7"],
      "circle-stroke-width": 3,
    },
  });
  map.addLayer({
    id: "route-node-labels",
    type: "symbol",
    source: "journey-nodes",
    layout: {
      "text-field": ["get", "name"],
      "text-size": 15,
      "text-offset": [0, -1.35],
      "text-anchor": "bottom",
      "text-allow-overlap": true,
    },
    paint: {
      "text-color": "#fffdf7",
      "text-halo-color": "#171b15",
      "text-halo-width": 3,
    },
  });
}

export function JourneyMap({
  cityIndex,
  typedProgress,
  arriving,
  is3d,
  onToggle3d,
  fullscreen,
  onToggleFullscreen,
  hiddenRouteUnlocked,
}) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const markerRef = useRef(null);
  const markerRootRef = useRef(null);
  const eventMarkersRef = useRef([]);
  const [routeCoordinates, setRouteCoordinates] = useState(ROUTE_POINTS.map((point) => point.coordinates));
  const [mapReady, setMapReady] = useState(false);
  const [mapError, setMapError] = useState(false);
  const cursor = getJourneyCursor(cityIndex, typedProgress);
  const journey = useMemo(
    () => getRouteJourney(routeCoordinates, ROUTE_POINTS, cursor),
    [cursor, routeCoordinates],
  );
  const nodes = useMemo(
    () => buildRouteNodeGeoJson(ROUTE_POINTS, cursor, arriving),
    [arriving, cursor],
  );

  useEffect(() => {
    let cancelled = false;
    fetch(ROUTE_DATA_URL)
      .then((response) => {
        if (!response.ok) throw new Error(`route data ${response.status}`);
        return response.json();
      })
      .then((route) => {
        if (!cancelled && route?.geometry?.coordinates?.length > 2) {
          setRouteCoordinates(route.geometry.coordinates);
        }
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return undefined;
    const initialJourney = getRouteJourney(routeCoordinates, ROUTE_POINTS, cursor);
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE_URL,
      center: [103.78, 29.69],
      zoom: 6.75,
      pitch: 48,
      bearing: -12,
      minZoom: 5,
      maxZoom: 17,
      maxPitch: 75,
      attributionControl: false,
      renderWorldCopies: false,
      canvasContextAttributes: { antialias: true },
    });
    mapRef.current = map;

    map.once("load", () => {
      styleTerrainBasemap(map);
      addTerrain(map);
      addJourneyLayers(
        map,
        routeCoordinates,
        initialJourney,
        buildRouteNodeGeoJson(ROUTE_POINTS, cursor, arriving),
      );

      const carElement = document.createElement("div");
      carElement.className = "map-car-marker";
      carElement.setAttribute("aria-label", "旅行车辆当前位置");
      const carRoot = createRoot(carElement);
      carRoot.render(<CarProfile size={25} weight="fill" aria-hidden="true" />);
      markerRef.current = new maplibregl.Marker({
        element: carElement,
        anchor: "center",
        rotationAlignment: "map",
        pitchAlignment: "viewport",
      })
        .setLngLat(initialJourney.position)
        .setRotation(initialJourney.bearing)
        .addTo(map);
      markerRootRef.current = carRoot;

      eventMarkersRef.current = MAP_EVENTS.map((event) => {
        const element = document.createElement("div");
        element.className = `event-map-marker ${event.color}${event.id === "hidden-stamp" ? " hidden-event" : ""}`;
        element.title = event.label;
        element.dataset.eventId = event.id;
        const root = createRoot(element);
        const Icon = event.icon;
        root.render(<Icon size={21} weight="fill" aria-hidden="true" />);
        const marker = new maplibregl.Marker({ element, anchor: "bottom" })
          .setLngLat(event.coordinates)
          .addTo(map);
        return { element, marker, root };
      });

      setMapReady(true);
    });
    map.once("error", () => {
      if (!map.loaded()) setMapError(true);
    });

    const resizeObserver = new ResizeObserver(() => map.resize());
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      markerRef.current?.remove();
      markerRootRef.current?.unmount();
      eventMarkersRef.current.forEach(({ marker, root }) => {
        marker.remove();
        root.unmount();
      });
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!mapReady || !map) return;
    map.getSource("journey-route")?.setData(lineFeature(routeCoordinates));
    map.getSource("journey-progress")?.setData(lineFeature(journey.completed));
    map.getSource("journey-nodes")?.setData(nodes);
    markerRef.current?.setLngLat(journey.position).setRotation(journey.bearing);
  }, [journey, mapReady, nodes, routeCoordinates]);

  useEffect(() => {
    const map = mapRef.current;
    if (!mapReady || !map) return;
    map.setTerrain(is3d ? { source: "terrain-dem", exaggeration: 1.18 } : null);
    map.easeTo({ pitch: is3d ? 48 : 0, bearing: is3d ? -12 : 0, duration: 520 });
  }, [is3d, mapReady]);

  useEffect(() => {
    const hiddenMarker = eventMarkersRef.current.find(
      ({ element }) => element.dataset.eventId === "hidden-stamp",
    );
    hiddenMarker?.element.classList.toggle("unlocked", hiddenRouteUnlocked);
  }, [hiddenRouteUnlocked, mapReady]);

  useEffect(() => {
    window.setTimeout(() => mapRef.current?.resize(), 180);
  }, [fullscreen]);

  return (
    <div className="journey-map" aria-label="真实卫星三维地形道路地图" onClick={(event) => event.stopPropagation()}>
      <div className="map-canvas" ref={containerRef} />
      {!mapReady && !mapError ? <span className="map-status">真实卫星地形地图载入中…</span> : null}
      {mapError ? <span className="map-status">地图暂时不可用</span> : null}

      <div className="map-controls" aria-label="地图显示控制">
        <button type="button" className="active" aria-pressed="true">
          <Mountains size={18} />真实地形
        </button>
        <button type="button" aria-pressed={is3d} onClick={onToggle3d}>
          <Cube size={18} />{is3d ? "2D 地图" : "3D 地形"}
        </button>
        <button type="button" aria-pressed={fullscreen} onClick={onToggleFullscreen}>
          {fullscreen ? <ArrowsIn size={18} /> : <ArrowsOut size={18} />}
          {fullscreen ? "退出全屏" : "全屏"}
        </button>
      </div>

      <div className="map-attribution">
        <MapTrifold size={12} weight="fill" />
        <a href="https://cloudless.eox.at/" target="_blank" rel="noreferrer">EOxCloudless / Copernicus</a>
        <span>·</span>
        <a href="https://openfreemap.org/" target="_blank" rel="noreferrer">OpenFreeMap</a>
        <span>·</span>
        <a href="https://mapterhorn.com/" target="_blank" rel="noreferrer">Mapterhorn</a>
      </div>

      <span className="map-route-caption">川南城市线 · 成都 → {CITIES[cityIndex].name}</span>
    </div>
  );
}
