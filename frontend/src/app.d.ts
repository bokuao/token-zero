/// <reference types="svelte" />
/// <reference types="vite/client" />

// Svelte 5 onclick event handler
declare namespace svelteHTML {
  interface HTMLAttributes<T> {
    onclick?: (event: MouseEvent) => void;
    onkeydown?: (event: KeyboardEvent) => void;
    oninput?: (event: Event) => void;
  }
}
