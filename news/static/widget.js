(function () {
  // 스크립트가 삽입된 위치의 부모 요소를 찾습니다.
  const container = document.currentScript ? document.currentScript.parentElement : document.body;

  // 1. 초기 로딩 화면 표시
  container.innerHTML = `
    <div id="medal-loader" style="padding:40px 20px; text-align:center; color:#64748b; font-size:0.9rem;">
      <div style="font-size:2rem; margin-bottom:10px;">📡</div>
      데이터를 불러오는 중입니다...
    </div>`;

  // 2. 데이터 가져오기 (상대 경로 /medals 사용)
  fetch("/medals")
    .then(res => {
      if (!res.ok) throw new Error("서버 응답 오류");
      return res.json();
    })
    .then(data => {
      // 데이터가 비어있을 경우 처리
      if (!data || data.length === 0) {
        container.innerHTML = "<div style='padding:20px; text-align:center;'>표시할 메달 데이터가 없습니다.</div>";
        return;
      }

      // 3. HTML 틀 만들기
      let html = `
        <div style="font-family: sans-serif; width: 100%; max-width: 400px; margin: 10px auto; background: #fff; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #eee;">
          <div style="background: #2563eb; color: white; padding: 15px; text-align: center;">
            <h3 style="margin:0; font-size: 1.1rem;">🏅 실시간 메달 순위</h3>
          </div>
          <div style="padding: 10px;">
      `;

      // 4. 반복문으로 국가별 행 추가
      data.forEach((team, index) => {
        // 혹시 서버에서 데이터가 깨져서 올 경우를 대비해 기본값('0') 설정
        const country = team.country || "미정";
        const gold = team.gold || "0";
        const silver = team.silver || "0";
        const bronze = team.bronze || "0";

        html += `
          <div style="display: flex; align-items: center; padding: 12px 10px; border-bottom: 1px solid #f0f0f0;">
            <span style="width: 25px; font-weight: bold; color: #666;">${index + 1}</span>
            <div style="flex: 1; font-weight: bold; color: #333;">${country}</div>
            <div style="display: flex; gap: 8px; text-align: center; font-size: 0.9rem;">
              <div style="width: 30px;"><div style="color: #d4af37; font-weight: bold;">${gold}</div></div>
              <div style="width: 30px;"><div style="color: #94a3b8; font-weight: bold;">${silver}</div></div>
              <div style="width: 30px;"><div style="color: #b45309; font-weight: bold;">${bronze}</div></div>
            </div>
          </div>
        `;
      });

      html += `
          </div>
          <div style="background: #f8fafc; padding: 10px; text-align: center; font-size: 0.8rem; color: #94a3b8;">
            자동 업데이트 활성화됨
          </div>
        </div>
      `;

      // 5. 로더를 지우고 실제 표를 삽입
      container.innerHTML = html;
    })
    .catch(err => {
      console.error("Widget Error:", err);
      container.innerHTML = `
        <div style="padding:20px; text-align:center; color:#ef4444; font-size:0.85rem;">
          ⚠️ 연결 실패: ${err.message}<br>잠시 후 새로고침 해주세요.
        </div>`;
    });
})();