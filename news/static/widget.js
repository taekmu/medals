(function () {
  const container = document.currentScript ? document.currentScript.parentElement : document.body;

  // 1. 내부 콘텐츠를 담을 전용 영역 생성 (전체가 깜빡이는 것 방지)
  container.innerHTML = `<div id="medal-content-area"></div>`;
  const contentArea = document.getElementById("medal-content-area");

  // 초기 로딩 화면 표시
  contentArea.innerHTML = `
    <div id="medal-loader" style="padding:40px 20px; text-align:center; color:#64748b; font-family:sans-serif; font-size:0.9rem;">
      <div style="font-size:2rem; margin-bottom:10px; animation: pulse 1.5s infinite;">📡</div>
      대한민국 데이터 확인 중...
    </div>
    <style>@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }</style>`;

  // 2. 데이터를 가져오고 화면을 그리는 함수 정의
  function updateMedals() {
    fetch("/medals")
      .then(res => res.json())
      .then(data => {
        if (!data || data.length === 0) {
          // 이미 데이터가 표시 중인 경우 에러 메시지로 덮어쓰지 않음
          if (!contentArea.querySelector('h3')) {
            contentArea.innerHTML = "<div style='padding:20px; text-align:center;'>데이터를 가져올 수 없습니다.</div>";
          }
          return;
        }

        let html = `
          <div style="font-family: 'Pretendard', -apple-system, sans-serif; width: 100%; max-width: 400px; margin: 10px auto; background: #fff; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.12); overflow: hidden; border: 1px solid #e2e8f0;">
            <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); color: white; padding: 20px; text-align: center;">
              <h3 style="margin:0; font-size: 1.2rem; font-weight: 800; letter-spacing: -0.5px;">🏅 2026 동계 올림픽 순위</h3>
            </div>
            <div style="background: #f8fafc; display: flex; padding: 12px 10px; font-size: 0.75rem; color: #64748b; font-weight: bold; text-align: center; border-bottom: 1px solid #f1f5f9; letter-spacing: 1px;">
              <div style="width: 40px;">RANK</div>
              <div style="flex: 1; text-align: left; padding-left: 10px;">COUNTRY</div>
              <div style="width: 35px;">G</div>
              <div style="width: 35px;">S</div>
              <div style="width: 35px;">B</div>
            </div>
            <div style="padding: 8px;">
        `;

        data.forEach((team) => {
          const isKorea = team.is_korea === true;
          const rank = team.rank;
          const rowStyle = isKorea 
            ? `background: #eff6ff; border: 2px solid #2563eb; border-radius: 14px; margin: 8px 0; padding: 15px 5px; transform: scale(1.02); box-shadow: 0 4px 12px rgba(37,99,235,0.15);` 
            : `border-bottom: 1px solid #f1f5f9; padding: 12px 5px;`;
          
          const rankColor = isKorea ? '#1d4ed8' : (rank <= 3 ? '#2563eb' : '#94a3b8');
          const nameColor = isKorea ? '#1d4ed8' : '#1e293b';

          html += `
            <div style="display: flex; align-items: center; transition: all 0.3s ease; ${rowStyle}">
              <div style="width: 40px; text-align: center; font-weight: 900; color: ${rankColor}; font-size: 1.1rem;">${rank}</div>
              <div style="flex: 1; font-weight: ${isKorea ? '900' : '600'}; color: ${nameColor}; display: flex; align-items: center; gap: 8px; padding-left: 5px;">
                ${isKorea ? '<span style="font-size: 1.4rem;">🇰🇷</span>' : ''} 
                <span style="font-size: ${isKorea ? '1rem' : '0.95rem'};">${team.country}</span>
                ${isKorea ? '<span style="background:#2563eb; color:white; font-size:0.65rem; padding:3px 7px; border-radius:20px; font-weight:bold; margin-left: auto; margin-right: 10px; white-space:nowrap;">KOREA</span>' : ''}
              </div>
              <div style="display: flex; gap: 4px; text-align: center; font-size: 1rem;">
                <div style="width: 35px; color: #d4af37; font-weight: 800;">${team.gold}</div>
                <div style="width: 35px; color: #94a3b8; font-weight: 800;">${team.silver}</div>
                <div style="width: 35px; color: #b45309; font-weight: 800;">${team.bronze}</div>
              </div>
            </div>`;
        });

        // 현재 시간 표시
        const now = new Date();
        const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

        html += `
            </div>
            <div style="background: #f8fafc; padding: 15px; text-align: center; font-size: 0.8rem; color: #94a3b8; border-top: 1px solid #f1f5f9;">
              📡 실시간 동기화 중 (마지막 업데이트: ${timeStr})
            </div>
          </div>
        `;

        contentArea.innerHTML = html;
      })
      .catch(err => {
        if (!contentArea.querySelector('h3')) {
          contentArea.innerHTML = `<div style="padding:20px; text-align:center; color:#ef4444;">서버 연결 확인 필요</div>`;
        }
      });
  }

  // 3. 실행 로직
  updateMedals(); // 즉시 한 번 실행
  setInterval(updateMedals, 5 * 60 * 1000); // 5분(300,000ms)마다 실행
})();