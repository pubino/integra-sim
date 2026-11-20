export type Point = [x: number, y: number];
export type Result = [midpoint: number, trapezoid: number, curve: Point[], edges: Point[], heights: number[]];
export type Request = { id: number; parameters: number[] };
export type Reply =
  | { type: "ready" | "fatal" }
  | { type: "result"; id: number; result: Result }
  | { type: "error"; id: number; message: string };
export interface WorkerScope {
  importScripts(url: string): void;
  location: Location;
  loadPyodide(options: { indexURL: string }): Promise<{
    FS: { writeFile(path: string, contents: string): void };
    runPython(code: string): (parameters: string) => {
      toJs(options: { create_pyproxies: false }): Result;
      destroy(): void;
    };
  }>;
  onmessage: (event: MessageEvent<Request>) => void;
  postMessage(message: Reply): void;
}
