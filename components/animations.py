import streamlit as st
from streamlit.components.v1 import html


def render_motion_stage() -> None:
    """Render a cinematic animated banner using GSAP inside an iframe with enhanced parallax and particles."""
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
      font-family: 'Space Grotesk', system-ui, sans-serif;
    }

    .stage {
      position: relative;
      width: 100%;
      height: 220px;
      border-radius: 28px;
      overflow: hidden;
      background:
        radial-gradient(circle at 20% 20%, rgba(6, 182, 212, 0.32), transparent 26%),
        radial-gradient(circle at 80% 30%, rgba(139, 92, 246, 0.28), transparent 28%),
        radial-gradient(circle at 50% 80%, rgba(16, 185, 129, 0.16), transparent 28%),
        linear-gradient(135deg, rgba(15, 15, 26, 0.98), rgba(17, 24, 39, 0.98));
      box-shadow: 
        inset 0 0 120px rgba(255, 255, 255, 0.05),
        inset 0 0 60px rgba(6, 182, 212, 0.08),
        0 20px 60px rgba(0, 0, 0, 0.45),
        0 0 40px rgba(6, 182, 212, 0.1);
      border: 1px solid rgba(125, 211, 252, 0.18);
      will-change: transform;
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
      filter: blur(12px);
      opacity: 0.85;
      will-change: transform;
      animation: float 6s ease-in-out infinite;
    }

    .orb.one { 
      width: 140px; 
      height: 140px; 
      left: 2%; 
      top: 12%; 
      background: linear-gradient(135deg, rgba(6,182,212,0.98), rgba(59,130,246,0.32));
      animation-delay: 0s;
    }
    
    .orb.two { 
      width: 180px; 
      height: 180px; 
      right: 2%; 
      top: 0%; 
      background: linear-gradient(135deg, rgba(139,92,246,0.92), rgba(236,72,153,0.24));
      animation-delay: 0.8s;
    }
    
    .orb.three { 
      width: 100px; 
      height: 100px; 
      right: 18%; 
      bottom: 8%; 
      background: linear-gradient(135deg, rgba(16,185,129,0.92), rgba(34,197,94,0.28));
      animation-delay: 1.6s;
    }

    .particle {
      position: absolute;
      border-radius: 999px;
      opacity: 0.4;
      will-change: transform, opacity;
      pointer-events: none;
    }

    .grid {
      position: absolute;
      inset: 0;
      background-image: 
        linear-gradient(rgba(125,211,252,0.08) 1px, transparent 1px), 
        linear-gradient(90deg, rgba(125,211,252,0.08) 1px, transparent 1px);
      background-size: 50px 50px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,0.15), rgba(0,0,0,0.8));
      opacity: 0.4;
      animation: parallaxShift 8s ease-in-out infinite;
    }

    .headline {
      position: absolute;
      left: 32px;
      bottom: 24px;
      z-index: 3;
      color: white;
      animation: slideInLeft 0.8s ease-out;
    }

    .eyebrow {
      font-size: 0.72rem;
      letter-spacing: 0.32em;
      text-transform: uppercase;
      color: rgba(6, 182, 212, 0.8);
      margin-bottom: 8px;
      font-weight: 600;
    }

    .title {
      font-size: 1.95rem;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.04em;
      background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 35%, #67e8f9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: slideInUp 0.9s ease-out 0.1s both;
    }

    .subtitle {
      margin-top: 10px;
      color: rgba(226, 232, 240, 0.74);
      max-width: 450px;
      font-size: 0.96rem;
      line-height: 1.5;
      animation: slideInUp 0.9s ease-out 0.2s both;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px) translateX(0px); }
      25% { transform: translateY(-16px) translateX(8px); }
      50% { transform: translateY(-6px) translateX(-12px); }
      75% { transform: translateY(-18px) translateX(10px); }
    }

    @keyframes parallaxShift {
      0% { transform: translateY(0px) scale(1); }
      50% { transform: translateY(-6px) scale(1.02); }
      100% { transform: translateY(0px) scale(1); }
    }

    @keyframes slideInLeft {
      from { 
        opacity: 0; 
        transform: translateX(-40px);
      }
      to { 
        opacity: 1; 
        transform: translateX(0);
      }
    }

    @keyframes slideInUp {
      from { 
        opacity: 0; 
        transform: translateY(24px);
      }
      to { 
        opacity: 1; 
        transform: translateY(0);
      }
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
      <div id="particles-container"></div>
    </div>

    <div class="headline">
      <div class="eyebrow">✨ SkyCoach Motion Layer</div>
      <div class="title">Weather Intelligence, Cinematic</div>
      <div class="subtitle">Glassmorphic layers, parallax depth, and flowing particle dynamics for the next-gen interface.</div>
    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script>
    const prefersReducedMotion = window.matchMedia('(prefers-reduce-motion: reduce)').matches;
    
    // Particle system
    class ParticleSystem {
      constructor(container) {
        this.container = container;
        this.particles = [];
        this.init();
      }

      init() {
        for (let i = 0; i < 12; i++) {
          this.createParticle();
        }
      }

      createParticle() {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = Math.random() * 6 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.background = ['rgba(6,182,212,0.6)', 'rgba(139,92,246,0.5)', 'rgba(16,185,129,0.5)'][Math.floor(Math.random() * 3)];
        this.container.appendChild(particle);
        
        this.animateParticle(particle);
      }

      animateParticle(particle) {
        const duration = Math.random() * 4 + 3;
        const delay = Math.random() * 0.5;
        
        if (!prefersReducedMotion && window.gsap) {
          gsap.to(particle, {
            y: Math.random() * -80 - 40 + 'px',
            x: (Math.random() - 0.5) * 60 + 'px',
            opacity: 0,
            duration: duration,
            delay: delay,
            ease: 'sine.inOut',
            onComplete: () => this.createParticle()
          });
        }
      }
    }

    // Initialize systems
    if (window.gsap) {
      const container = document.getElementById('particles-container');
      new ParticleSystem(container);

      if (!prefersReducedMotion) {
        // Orb animations
        gsap.to('.orb.one', { 
          x: 50, 
          y: -20, 
          duration: 6.2, 
          ease: 'sine.inOut', 
          repeat: -1, 
          yoyo: true 
        });
        
        gsap.to('.orb.two', { 
          x: -40, 
          y: 24, 
          duration: 7.4, 
          ease: 'sine.inOut', 
          repeat: -1, 
          yoyo: true 
        });
        
        gsap.to('.orb.three', { 
          x: 32, 
          y: -28, 
          duration: 5.6, 
          ease: 'sine.inOut', 
          repeat: -1, 
          yoyo: true 
        });

        // Stage glow pulse
        gsap.to('.stage', {
          boxShadow: [
            '0 0 40px rgba(6, 182, 212, 0.1)',
            '0 0 60px rgba(6, 182, 212, 0.2)',
            '0 0 40px rgba(6, 182, 212, 0.1)'
          ],
          duration: 3,
          repeat: -1,
          ease: 'sine.inOut'
        });
      }
    }
  </script>
</body>
</html>
        """,
        height=250,
        scrolling=False,
    )


class ParallaxEffect:
    """Manage parallax scrolling effects on page sections."""
    
    def __init__(self):
        self.enabled = True
    
    @staticmethod
    def inject_parallax_script():
        """Inject scroll-triggered parallax animations."""
        st.markdown(
            """
            <script>
            const prefersReducedMotion = window.matchMedia('(prefers-reduce-motion: reduce)').matches;
            if (!prefersReducedMotion) {
              document.addEventListener('scroll', function() {
                const scrolled = window.scrollY;
                const parallaxElements = document.querySelectorAll('[data-parallax]');
                
                parallaxElements.forEach(el => {
                  const speed = parseFloat(el.getAttribute('data-parallax')) || 0.5;
                  el.style.transform = 'translateY(' + (scrolled * speed) + 'px)';
                });
              }, false);
            }
            </script>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def add_parallax_class(element_id: str, speed: float = 0.5):
        """Add parallax effect to an element."""
        st.markdown(
            f'<div id="{element_id}" data-parallax="{speed}"></div>',
            unsafe_allow_html=True
        )
