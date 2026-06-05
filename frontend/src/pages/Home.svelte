<script lang="ts">
    import { onMount } from "svelte";
    import { link } from "svelte-spa-router";
    import {
        api,
        type Provider,
        type ProviderModel,
        type ConfigResult,
    } from "../lib/api";
    import { capClass } from "../lib/utils";

    let providers: Provider[] = [];
    let totalModels = 0;
    let loading = true;
    let error = "";
    let expanded: Record<string, boolean> = {};
    let search = "";
    let health: Record<string, boolean> = {};
    let sortNewest = true;

    // Bundle state
    let bundleIds = new Set<number>();
    let showBundleModal = false;
    let bundleAgent = "cline";
    let bundleConfigs: ConfigResult[] = [];
    let bundleLoading = false;
    let bundleCopied = false;
    const configCache = new Map<string, ConfigResult>();

    const MAX_BUNDLE = 10;
    const agents = [
        {
            id: "cline",
            name: "Cline",
            logo: "https://cdn.simpleicons.org/cline",
        },
        { id: "opencode", name: "opencode", logo: "" },
        { id: "hermes", name: "Hermes", logo: "" },
        { id: "openclaw", name: "OpenClaw", logo: "" },
        { id: "pi", name: "Pi", logo: "" },
        { id: "kilo", name: "Kilo Code", logo: "" },
        { id: "roocode", name: "RooCode", logo: "" },
    ];

    onMount(async () => {
        try {
            providers = await api.getProviders("newest");
            totalModels = providers.reduce((sum, p) => sum + p.model_count, 0);
            providers.forEach(async (p) => {
                try {
                    const h = await api.getProviderHealth(p.id);
                    health[p.id] = h.healthy;
                    health = health;
                } catch {
                    /* ignore */
                }
            });
        } catch (e: any) {
            error = e.message;
        } finally {
            loading = false;
        }
    });

    function toggle(pid: string) {
        expanded[pid] = !expanded[pid];
        expanded = expanded;
    }

    function matchModel(m: ProviderModel, q: string): boolean {
        const ql = q.toLowerCase();
        return (
            m.display_name.toLowerCase().includes(ql) ||
            m.model_id.toLowerCase().includes(ql)
        );
    }

    function filteredModels(p: Provider): ProviderModel[] {
        if (!search.trim()) return p.models;
        return p.models.filter((m) => matchModel(m, search));
    }

    function onSearch() {
        const q = search.trim();
        if (q) {
            for (const p of providers) {
                if (filteredModels(p).length > 0) expanded[p.id] = true;
            }
        }
        expanded = { ...expanded };
    }

    function getVisibleProviders(): Provider[] {
        if (!search.trim()) return providers;
        return providers.filter((p) => filteredModels(p).length > 0);
    }

    async function toggleSort() {
        sortNewest = !sortNewest;
        try {
            providers = await api.getProviders(sortNewest ? "newest" : "");
        } catch {
            /* ignore */
        }
    }

    function isNew(m: ProviderModel): boolean {
        if (!m.first_seen_at) return false;
        const seen = new Date(m.first_seen_at).getTime();
        const now = Date.now();
        return now - seen < 2 * 24 * 60 * 60 * 1000; // 2 hari
    }

    // Bundle actions
    function toggleBundle(modelId: number) {
        if (bundleIds.has(modelId)) {
            bundleIds.delete(modelId);
        } else if (bundleIds.size < MAX_BUNDLE) {
            bundleIds.add(modelId);
        }
        bundleIds = new Set(bundleIds); // trigger reactivity
    }

    function getModelById(id: number): ProviderModel | null {
        for (const p of providers) {
            for (const m of p.models) {
                if (m.id === id) return m;
            }
        }
        return null;
    }

    function getBundleModels(): (ProviderModel & { provider_id: string })[] {
        const result: (ProviderModel & { provider_id: string })[] = [];
        for (const p of providers) {
            for (const m of p.models) {
                if (bundleIds.has(m.id))
                    result.push({ ...m, provider_id: p.id });
            }
        }
        return result;
    }

    async function fetchBundleConfigs(agentId: string) {
      bundleLoading = true;
      const ids = Array.from(bundleIds);
      const results = await Promise.all(
        ids.map(async (id) => {
          const key = `${agentId}:${id}`;
          if (configCache.has(key)) return configCache.get(key)!;
          const cfg = await api.getConfig(agentId, id);
          configCache.set(key, cfg);
          return cfg;
        })
      );
      bundleConfigs = results;
      bundleLoading = false;
    }

    async function openBundleModal() {
      showBundleModal = true;
      await fetchBundleConfigs(bundleAgent);
    }

    async function onBundleAgentChange(agentId: string) {
      bundleAgent = agentId;
      bundleCopied = false;
      await fetchBundleConfigs(agentId);
    }

    async function copyBundle() {
        const combined = bundleConfigs
            .map((c) => `# ${c.model}\n${c.content}`)
            .join("\n\n---\n\n");
        await navigator.clipboard.writeText(combined);
        bundleCopied = true;
        setTimeout(() => (bundleCopied = false), 2000);
    }

    function downloadBundle() {
        const combined = bundleConfigs
            .map((c) => `# ${c.model}\n${c.content}`)
            .join("\n\n---\n\n");
        const blob = new Blob([combined], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `tokenzero-bundle-${bundleAgent}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
</script>

<div class="space-y-12">
    <!-- Hero -->
    <section class="text-center py-16 space-y-4">
        <h1
            class="text-5xl font-bold tracking-tight flex items-center justify-center gap-3"
        >
            <span
                class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-linear-to-br from-zinc-800 to-zinc-950 dark:from-zinc-200 dark:to-white text-white dark:text-zinc-900 text-xl font-black tracking-tighter shadow-md ring-1 ring-zinc-200 dark:ring-zinc-700"
                >T0</span
            >
            Token Zero
        </h1>
        <p class="text-xl text-muted-foreground max-w-lg mx-auto">
            Free AI models. Always updated. One-click config. Bundle ready.
        </p>
        {#if loading}
            <p class="text-sm text-muted-foreground animate-pulse">
                Loading...
            </p>
        {:else}
            <div
                class="flex items-center justify-center gap-4 text-sm text-muted-foreground"
            >
                <span class="font-semibold text-foreground"
                    >{providers.length}</span
                >
                provider
                <span class="text-border">·</span>
                <span class="font-semibold text-foreground">{totalModels}</span> free
                models
            </div>
        {/if}
    </section>

    <!-- Search + Sort -->
    <div class="max-w-md mx-auto flex gap-2">
        <div class="relative flex-1">
            <span
                class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm"
                >🔍</span
            >
            <input
                type="text"
                bind:value={search}
                oninput={onSearch}
                placeholder="Search models..."
                class="w-full h-10 pl-9 pr-4 rounded-md border bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 text-sm placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-zinc-900 dark:focus:ring-zinc-100 appearance-none"
            />
            {#if search}
                <button
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground text-xs"
                    onclick={() => {
                        search = "";
                        onSearch();
                    }}>✕</button
                >
            {/if}
        </div>
        <button
            onclick={toggleSort}
            class="inline-flex items-center rounded-md border px-3 py-2 text-xs font-medium hover:bg-accent transition-colors shrink-0
             {sortNewest
                ? 'bg-primary text-primary-foreground border-primary'
                : ''}"
        >
            {sortNewest ? "✨ Newest" : "📋 A-Z"}
        </button>
    </div>

    <!-- Providers -->
    {#if error}
        <div class="text-center text-red-500 text-sm">{error}</div>
    {/if}

    <div class="space-y-2">
        {#each getVisibleProviders() as p}
            {@const models = filteredModels(p)}
            <div
                class="rounded-lg border bg-card shadow-sm overflow-hidden transition-shadow hover:shadow-md"
            >
                <button
                    class="w-full flex items-center justify-between px-5 py-3.5 text-left"
                    onclick={() => toggle(p.id)}
                >
                    <div class="flex items-center gap-3">
                        {#if p.logo_url}
                            <img
                                src={p.logo_url}
                                alt=""
                                class="w-5 h-5 rounded"
                            />
                        {/if}
                        <span class="font-semibold">{p.name}</span>
                        {#if health[p.id] !== undefined}
                            <span
                                class="inline-block w-2 h-2 rounded-full {health[
                                    p.id
                                ]
                                    ? 'bg-green-500'
                                    : 'bg-red-500'}"
                                title={health[p.id] ? "Online" : "Offline"}
                            ></span>
                        {/if}
                        <span
                            class="inline-flex items-center rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground"
                        >
                            {models.length}/{p.model_count} model
                        </span>
                    </div>
                    <svg
                        class="w-4 h-4 text-muted-foreground transition-transform {expanded[
                            p.id
                        ]
                            ? 'rotate-90'
                            : ''}"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        ><path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M9 5l7 7-7 7"
                        /></svg
                    >
                </button>

                {#if expanded[p.id]}
                    {#if models.length > 0}
                        <div class="border-t divide-y">
                            {#each models as m}
                                <div
                                    class="flex items-center justify-between gap-3 px-5 py-3 hover:bg-muted/50 transition-colors"
                                >
                                    <a
                                        href={`/models/${m.id}`}
                                        use:link
                                        class="min-w-0"
                                    >
                                        <div class="flex items-center gap-2">
                                            {#if isNew(m)}
                                                <span
                                                    class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-1.5 py-0 text-[10px] font-bold shrink-0"
                                                    >NEW</span
                                                >
                                            {/if}
                                            <span class="font-medium text-sm"
                                                >{m.display_name}</span
                                            >
                                            {#each m.capabilities.filter((c) => c !== "text") as cap}
                                                <span
                                                    class="inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-medium {capClass(
                                                        cap,
                                                    )} shrink-0">{cap}</span
                                                >
                                            {/each}
                                        </div>
                                        <div class="mt-0.5">
                                            <span
                                                class="text-xs text-muted-foreground font-mono"
                                                >{m.model_id}</span
                                            >
                                        </div>
                                    </a>
                                    <button
                                        class="inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-medium transition-colors shrink-0
                           {bundleIds.has(m.id)
                                            ? 'bg-primary text-primary-foreground border-primary'
                                            : 'hover:bg-accent'}"
                                        onclick={() => toggleBundle(m.id)}
                                    >
                                        {bundleIds.has(m.id)
                                            ? "✓ Bundled"
                                            : "+ Bundle"}
                                    </button>
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <div
                            class="border-t px-5 py-3 text-sm text-muted-foreground"
                        >
                            No matching models.
                        </div>
                    {/if}
                {/if}
            </div>
        {:else}
            {#if search && !loading}
                <div class="text-center py-12 text-muted-foreground">
                    No results. Try another keyword.
                </div>
            {/if}
        {/each}
    </div>

    <!-- Footer -->
    <footer class="text-center text-xs text-muted-foreground py-8">
        Token Zero · token-0.com
    </footer>
</div>

<!-- Floating bundle bar -->
{#if bundleIds.size > 0}
    <div class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <button
            onclick={openBundleModal}
            class="inline-flex items-center gap-2 rounded-full bg-primary text-primary-foreground shadow-lg px-5 py-3 text-sm font-medium hover:opacity-90 transition-opacity"
        >
            📦 {bundleIds.size}/{MAX_BUNDLE} models — Bundle Config
        </button>
    </div>
{/if}

<!-- Bundle Modal -->
{#if showBundleModal}
    <div
        class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
        role="button"
        tabindex="0"
        onclick={() => (showBundleModal = false)}
        onkeydown={(e) => e.key === 'Escape' && (showBundleModal = false)}
    >
        <div
            class="bg-white dark:bg-zinc-900 rounded-lg border shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-5"
            role="presentation"
            onclick={(e) => e.stopPropagation()}
            onkeydown={(e) => e.stopPropagation()}
        >
            <div class="flex items-center justify-between">
                <h2 class="font-semibold text-lg">
                    📦 Bundle Config ({bundleIds.size} models)
                </h2>
                <button
                    onclick={() => (showBundleModal = false)}
                    class="text-muted-foreground hover:text-foreground text-lg"
                    >✕</button
                >
            </div>

            <!-- Agent tabs -->
            <div class="flex flex-wrap gap-2">
                {#each agents as a}
                    <button
                        class="inline-flex items-center rounded-md px-3 py-1.5 text-sm font-medium transition-colors
                   {bundleAgent === a.id
                            ? 'bg-primary text-primary-foreground shadow'
                            : 'border hover:bg-accent'}"
                        onclick={() => onBundleAgentChange(a.id)}
                    >
                        {#if a.logo}<img
                                src={a.logo}
                                alt=""
                                class="w-4 h-4 rounded-sm mr-1.5"
                            />{/if}
                        {a.name}
                    </button>
                {/each}
            </div>

            <!-- Config output -->
            {#if bundleLoading}
                <p class="text-sm text-muted-foreground animate-pulse">
                    Generating configs...
                </p>
            {:else}
                <pre
                    class="bg-secondary/50 rounded-md border p-4 text-xs overflow-x-auto leading-relaxed max-h-96"><code>
          {bundleConfigs
                            .map((c) => `# ${c.model}\n${c.content}`)
                            .join("\n\n---\n\n")}
        </code></pre>
                <div class="flex gap-2">
                    <button
                        onclick={copyBundle}
                        class="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
                    >
                        {bundleCopied ? "✓ Copied!" : "📋 Copy All"}
                    </button>
                    <button
                        onclick={downloadBundle}
                        class="inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors"
                    >
                        ⬇ Download .txt
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}
