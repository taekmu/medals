(function () {
  const container = document.currentScript.parentElement;

  fetch("https://medalboard.onrender.com/medals")
    .then(res => res.json())
    .then(data => {
      // 모바일 최적화 스타일 정의
      let html = `
        <div style="
          font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
          width: 100%;
          max-width: 100%;
          margin: 10px auto;
          background: #ffffff;
          border-radius: 20px;
          box-shadow: 0 8px 30px rgba(0,0,0,0.08);
          overflow: hidden;
          border: 1px solid #efefef;
          -webkit-tap-highlight-color: transparent;
        ">
          <div style="
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: white;
            padding: 18px 20px;
            text-align: left;
          ">
            <h3 style="margin:0; font-size: 1.15rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
              <span>🏅</span> 실시간 메달 순위...
            </h3>
            <p style="margin:4px 0 0; font-size: 0.75rem; opacity: 0.85;">실시간 자동 업데이트 중</p>
          </div>
          
          <div style="padding: 5px 0;">
      `;

      data.forEach((team, index) => {
        const isTop3 = index < 3;
        const medalColors = ['#FFD700', '#C0C0C0', '#CD7F32']; // 금, 은, 동 색상
        
        html += `
          <div style="
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: ${index === data.length - 1 ? 'none' : '1px solid #f8f9fa'};
            transition: background 0.2s;
          " onclick="this.style.background='#f0f4ff'; setTimeout(()=>this.style.background='transparent', 200);">
            
            <span style="
              width: 28px; 
              font-weight: 800; 
              color: ${isTop3 ? '#1e293b' : '#94a3b8'};
              font-size: 1rem;
            ">${index + 1}</span>
            
            <div style="flex: 1; font-weight: 600; color: #334155; margin-left: 10px; font-size: 1rem;">
              ${team.country}
            </div>
            
            <div style="display: flex; gap: 10px; text-align: center;">
              <div style="width: 32px;">
                <div style="font-weight: 700; color: #d4af37; font-size: 1.05rem;">${team.gold}</div>
                <div style="font-size: 0.65rem; color: #94a3b8; margin-top: 1px;">금</div>
              </div>
              <div style="width: 32px;">
                <div style="font-weight: 700; color: #94a3b8; font-size: 1.05rem;">${team.silver}</div>
                <div style="font-size: 0.65rem; color: #94a3b8; margin-top: 1px;">은</div>
              </div>
              <div style="width: 32px;">
                <div style="font-weight: 700; color: #b45309; font-size: 1.05rem;">${team.bronze}</div>
                <div style="font-size: 0.65rem; color: #94a3b8; margin-top: 1px;">동</div>
              </div>
            </div>
          </div>
        `;
      });

      html += `
          </div>
          <div style="
            background: #f1f5f9;
            padding: 16px;
            text-align: center;
            font-size: 0.9rem;
            color: #2563eb;
            cursor: pointer;
            font-weight: 700;
            border-top: 1px solid #e2e8f0;
          " onclick="alert('전체 순위 페이지로 이동합니다')">
            전체 순위 더보기
          </div>
        </div>
      `;

      container.innerHTML = html;
    })
    .catch(err => {
      container.innerHTML = `
        <div style='padding:40px 20px; text-align:center; color:#64748b; font-size:0.9rem;'>
          <div style='font-size:2rem; margin-bottom:10px;'>📡</div>
          데이터를 연결하는 중입니다...
        </div>`;
    });
})();