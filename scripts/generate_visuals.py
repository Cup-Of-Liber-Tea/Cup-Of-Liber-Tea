import os
import random

def generate_glitch_header():
    # Cyberpunk Colors
    cyan = "#00f3ff"
    magenta = "#ff00ff"
    white = "#ffffff"
    bg = "#0a0a0a"
    
    svg_content = f"""
<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&amp;display=swap');
    
    .bg {{ fill: {bg}; }}
    .text {{ 
      font-family: 'Black Ops One', cursive; 
      font-size: 60px; 
      fill: {white};
      text-anchor: middle;
      dominant-baseline: middle;
    }}
    
    /* Glitch Animation */
    @keyframes glitch-anim {{
      0% {{ transform: translate(0); }}
      20% {{ transform: translate(-2px, 2px); }}
      40% {{ transform: translate(-2px, -2px); }}
      60% {{ transform: translate(2px, 2px); }}
      80% {{ transform: translate(2px, -2px); }}
      100% {{ transform: translate(0); }}
    }}
    
    @keyframes glitch-color {{
      0% {{ fill: {white}; }}
      33% {{ fill: {cyan}; }}
      66% {{ fill: {magenta}; }}
      100% {{ fill: {white}; }}
    }}
    
    .glitch-layer {{ mix-blend-mode: exclusion; }}
    .g1 {{ animation: glitch-anim 2s infinite linear alternate-reverse; fill: {cyan}; opacity: 0.8; }}
    .g2 {{ animation: glitch-anim 3s infinite linear alternate-reverse; fill: {magenta}; opacity: 0.8; }}
    .main-text {{ animation: glitch-color 5s infinite; }}
    
  </style>
  
  <rect width="800" height="200" class="bg" />
  
  <!-- Glitch Layers -->
  <text x="400" y="100" class="text g1 glitch-layer" dx="-5" dy="0">CUP-OF-LIBER-TEA</text>
  <text x="400" y="100" class="text g2 glitch-layer" dx="5" dy="0">CUP-OF-LIBER-TEA</text>
  <text x="400" y="100" class="text main-text">CUP-OF-LIBER-TEA</text>
  
  <!-- Deco Lines -->
  <path d="M 100 130 L 700 130" stroke="{cyan}" stroke-width="2" opacity="0.5" />
  <path d="M 100 70 L 700 70" stroke="{magenta}" stroke-width="2" opacity="0.5" />

</svg>
    """
    save_svg("header_glitch.svg", svg_content)

def generate_holo_skills():
    # Hexagon Grid for Skills
    cyan = "#00f3ff"
    
    # Skills Configuration
    skills = [
        {"name": "JS", "x": 300, "y": 100, "icon": "javascript-original"},
        {"name": "TS", "x": 380, "y": 60, "icon": "typescript-original"},
        {"name": "React", "x": 380, "y": 140, "icon": "react-original"},
        {"name": "Node", "x": 460, "y": 100, "icon": "nodejs-original"},
        {"name": "Python", "x": 540, "y": 60, "icon": "python-original"},
        {"name": "Git", "x": 540, "y": 140, "icon": "git-original"}
    ]
    
    hex_path = "M 30 0 L 60 17 L 60 52 L 30 70 L 0 52 L 0 17 Z" # Basic Hexagon path
    
    shapes = ""
    for skill in skills:
        # Devicon URL
        icon_url = f"https://cdn.jsdelivr.net/gh/devicons/devicon/icons/{skill['icon'].split('-')[0]}/{skill['icon']}.svg"
        
        shapes += f"""
        <g transform="translate({skill['x']}, {skill['y']})" class="hex-container">
            <path d="{hex_path}" fill="#111" stroke="{cyan}" stroke-width="2" opacity="0.8">
                <animate attributeName="stroke-opacity" values="0.8;0.2;0.8" dur="{random.randint(2,5)}s" repeatCount="indefinite" />
            </path>
            <image href="{icon_url}" x="15" y="15" height="40" width="40" />
        </g>
        """

    svg_content = f"""
<svg width="800" height="250" viewBox="0 0 800 250" xmlns="http://www.w3.org/2000/svg">
  <style>
    .hex-container:hover path {{ fill: #222; stroke: #fff; cursor: pointer; }}
  </style>
  <rect width="800" height="250" fill="#0a0a0a" />
  
  <text x="400" y="30" fill="{cyan}" font-family="monospace" text-anchor="middle" font-size="16">>> ACTIVE_MODULES <<</text>
  
  {shapes}
  
  <!-- Connecting Lines -->
  <path d="M 360 135 L 380 135" stroke="{cyan}" stroke-width="1" opacity="0.3" />
  <path d="M 440 95 L 460 95" stroke="{cyan}" stroke-width="1" opacity="0.3" />
  
</svg>
    """
    save_svg("skills_holo.svg", svg_content)

def save_svg(filename, content):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    assets_dir = os.path.join(project_root, "assets")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    with open(os.path.join(assets_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_glitch_header()
    generate_holo_skills()

