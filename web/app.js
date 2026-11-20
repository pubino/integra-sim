import { draw, formatNumber } from "./view.js";

/**
 * @template {Element} T
 * @param {string} id
 * @param {{new(): T}} constructor
 */
function find(id, constructor) {
  const element = document.getElementById(id);
  if (!(element instanceof constructor)) throw new Error(`Missing element ${id}`);
  return element;
}

const inputs = find("inputs", HTMLFieldSetElement);
const submit = find("integrate", HTMLButtonElement);
const layers = find("layers", HTMLSelectElement);
const status = find("status", HTMLElement);
const error = find("error", HTMLElement);
const loading = find("loading", HTMLElement);
const retry = find("retry", HTMLButtonElement);
const canvas = find("plot", HTMLCanvasElement);
const midpoint = find("midpoint", HTMLElement);
const trapezoid = find("trapezoid", HTMLElement);

const worker = new Worker(new URL("./worker.js", import.meta.url));
let generation = 0;
/** @type {import("./protocol").Result | undefined} */
let lastResult;

/** @param {import("./protocol").Request} request */
function send(request) {
  worker.postMessage(request);
}

function calculate() {
  generation++;
  error.hidden = true;
  const form = find("settings", HTMLFormElement);
  if (!form.reportValidity()) {
    submit.disabled = false;
    status.textContent = "Correct the highlighted field.";
    return;
  }
  status.textContent = "Calculating…";
  submit.disabled = true;
  send({
    id: generation,
    parameters: Array.from(inputs.querySelectorAll("input"), input => input.valueAsNumber),
  });
}

function showFatal() {
  worker.terminate();
  inputs.disabled = true;
  submit.disabled = true;
  status.textContent = "";
  loading.textContent = "Calculation unavailable";
  error.textContent = "Python could not load. Reload to try again.";
  error.hidden = false;
  retry.hidden = false;
}

worker.onerror = showFatal;
worker.onmessage = (/** @type {MessageEvent<import("./protocol").Reply>} */ { data }) => {
  if (data.type === "ready") {
    inputs.disabled = false;
    calculate();
    return;
  }
  if (data.type === "fatal") {
    showFatal();
    return;
  }
  if (!("id" in data) || generation !== data.id) return;
  loading.hidden = true;
  submit.disabled = false;
  if (data.type === "error") {
    status.textContent = "";
    error.textContent = data.message;
    error.hidden = false;
    return;
  }
  lastResult = data.result;
  redraw();
  midpoint.textContent = formatNumber(lastResult[0], 6);
  trapezoid.textContent = formatNumber(lastResult[1], 6);
  status.textContent = "Calculated.";
};

find("settings", HTMLFormElement).addEventListener("submit", (event) => {
  event.preventDefault();
  calculate();
});
function redraw() {
  if (lastResult) draw(canvas, lastResult, layers.value);
}

layers.addEventListener("change", redraw);
new ResizeObserver(redraw).observe(canvas);
retry.addEventListener("click", () => window.location.reload());
