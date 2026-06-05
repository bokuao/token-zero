<script lang="ts">
  import { onMount } from "svelte";
  import { link } from "svelte-spa-router";
  import { capClass } from "../lib/utils";
  import { api, type ModelDetail, type ConfigResult } from "../lib/api";

  export let params: { id: string };

  let model: ModelDetail | null = null;
  let loading = true;
  let error = "";
  let health: { healthy: boolean } | null = null;

  const agents = [
    { id: "cline", name: "Cline", logo: "https://cdn.simpleicons.org/cline" },
    { id: "opencode", name: "opencode", logo: "" },
    { id: "hermes", name: "Hermes", logo: "" },
    { id: "openclaw", name: "OpenClaw", logo: "" },
    { id: "pi", name: "Pi", logo: "" },
    { id: "kilo", name: "Kilo Code", logo: "" },
    { id: "roocode", name: "RooCode", logo: "" },
  ];

  let selectedAgent = "hermes";
  let config: ConfigResult | null = null;
  let configLoading = false;
  let copied = false;

  onMount(async () => {
    try {
      model = await api.getModel(Number(params.id));
      if (model.provider?.id) {
        health = await api.getProviderHealth(model.provider.id);
      }
      await loadConfig();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function loadConfig() {
    if (!model) return;
    configLoading = true;
    try {
      config = await api.getConfig(selectedAgent, model.id);
    } catch {
      config = null;
    } finally {
      configLoading = false;
    }
  }

  async function onAgentChange(agentId: string) {
    selectedAgent = agentId;
    copied = false;
    (window as any).umami?.track("agent-select", { agent: agentId });
    await loadConfig();
  }

  async function copyConfig() {
    if (!config || !model) return;
    await navigator.clipboard.writeText(config.content);
    copied = true;
    setTimeout(() => (copied = false), 2000);
    (window as any).umami?.track("config-copy", {
      agent: selectedAgent,
      model: model.model_id,
    });
  }

  function downloadConfig() {
    if (!config || !model) return;
    const blob = new Blob([config.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = config.filename;
    a.click();
    URL.revokeObjectURL(url);
    (window as any).umami?.track("config-download", {
      agent: selectedAgent,
      model: model.model_id,
    });
  }

  function fmtNum(n: number): string {
    if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
    if (n >= 1_000) return (n / 1_000).toFixed(0) + "K";
    return String(n);
  }
</script>

<div>
  <a
    href="/"
    use:link
    class="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
  >
    ← Back
  </a>

  {#if loading}
    <div class="flex items-center justify-center py-20">
      <p class="text-muted-foreground animate-pulse">Loading...</p>
    </div>
  {:else if error}
    <div class="text-center py-20">
      <p class="text-red-500">{error}</p>
    </div>
  {:else if model}
    <!-- Header -->
    <div class="mb-10 space-y-4">
      <h1 class="text-3xl font-bold tracking-tight">{model.display_name}</h1>
      <p class="text-sm text-muted-foreground font-mono">{model.model_id}</p>

      <div class="flex flex-wrap items-center gap-3 text-sm">
        <span class="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1">
          <span class="text-base">🏢</span> {model.provider.name}
        </span>
        {#if model.provider.base_url}
          <span class="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1 text-xs font-mono">
            {#if health}
              <span class="inline-block w-2 h-2 rounded-full {health.healthy ? 'bg-green-500' : 'bg-red-500'}"></span>
            {/if}
            {model.provider.base_url}
          </span>
        {/if}
        <span class="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1">
          <span class="font-medium">{fmtNum(model.context_length)}</span> ctx
        </span>
        {#if model.max_output}
          <span class="inline-flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1">
            <span class="font-medium">{fmtNum(model.max_output)}</span> max out
          </span>
        {/if}
        <span class="inline-flex items-center gap-1.5 rounded-md bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300 px-3 py-1 font-semibold">
          🆓 $0
        </span>
      </div>

      <div class="flex flex-wrap gap-1.5">
        {#each model.capabilities.filter(c => c !== 'text') as cap}
          <span class="inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-medium {capClass(cap)}">
            {cap}
          </span>
        {/each}
      </div>

      {#if model.description}
        <p class="text-sm text-muted-foreground leading-relaxed">{model.description}</p>
      {/if}
      {#if model.rate_limits}
        <p class="text-xs text-muted-foreground">⏱ Rate limit: {model.rate_limits}</p>
      {/if}
    </div>

    <!-- Config Generator -->
    <div class="rounded-lg border bg-card shadow-sm p-6 space-y-5">
      <h2 class="font-semibold text-lg">📋 Choose your agent</h2>

      <!-- Agent tabs -->
      <div class="flex flex-wrap gap-2">
        {#each agents as a}
          <button
            class="inline-flex items-center rounded-md px-3 py-1.5 text-sm font-medium transition-colors
                   {selectedAgent === a.id
                     ? 'bg-primary text-primary-foreground shadow'
                     : 'border hover:bg-accent'}"
            onclick={() => onAgentChange(a.id)}
          >
            {#if a.logo}
              <img src={a.logo} alt="" class="w-4 h-4 rounded-sm mr-1.5" />
            {/if}
            {a.name}
          </button>
        {/each}
      </div>

      <!-- Config output -->
      {#if configLoading}
        <p class="text-sm text-muted-foreground animate-pulse">Generating config...</p>
      {:else if config}
        <div class="space-y-3">
          <pre class="bg-secondary/50 rounded-md border p-4 text-xs overflow-x-auto leading-relaxed"><code>{config.content}</code></pre>
          {#if config.paths && Object.keys(config.paths).length > 0}
            <div class="rounded-md border p-3 space-y-1 text-xs">
              <p class="font-medium text-muted-foreground mb-1">📁 Install location:</p>
              {#each Object.entries(config.paths) as [os, path]}
                <div class="flex gap-2">
                  <span class="font-medium w-16 text-muted-foreground">{os}</span>
                  <code class="text-xs">{path}</code>
                </div>
              {/each}
            </div>
          {/if}
          <div class="flex gap-2">
            <button
              class="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
              onclick={copyConfig}
            >
              {copied ? "✓ Copied!" : "📋 Copy"}
            </button>
            <button
              class="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
              onclick={downloadConfig}
            >
              ⬇ Download .{config.format}
            </button>
          </div>
        </div>
      {:else}
        <p class="text-sm text-yellow-600 dark:text-yellow-400">Config not available for this agent.</p>
      {/if}
    </div>
  {/if}
</div>
