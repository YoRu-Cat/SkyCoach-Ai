import streamlit as st
from streamlit.components.v1 import html


def render_motion_stage() -> None:
    """Render a cinematic animated banner using GSAP inside an iframe."""
    html(
        """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body {
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: linear-gradient(135deg, #0f0f1a 0%, #12182b 50%, #0f172a 100%);
      font-family: Inter, system-ui, sans-serif;
    }

    .stage {
      position: relative;
      width: 100%;
      height: 220px;
      border-radius: 28px;
      overflow: hidden;
      background:
        radial-gradient(circle at 20% 20%, rgba(6, 182, 212, 0.28), transparent 26%),
        radial-gradient(circle at 80% 30%, rgba(139, 92, 246, 0.26), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(16, 185, 129, 0.14), transparent 28%),
        linear-gradient(135deg, rgba(15, 15, 26, 0.98), rgba(17, 24, 39, 0.98));
      box-shadow: inset 0 0 120px rgba(255, 255, 255, 0.04), 0 20px 60px rgba(0, 0, 0, 0.45);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .glow {
      position: absolute;
      inset: 0;
      pointer-events: none;
      mix-blend-mode: screen;
    }

    .orb {
      position: absolute;
      border-radius: 999px;
      filter: blur(10px);
      opacity: 0.9;
      will-change: transform;
    }

    .orb.one { width: 120px; height: 120px; left: 4%; top: 16%; background: linear-gradient(135deg, rgba(6,182,212,0.95), rgba(59,130,246,0.25)); }
    .orb.two { width: 160px; height: 160px; right: 5%; top: 6%; background: linear-gradient(135deg, rgba(139,92,246,0.9), rgba(236,72,153,0.16)); }
    .orb.three { width: 90px; height: 90px; right: 22%; bottom: 14%; background: linear-gradient(135deg, rgba(16,185,129,0.9), rgba(34,197,94,0.18)); }

    .grid {
      position: absolute;
      inset: 0;
      background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
      background-size: 40px 40px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8));
      opacity: 0.35;
    }

    .headline {
      position: absolute;
      left: 28px;
      bottom: 22px;
      z-index: 3;
      color: white;
    }

    .eyebrow {
      font-size: 0.72rem;
      letter-spacing: 0.28em;
      text-transform: uppercase;
      color: rgba(255,255,255,0.55);
      margin-bottom: 8px;
    }

    .title {
      font-size: 1.85rem;
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.04em;
      background: linear-gradient(135deg, #ffffff 0%, #b7c0ff 35%, #67e8f9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .subtitle {
      margin-top: 8px;
      color: rgba(255,255,255,0.68);
      max-width: 420px;
      font-size: 0.96rem;
    }

    .spark {
      position: absolute;
      width: 12px;
      height: 12px;
      border-radius: 999px;
      background: white;
      box-shadow: 0 0 18px rgba(255,255,255,0.9);
      opacity: 0.8;
      will-change: transform, opacity;
    }
  </style>
</head>
<body>
  <div class="stage">
    <div class="grid"></div>
    <div class="glow">
      <div class="orb one"></div>
      <div class="orb two"></div>
      <div class="orb three"></div>
      <div class="spark" style="left: 18%; top: 28%;"></div>
      <div class="spark" style="left: 42%; top: 18%;"></div>
      <div class="spark" style="left: 66%; top: 36%;"></div>
      <div class="spark" style="left: 82%; top: 62%;"></div>
      <div class="spark" style="left: 58%; top: 76%;"></div>
    </div>

    <div class="headline">
      <div class="eyebrow">SkyCoach Motion Layer</div>
      <div class="title">Weather intelligence, but cinematic.</div>
      <div class="subtitle">Animated light fields, drifting particles, and a glass-forward stage for the new interface system.</div>
    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script>
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!prefersReducedMotion && window.gsap) {
      gsap.to('.orb.one', { x: 40, y: -14, duration: 5.5, ease: 'sine.inOut', repeat: -1, yoyo: true });
      gsap.to('.orb.two', { x: -28, y: 18, duration: 6.8, ease: 'sine.inOut', repeat: -1, yoyo: true });
      gsap.to('.orb.three', { x: 24, y: -20, duration: 4.9, ease: 'sine.inOut', repeat: -1, yoyo: true });

      gsap.utils.toArray('.spark').forEach((spark, index) => {
        gsap.to(spark, {
          y: -12 - (index % 3) * 8,
          x: 8 + (index % 2) * 12,
          opacity: 0.35,
          duration: 1.4 + index * 0.18,
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut'
        });
      });
    }
  </script>
</body>
</html>
        """,
        height=240,
        scrolling=False,
    )
