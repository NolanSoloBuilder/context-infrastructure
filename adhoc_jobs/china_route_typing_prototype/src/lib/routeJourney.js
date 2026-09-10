function clamp(value, minimum, maximum) {
  return Math.min(Math.max(value, minimum), maximum);
}

export function lineFeature(coordinates, properties = {}) {
  return {
    type: "Feature",
    properties,
    geometry: { type: "LineString", coordinates },
  };
}

export function featureCollection(features = []) {
  return { type: "FeatureCollection", features };
}

export function nearestCoordinateIndex(coordinates, target) {
  let result = 0;
  let smallestDistance = Number.POSITIVE_INFINITY;
  coordinates.forEach((coordinate, index) => {
    const distance =
      (coordinate[0] - target[0]) ** 2 +
      (coordinate[1] - target[1]) ** 2;
    if (distance < smallestDistance) {
      smallestDistance = distance;
      result = index;
    }
  });
  return result;
}

export function getJourneyCursor(cityIndex, typedProgress) {
  return Math.max(cityIndex, 0) + clamp(typedProgress, 0, 1);
}

export function getRouteJourney(routeCoordinates, routePoints, journeyCursor) {
  const maximumSegment = Math.max(routePoints.length - 2, 0);
  const cursor = clamp(journeyCursor, 0, routePoints.length - 1);
  const segmentIndex = Math.min(Math.floor(cursor), maximumSegment);
  const segmentProgress = cursor - segmentIndex;
  const startIndex = nearestCoordinateIndex(
    routeCoordinates,
    routePoints[segmentIndex].coordinates,
  );
  const endIndex = nearestCoordinateIndex(
    routeCoordinates,
    routePoints[segmentIndex + 1].coordinates,
  );
  const routePosition =
    startIndex + Math.max(0, endIndex - startIndex) * segmentProgress;
  const lowerIndex = Math.floor(routePosition);
  const upperIndex = Math.min(
    Math.ceil(routePosition),
    routeCoordinates.length - 1,
  );
  const fraction = routePosition - lowerIndex;
  const start = routeCoordinates[lowerIndex];
  const end = routeCoordinates[upperIndex];
  const position = [
    start[0] + (end[0] - start[0]) * fraction,
    start[1] + (end[1] - start[1]) * fraction,
  ];
  const bearing =
    Math.atan2(end[0] - start[0], end[1] - start[1]) * (180 / Math.PI);

  return {
    bearing,
    completed: [...routeCoordinates.slice(0, lowerIndex + 1), position],
    position,
    segmentIndex,
    segmentProgress,
    startRouteIndex: startIndex,
    endRouteIndex: endIndex,
  };
}

export function buildRouteNodeGeoJson(routePoints, journeyCursor, arriving) {
  const currentDestination = Math.min(
    Math.ceil(journeyCursor + 0.000001),
    routePoints.length - 1,
  );
  return featureCollection(
    routePoints.map((point, index) => {
      const state =
        arriving && index === currentDestination
          ? "arrived"
          : index < currentDestination
            ? "passed"
            : index === currentDestination
              ? "current"
              : index === currentDestination + 1
                ? "next"
                : "idle";
      return {
        type: "Feature",
        properties: { index, name: point.name, state },
        geometry: { type: "Point", coordinates: point.coordinates },
      };
    }),
  );
}

export function getSegmentCoordinates(routeCoordinates, journey) {
  return routeCoordinates.slice(
    Math.min(journey.startRouteIndex, journey.endRouteIndex),
    Math.max(journey.startRouteIndex, journey.endRouteIndex) + 1,
  );
}
