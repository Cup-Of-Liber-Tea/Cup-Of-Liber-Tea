import os
import datetime
import random

def generate_hud():
    # 색상 팔레트 (Cyberpunk Neon)
    cyan = "#00f3ff"
    red = "#ff003c"
    yellow = "#fcee0a"
    bg = "#0a0a0a"
    
    # 현재 시간
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    
    # 랜덤 데이터 시뮬레이션
    core_temp = random.randint(40, 65)
    cpu_load = random.randint(10, 40)
    
    svg_content = f"""
<svg width="800" height="300" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&amp;display=swap');
    
    .text {{ font-family: 'Share Tech Mono', monospace; fill: {cyan}; }}
    .alert {{ fill: {red}; }}
    .warn {{ fill: {yellow}; }}
    
    /* 애니메이션 정의 */
    @keyframes rotate {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}
    
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}
    
    @keyframes scan {{
      0% {{ transform: translateX(-50px); opacity: 0; }}
      10% {{ opacity: 1; }}
      90% {{ opacity: 1; }}
      100% {{ transform: translateX(850px); opacity: 0; }}
    }}
    
    @keyframes pulse {{
      0% {{ r: 5; opacity: 0.5; }}
      100% {{ r: 15; opacity: 0; }}
    }}

    .spinner {{ transform-origin: 100px 150px; animation: rotate 10s linear infinite; }}
    .blinker {{ animation: blink 1s infinite; }}
    .scanner {{ animation: scan 3s linear infinite; }}
    .pulser {{ animation: pulse 2s infinite; }}
    
  </style>

  <!-- 배경 -->
  <rect x="0" y="0" width="800" height="300" fill="{bg}" rx="15" />
  
  <!-- 배경 그리드 -->
  <defs>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="{cyan}" stroke-width="0.5" opacity="0.1"/>
    </pattern>
  </defs>
  <rect width="800" height="300" fill="url(#grid)" />

  <!-- 왼쪽: 회전하는 리액터 코어 -->
  <g class="spinner">
    <circle cx="100" cy="150" r="60" stroke="{cyan}" stroke-width="2" fill="none" stroke-dasharray="10 5" opacity="0.7" />
    <circle cx="100" cy="150" r="45" stroke="{yellow}" stroke-width="1" fill="none" stroke-dasharray="5 5" opacity="0.5" />
    <circle cx="100" cy="150" r="30" stroke="{red}" stroke-width="2" fill="none" opacity="0.8" />
  </g>
  <text x="100" y="155" text-anchor="middle" class="text" font-size="12">CORE</text>

  <!-- 중앙: 시스템 정보 -->
  <g transform="translate(200, 50)">
    <text x="0" y="0" class="text" font-size="24" font-weight="bold">SYSTEM ONLINE</text>
    <rect x="220" y="-15" width="10" height="10" fill="{cyan}" class="blinker" />
    
    <text x="0" y="40" class="text" font-size="16">TARGET: CUP-OF-LIBER-TEA</text>
    <text x="0" y="70" class="text" font-size="16">ACCESS: GRANTED (Lv.99)</text>
    
    <!-- 실시간(빌드타임) 데이터 -->
    <text x="0" y="110" class="text" font-size="14">SERVER TIME: {time_str} KST</text>
    <text x="0" y="130" class="text" font-size="14">DATE: {date_str}</text>
    
    <!-- 가짜 로딩 바 -->
    <text x="0" y="170" class="text" font-size="14">SYNC RATE</text>
    <rect x="100" y="160" width="200" height="10" stroke="{cyan}" fill="none" />
    <rect x="102" y="162" width="{random.randint(150, 190)}" height="6" fill="{cyan}" opacity="0.8">
      <animate attributeName="width" values="150;190;160;180" dur="2s" repeatCount="indefinite" />
    </rect>
  </g>

  <!-- 오른쪽: 상태 게이지 -->
  <g transform="translate(550, 50)">
    <text x="0" y="0" class="text" font-size="14">CORE TEMP</text>
    <rect x="0" y="10" width="150" height="5" fill="#333" />
    <rect x="0" y="10" width="{core_temp * 1.5}" height="5" fill="{red}" />
    <text x="160" y="15" class="text" font-size="12">{core_temp}°C</text>
    
    <text x="0" y="40" class="text" font-size="14">CPU LOAD</text>
    <rect x="0" y="50" width="150" height="5" fill="#333" />
    <rect x="0" y="50" width="{cpu_load * 1.5}" height="5" fill="{yellow}" />
    <text x="160" y="55" class="text" font-size="12">{cpu_load}%</text>
    
    <!-- 스캔 효과 -->
    <rect x="0" y="100" width="200" height="100" fill="none" stroke="{cyan}" stroke-width="1" opacity="0.5"/>
    <text x="10" y="120" class="text" font-size="10" opacity="0.7">
      Analyzing commit history...
      Optimizing neural net...
      Brewing coffee...
    </text>
  </g>
  
  <!-- 스캐너 라인 (화면 전체를 훑음) -->
  <rect class="scanner" x="0" y="0" width="20" height="300" fill="url(#grid)" opacity="0.3" />
  <rect class="scanner" x="0" y="0" width="2" height="300" fill="{cyan}" opacity="0.8" style="filter: drop-shadow(0 0 5px {cyan});" />

</svg>
    """
    
    # Save to assets/hud.svg
    # Ensure assets dir exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    assets_dir = os.path.join(project_root, "assets")
    
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    with open(os.path.join(assets_dir, "hud.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("Generated hud.svg")

if __name__ == "__main__":
    generate_hud()

