declare module "plotly.js-dist-min" {
  export function newPlot(
    root: HTMLElement,
    data: object[],
    layout?: object,
    config?: object
  ): Promise<void>;
  export function purge(root: HTMLElement): void;
}
