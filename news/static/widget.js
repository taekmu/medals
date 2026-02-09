(function () {
  // 스크립트가 삽입된 위치의 부모 요소를 찾습니다.
  const container = document.currentScript ? document.currentScript.parentElement : document.body;

  // 1. 초기 로딩 화면 표시
  container.innerHTML = `
    <div id="medal-loader" style="padding:40px 20px; text-align:center; color:#64748b; font-family:sans-serif; font-size:0.9rem;">
      <div style="font-size:2rem; margin-bottom:10px; animation: pulse 1.5s infinite;">📡</div>
      데이터를 불러오는 중입니다...
    </div>
    <style>@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }</style>`;

  // 2. 데이터 가져오기 (FastAPI 서버의 /medals 엔드포인트)
  fetch("/medals")
    .then(res => {
      if (!res.ok) throw new Error("서버 응답 오류");
      return res.json();
    })
    .then(data => {
      // 데이터가 비어있을 경우 처리
      if (!data || data.length === 0) {
        container.innerHTML = "<div style='padding:20px; text-align:center; font-family:sans-serif;'>현재 집계된 메달 데이터가 없습니다.</div>";
        return;
      }

      // 3. HTML 틀 만들기
      let html = `
        <div style="font-family: 'Pretendard', sans-serif; width: 100%; max-width: 400px; margin: 10px auto; background: #fff; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); overflow: hidden; border: 1px solid #f0f0f0;">
          <div style="background: linear-gradient(135deg, #2563eb, #1e40af); color: white; padding: 18px; text-align: center;">
            <h3 style="margin:0; font-size: 1.15rem; letter-spacing: -0.5px;">🏅 2026 동계 올림픽 순위</h3>
          </div>
          <div style="background: #f1f5f9; display: flex; padding: 8px 10px; font-size: 0.75rem; color: #64748b; font-weight: bold; text-align: center;">
            <div style="width: 35px;">순위</div>
            <div style="flex: 1; text-align: left; padding-left: 5px;">국가명</div>
            <div style="width: 30px;">금</div>
            <div style="width: 30px;">은</div>
            <div style="width: 30px;">동</div>
          </div>
          <div style="padding: 0 5px;">
      `;

      // 4. 반복문으로 국가별 행 추가
      data.forEach((team) => {
        // 서버에서 계산된 rank 사용 (공동 순위 대응)
        const rank = team.rank || "-";
        const country = team.country || "미정";
        const gold = team.gold || "0";
        const silver = team.silver || "0";
        const bronze = team.bronze || "0";

        html += `
          <div style="display: flex; align-items: center; padding: 12px 5px; border-bottom: 1px solid #f8fafc; transition: background 0.2s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
            <div style="width: 35px; text-align: center; font-weight: 800; color: ${rank <= 3 ? '#2563eb' : '#94a3b8'}; font-size: 0.95rem;">
              ${rank}
            </div>
            <div style="flex: 1; font-weight: 600; color: #1e293b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              ${country}
            </div>
            <div style="display: flex; gap: 4px; text-align: center; font-size: 0.9rem;">
              <div style="width: 30px; color: #d4af37; font-weight: 700;">${gold}</div>
              <div style="width: 30px; color: #94a3b8; font-weight: 700;">${silver}</div>
              <div style="width: 30px; color: #b45309; font-weight: 700;">${bronze}</div>
            </div>
          </div>
        `;
      });

      html += `
          </div>
          <div style="background: #f8fafc; padding: 12px; text-align: center; font-size: 0.75rem; color: #94a3b8; border-top: 1px solid #f1f5f9;">
            📡 위키피디아 실시간 데이터 연동 중
          </div>
        </div>
      `;

      // 5. 로더를 지우고 실제 표를 삽입
      container.innerHTML = html;
    })
    .catch(err => {
      console.error("Widget Error:", err);
      container.innerHTML = `
        <div style="padding:20px; text-align:center; color:#ef4444; font-family:sans-serif; font-size:0.85rem; border: 1px solid #fee2e2; border-radius:12px; background:#fef2f2;">
          <div style="font-size:1.5rem; margin-bottom:5px;">⚠️</div>
          데이터 연결에 실패했습니다.<br>
          <span style="font-size:0.75rem; color:#991b1b;">(${err.message})</span>
        </div>`;
    });
})();