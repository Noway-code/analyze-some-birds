import "./style.css";
import { setupCounter } from "./counter.ts";

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
<div id="app">
  <section id="top">
    <h1>Welcome to your bird feed!</h1>
  </section>

  <section id="center">
    <div class="choices">
      <a class="card" href="#feed">Feed</a>
      <a class="card" href="#explore">Explore</a>
      <a class="card" href="#profile">Profile</a>
    </div>
  </section>

  <section class="featured">
  <div class="featured-card">
    <img src="thumb.jpg" />
    <div class="meta">
      <span class="badge">NEW</span>
      <h2>Video Title</h2>
    </div>
  </div>
</section>

<section class="video-grid">
  <div class="video-card">...</div>
  <div class="video-card">...</div>
  <div class="video-card">...</div>
</section>

  <section id="spacer"></section>
</div>
`;

document.querySelector("#load-button")?.addEventListener("click", loadVideos);

async function loadVideos() {
  try {
    const res = await fetch("/api/videos");
    const videos = await res.json();

    const container = document.querySelector("#gallery")!;

    videos.forEach((v) => {
      const video = document.createElement("video");
      video.src = v.url;
      video.controls = true;
      video.width = 300;
      container.appendChild(video);
    });
  } catch (err) {
    console.error("Failed to load videos", err);
  }
}
