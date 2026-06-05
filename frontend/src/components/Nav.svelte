<script lang="ts">
  import { link } from "svelte-spa-router";

  let dark = $state(false);

  $effect(() => {
    const saved = localStorage.getItem("theme");
    dark = saved === "dark" || (!saved && window.matchMedia("(prefers-color-scheme: dark)").matches);
  });

  $effect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  });

  function toggleTheme() {
    dark = !dark;
  }
</script>

<nav class="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div class="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between">
    <a href="/" use:link class="inline-flex items-center gap-1.5 text-lg font-bold tracking-tight hover:opacity-80 transition-opacity">
      <span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-linear-to-br from-zinc-800 to-zinc-950 dark:from-zinc-200 dark:to-white text-white dark:text-zinc-900 text-xs font-black tracking-tighter shadow-sm ring-1 ring-zinc-200 dark:ring-zinc-700">T0</span>
      Token Zero
    </a>
    <div class="flex items-center gap-4">
      <button
        onclick={toggleTheme}
        class="inline-flex items-center justify-center rounded-md h-8 w-8 text-sm hover:bg-accent transition-colors"
        aria-label="Toggle theme"
      >
        {dark ? "☀️" : "🌙"}
      </button>
      <span class="text-sm text-muted-foreground">token-0.com</span>
    </div>
  </div>
</nav>
