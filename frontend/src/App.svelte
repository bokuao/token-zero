<script lang="ts">
  import "./app.css";
  import Router from "svelte-spa-router";
  import Home from "./pages/Home.svelte";
  import ModelDetail from "./pages/ModelDetail.svelte";
  import Nav from "./components/Nav.svelte";

  const routes = {
    "/": Home,
    "/models/:id": ModelDetail,
  };
</script>

<div class="min-h-screen bg-background text-foreground">
  <Nav />
  <main class="max-w-4xl mx-auto px-4 py-8">
    <Router {routes} />
  </main>
</div>
