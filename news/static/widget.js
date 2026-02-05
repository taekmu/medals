/*(function () {  
    const container = document.currentScript.parentElement;

  fetch("http://127.0.0.1:8000/medals")
    .then(res => res.json())
    .then(data => {

      let html = `
        <div style="
          font-family:sans-serif;
          border:1px solid #ddd;
          padding:10px;
          width:260px;
          background:#fafafa">

          <h3>🏅 실시간 메달보드</h3>
          <table style="width:100%">
            <tr>
              <th>국가</th>
              <th>🥇</th>
              <th>🥈</th>
              <th>🥉</th>
            </tr>
      `;

      data.forEach(team => {
        html += `
          <tr>
            <td>${team.country}</td>
            <td>${team.gold}</td>
            <td>${team.silver}</td>
            <td>${team.bronze}</td>
          </tr>
        `;
      });

      html += "</table></div>";

      container.innerHTML = html;
    })
    .catch(err => {
      container.innerHTML = "메달 데이터를 불러올 수 없습니다";
    });

})();

*/

(function () {
  const container = document.currentScript.parentElement;

  fetch("https://medalboard.onrender.com/medals")
    .then(res => res.json())
    .then(data => {
      // 스타일 정의
      let html = `
        <div style="
          font-family: 'Pretendard', sans-serif;
          max-width: 350px;
          background: #ffffff;
          border-radius: 16px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1);
          overflow: hidden;
          border: 1px solid #eee;
        ">
          <div style="
            background: linear-gradient(135deg, #1a73e8, #0d47a1);
            color: white;
            padding: 20px;
            text-align: center;
          ">
            <h3 style="margin:0; font-size: 1.2rem; letter-spacing: -0.5px;">🏅 실시간 메달 순위</h3>
            <p style="margin:5px 0 0; font-size: 0.8rem; opacity: 0.8;">최종 업데이트: 방금 전</p>
          </div>
          
          <div style="padding: 10px 0;">
      `;

      data.forEach((team, index) => {
        const isFirst = index === 0;
        html += `
          <div style="
            display: flex;
            align-items: center;
            padding: 12px 20px;
            border-bottom: ${index === data.length - 1 ? 'none' : '1px solid #f5f5f5'};
            background: ${isFirst ? '#fff9c433' : 'transparent'};
          ">
            <span style="
              width: 25px; 
              font-weight: bold; 
              color: ${index < 3 ? '#ff9800' : '#999'};
              font-size: 1.1rem;
            ">${index + 1}</span>
            
            <div style="flex: 1; font-weight: 600; color: #333; margin-left: 10px;">
              ${team.country}
            </div>
            
            <div style="display: flex; gap: 12px; text-align: center;">
              <div style="width: 30px;">
                <div style="font-size: 0.7rem; color: #aaa; margin-bottom: 2px;">금</div>
                <div style="font-weight: 700; color: #d4af37;">${team.gold}</div>
              </div>
              <div style="width: 30px;">
                <div style="font-size: 0.7rem; color: #aaa; margin-bottom: 2px;">은</div>
                <div style="font-weight: 700; color: #aaa;">${team.silver}</div>
              </div>
              <div style="width: 30px;">
                <div style="font-size: 0.7rem; color: #aaa; margin-bottom: 2px;">동</div>
                <div style="font-weight: 700; color: #cd7f32;">${team.bronze}</div>
              </div>
            </div>
          </div>
        `;
      });

      html += `
          </div>
          <div style="
            background: #f8f9fa;
            padding: 10px;
            text-align: center;
            font-size: 0.85rem;
            color: #1a73e8;
            cursor: pointer;
            font-weight: bold;
          ">
            전체 순위 더보기 >
          </div>
        </div>
      `;

      container.innerHTML = html;
    })
    .catch(err => {
      container.innerHTML = "<div style='padding:20px; color:#666;'>데이터를 불러오는 중입니다...</div>";
    });
})();
