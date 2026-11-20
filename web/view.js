/** @typedef {import("./protocol").Point} Point */

/** @param {number} n @param {number} precision */
export function formatNumber(n, precision) {
  if (n !== 0 && (Math.abs(n) >= 1e8 || Math.abs(n) < 10 ** -precision)) {
    return n.toExponential(precision);
  }
  return n.toFixed(precision);
}

/**
 * @param {HTMLCanvasElement} canvas
 * @param {import("./protocol").Result} result
 * @param {string} layers
 */
export function draw(canvas, [, , curve, edges, heights], layers) {
  const context = canvas.getContext("2d");
  if (!context) return;
  const { width, height } = canvas.getBoundingClientRect();
  if (width === 0 || height === 0) return;
  const backingWidth = Math.round(width * devicePixelRatio);
  const backingHeight = Math.round(height * devicePixelRatio);
  if (canvas.width !== backingWidth) canvas.width = backingWidth;
  if (canvas.height !== backingHeight) canvas.height = backingHeight;
  context.setTransform(backingWidth / width, 0, 0, backingHeight / height, 0, 0);

  const horizontal = [edges[0][0], edges[edges.length - 1][0]];
  const xMin = Math.min(...horizontal);
  const xMax = Math.max(...horizontal);
  const values = [...curve.map(([, y]) => y), ...edges.map(([, y]) => y), ...heights];
  const magnitude = Math.max(1e-300, Math.abs(Math.min(...values)), Math.abs(Math.max(...values)));
  const yMin = Math.min(...values, 0) / magnitude;
  const yMax = Math.max(...values, 0) / magnitude;
  const xPadding = Math.min(42, width / 4);
  const yPadding = Math.min(30, height / 4);
  const w = width - 2 * xPadding;
  const h = height - 2 * yPadding;
  /** @param {number} value */
  const xPixel = value => xPadding + (xMax === xMin ? 0.5 : (value - xMin) / (xMax - xMin)) * w;
  /** @param {number} value */
  const yPixel = value => yPadding + (yMax === yMin ? 0.5 : (yMax - value / magnitude) / (yMax - yMin)) * h;

  context.fillStyle = "#000";
  context.fillRect(0, 0, width, height);
  context.lineWidth = 1;
  context.strokeStyle = "#334257";
  context.beginPath();
  context.moveTo(xPadding, yPixel(0));
  context.lineTo(xPadding + w, yPixel(0));
  if (xMin < 0 && xMax > 0) {
    context.moveTo(xPixel(0), yPadding);
    context.lineTo(xPixel(0), yPadding + h);
  }
  context.stroke();

  /**
   * @param {Point[]} points
   * @param {string} stroke
   * @param {string} fill
   */
  function polygon(points, stroke, fill) {
    if (!context) return;
    context.beginPath();
    context.moveTo(xPixel(points[0][0]), yPixel(points[0][1]));
    for (const [x, y] of points.slice(1)) context.lineTo(xPixel(x), yPixel(y));
    context.closePath();
    context.fillStyle = fill;
    context.fill();
    context.strokeStyle = stroke;
    context.stroke();
  }

  for (let panel = 0; panel < heights.length; panel++) {
    const [left, leftY] = edges[panel];
    const [right, rightY] = edges[panel + 1];
    const midY = heights[panel];
    if (layers !== "trapezoids") {
      polygon([[left, 0], [left, midY], [right, midY], [right, 0]], "#f5c65e", "#f5c65e22");
    }
    if (layers !== "rectangles") {
      polygon([[left, 0], [left, leftY], [right, rightY], [right, 0]], "#ff7777", "#ff777722");
    }
  }

  context.beginPath();
  context.moveTo(xPixel(curve[0][0]), yPixel(curve[0][1]));
  for (const [x, y] of curve.slice(1)) context.lineTo(xPixel(x), yPixel(y));
  context.lineWidth = 2.5;
  context.strokeStyle = "#79baff";
  context.stroke();

  context.font = "12px system-ui, sans-serif";
  context.fillStyle = "#c6d4df";
  context.textAlign = "center";
  const xTicks = xMin === xMax ? [xMin] : [xMin, xMin + (xMax - xMin) / 2, xMax];
  for (const tick of xTicks) {
    context.fillText(formatNumber(tick, 2), xPixel(tick), height - 10);
  }
  context.textAlign = "left";
  context.fillText(formatNumber(yMax * magnitude, 2), 8, 18);
  if (yMin !== yMax) context.fillText(formatNumber(yMin * magnitude, 2), 8, height - yPadding + 5);
}
