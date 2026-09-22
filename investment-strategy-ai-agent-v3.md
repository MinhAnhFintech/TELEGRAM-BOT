# COMPREHENSIVE AI AGENT SPECIFICATION: INVESTMENT STRATEGIES & FINANCIAL ALGORITHMS (V3)

> **Document Type:** AI System Architecture & Algorithmic Trading Specification  
> **Source Material:** *Chiến Lược Đầu Tư Chứng Khoán - Phương Pháp và Chiến Thuật Thành Công* (PDF)  
> **Target Execution Engine:** Quant Investment AI Agent (Autonomous Trading, Screening & Portfolio Management)

---

## 1. ARCHITECTURAL OVERVIEW & 3-STEP INVESTMENT PROCESS

Mọi chiến lược trong sách đều vận hành dựa trên **Quy trình Đầu tư 3 Bước Standard (Standard 3-Step Investment Framework)**. AI Agent phải thực thi tuần tự 3 bước này cho từng khung thời gian đầu tư.

```
+-----------------------------------------------------------------------+
|                       STEP 1: STOCK SCREENING                         |
|   (Sàng lọc Cổ phiếu theo Chỉ số Cơ bản, Định giá hoặc Kỹ thuật)      |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    STEP 2: BUY/SELL TIMING ENGINE                     |
|    (Tính toán Thời điểm Mua/Bán theo Chỉ báo & Mô hình Kỹ thuật)       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                  STEP 3: PORTFOLIO & RISK MANAGEMENT                  |
|    (Phân bổ Vốn, Đa dạng hóa, Dừng lỗ Tự động & Bảo vệ Lợi nhuận)     |
+-----------------------------------------------------------------------+
```

---

## 2. MODULE 1: CHIẾN LƯỢC NGẮN HẠN - DƯỚI 3 THÁNG (CL1)
* **Khung thời gian nắm giữ:** Từ vài ngày đến dưới 90 ngày.
* **Tần suất theo dõi:** Hằng ngày (Daily Monitoring).
* **Đặc tính Tâm lý/PQ Score:** Yêu cầu Chịu bất ổn/Rủi ro cao (Score 9/10), Cam kết thời gian cao (Score 10/10), Kỷ luật tuyệt đối (Score 10/10).

### 2.1. Momentum Investing Agent (Đầu tư theo Đà tăng trưởng - Quy tắc 80/20)
* **Triết lý cốt lõi:** Cổ phiếu tăng trưởng mạnh tuân theo quy tắc **80/20** (đạt 80% mức tăng giá trong 20% thời gian bùng nổ).
* **Bộ lọc Sàng lọc (Screener Logic):**
  1. **Top-Down Sector Filter:** Lọc top 10%–20% nhóm ngành có mức tăng giá mạnh nhất trong tuần/tháng (sử dụng xếp hạng nhóm ngành IBD).
  2. **Volume Surge Condition:**
     $$	ext{Volume Ratio 1} = rac{	ext{Volume}_{	ext{Today}}}{	ext{Volume}_{	ext{Average 30D}}} \ge 1.5$$
     $$	ext{Volume Ratio 2} = rac{	ext{Volume}_{	ext{Average 5D}}}{	ext{Volume}_{	ext{Average 90D}}} \ge 1.3$$
  3. **Base Pattern Breakout Condition:** Cổ phiếu giao dịch tích lũy trong biên độ giá hẹp (Base Pattern - ví dụ AmeriCredit $34–$36) chuẩn bị bùng nổ.
* **Tín hiệu Mua (Entry Signal):**
  * Giá bùng nổ phá vỡ đỉnh của mô hình tích lũy nền giá (Base Pattern Breakout) kèm khối lượng tăng đột biến.
  * Hoặc xuất hiện tín hiệu giao cắt tích cực của MACD, Stochastics thoát vùng quá bán, hoặc RSI cắt lên đường 50.
* **Tín hiệu Bán & Quản trị Rủi ro (Exit & Risk Rules):**
  * **Trailing Stop Loss 10%:** Đặt lệnh cảnh báo bán tự động (Email/Stop Loss Alert). Khi giá cổ phiếu tăng, nâng dần giá dừng lỗ sao cho luôn duy trì **trong vòng 10%** so với đỉnh giá hiện tại để bảo vệ lợi nhuận.
  * **Cut Losses Fast:** Cắt lỗ máy móc ngay lập tức khi cổ phiếu giảm vi phạm điểm gia nhập, ngăn chặn khoản lỗ nhỏ biến thành khoản lỗ lớn. Bán ngay khi xuất hiện tín hiệu kỹ thuật tiêu cực mà không cần bận tâm đến lý do cơ bản.

### 2.2. Technical Charting Agent (Đầu tư / Giao dịch Kỹ thuật Thuần túy)
* **Triết lý cốt lõi:** Bỏ qua hoàn toàn chỉ số cơ bản (P/E, BCTCK, ban quản trị); giả định mọi thông tin đã phản ánh vào giá. Nhắm tới "Bằng chứng rõ ràng" (Evident Proof - Martin Pring).
* **Bộ chỉ báo & Ngưỡng kỹ thuật (Indicators & Metrics):**
  * **Moving Averages (MA):** MA 50 ngày (xu hướng trung hạn), MA 200 ngày (xu hướng dài hạn), Crossover MA 50/200.
  * **MACD (Moving Average Convergence Divergence):** Đường MACD và Đường Tín hiệu (Signal Line) theo khung Daily/Weekly.
  * **RSI (Relative Strength Index) & Stochastics:** Xác định điểm cạn kiệt đà tăng/giảm và vùng đảo chiều.
  * **Bollinger Bands:** Theo dõi hiện tượng "đám đông chen lấn" (Squeeze - dải Bollinger thu hẹp) để đón đầu biến động mạnh.
* **Tín hiệu Mua (Entry Signal):**
  * Giá cắt lên trên đường MA 50 ngày hoặc MA 200 ngày.
  * Đường MACD cắt lên đường Tín hiệu (Bullish Crossover).
  * Bollinger Bands mở rộng sau giai đoạn Squeeze kèm khối lượng tăng đột biến.
* **Tín hiệu Bán (Exit Signal):**
  * Giá cắt xuống dưới đường MA 50 ngày hoặc MA 200 ngày.
  * MACD cắt xuống (Bearish Crossover).
  * **Mô hình Đỉnh Tiêu cực (Volume-Price Divergence):** Giá tiếp tục tăng nhưng khối lượng giao dịch giảm dần (tín hiệu mua dựa trên lợi nhuận cạn kiệt, nhà phân tích đứng sang một bên) $ightarrow$ Bán ngay lập tức trước đợt sụt giảm mạnh.

### 2.3. Active Trading & Day Trading Agent (Giao dịch Chủ động trong ngày)
* **Khung thời gian:** Phút, giờ, ngày.
* **Thực thi:** Tận dụng các đợt tăng giá ngắn hạn, yêu cầu chịu bất ổn cực cao và kỷ luật cắt lỗ tự động từng phút.

### 2.4. Style Surfing Agent (Lướt sóng Phong cách)
* **Thực thi:** Luân chuyển tỷ trọng vốn liên tục giữa 4 nhóm phong cách (Giá trị, Tăng trưởng, Đà tăng trưởng, Quy mô vốn hóa Large/Small-cap) dựa trên chỉ số dòng tiền thị trường hằng ngày/hàng tuần.

---

## 3. MODULE 2: CHIẾN LƯỢC TRUNG HẠN - TỪ 3–12 THÁNG (CL2)
* **Khung thời gian nắm giữ:** Từ 90 ngày đến 365 ngày.
* **Tần suất theo dõi:** Định kỳ theo quý (Quarterly Rebalancing) sau các đợt công bố Báo cáo Tài chính Quý (10-Q).

### 3.1. Growth & GARP Investing Agent (Đầu tư Tăng trưởng & GARP - Peter Lynch Rule)
* **Tiêu chuẩn Cơ bản Cốt lõi (Fundamental Criteria):**
  1. Tỷ lệ tăng trưởng lợi nhuận (EPS) và Doanh thu cao bền vững: **15% – 30%+ / năm** trong 3–5 năm quá khứ và dự báo 3–5 năm tới.
  2. High Revenue Growth Filter: Đối với ngành công nghệ cao/sinh học, doanh thu tăng trưởng nhanh là yếu tố quan trọng hàng đầu dù lợi nhuận hiện tại chưa cao.
  3. **Bộ 3 Yếu tố Tăng trưởng:** Công ty phải đạt đủ 3 tiêu chuẩn: (1) Thương hiệu mạnh, (2) Quản lý hiệu quả, (3) Công nghệ dẫn đầu.
* **Công thức Định giá GARP (Growth At a Reasonable Price Metrics):**
  $$	ext{PEG Ratio} = rac{	ext{P/E Current}}{	ext{Tỷ lệ tăng trưởng EPS dự kiến (3-5 năm)}}$$
  * **Môi trường Lãi suất Bình thường:** $	ext{PEG} \le 1.0$ (Mức giá P/E trả không quá 1.0 lần tỷ lệ tăng trưởng EPS. Ví dụ: Cổ phiếu tăng trưởng 20%/năm thì P/E không quá 20).
  * **Môi trường Lãi suất Thấp:** $	ext{PEG} \le 1.5$ (Mức giá P/E trả không quá 1.5 lần tỷ lệ tăng trưởng EPS. Ví dụ: Cổ phiếu tăng trưởng 20%/năm thì P/E tối đa 30).
  * **Red Flag Exclusion (Loại bỏ):** Tẩy chay cổ phiếu có P/E gấp 3–4 lần tỷ lệ tăng trưởng EPS (Hội chứng "Kẻ ngốc hơn" - More Fool Syndrome).
* **Quy trình Kiểm tra Quý (Quarterly Audit & Checklist Engine):**
  * Đánh giá lại danh mục sau mỗi báo cáo 10-Q và các con số rò rỉ (Whisper Numbers).
  * Bảng chấm điểm Mua/Bán Quý:
    * Tin tức doanh nghiệp: Tin tốt $ightarrow$ Mua; Tin xấu $ightarrow$ Bán.
    * Giao dịch nội bộ: Mua nhiều hơn Bán $ightarrow$ Mua; Bán nhiều hơn Mua $ightarrow$ Bán.
    * Xếp hạng Nhóm ngành (IBD Group Rank): Trên trung bình $ightarrow$ Mua; Dưới trung bình $ightarrow$ Bán.
* **Xác định Thời điểm Mua/Bán Kỹ thuật (Technical Alignment):**
  * **Entry Confirmation:** Chỉ mua cổ phiếu GARP khi kỹ thuật đồng nhất — Giá vượt trên đường MA 50 ngày và MACD hàng tuần chuyển sang vùng tích cực.
  * **Profit Protection:** Thiết lập tự động Email Alert / Stop Loss duy trì khoảng cách **10%** dưới giá thị trường khi cổ phiếu tăng.
  * **Exit Execution:** Bán ra khi giá rơi xuống dưới MA 50 ngày (ví dụ Cisco tháng 4/2000), MACD hàng tuần tiêu cực, hoặc khi doanh thu/lợi nhuận suy giảm qua các quý.

### 3.2. CANSLIM Agent (Đầu tư Tăng trưởng & Tăng tốc - William J. O'Neil)
* **Bộ lọc 7 Tiêu chí CANSLIM:**
  * **C (Current Quarterly Earnings):** EPS quý hiện tại tăng trưởng $\ge 18\% - 25\%+$ so với cùng kỳ năm trước.
  * **A (Annual Earnings Growth):** EPS hàng năm tăng trưởng liên tục trong 3–5 năm ($\ge 25\%/năm$).
  * **N (New Products, Management, Highs):** Sản phẩm mới, ban quản lý mới, hoặc Giá bùng nổ lập Đỉnh cao 52 tuần mới từ nền giá tích lũy.
  * **S (Supply and Demand):** Cung - Cầu cổ phiếu; Khối lượng giao dịch tăng vọt (từ +50% đến +100%+) tại ngày breakout.
  * **L (Leader or Laggard):** Chỉ chọn Cổ phiếu Dẫn đầu ngành, chỉ số Sức mạnh Tương đối RS (Relative Strength) $\ge 80$.
  * **I (Institutional Sponsorship):** Có sự tham gia sở hữu của ít nhất một vài tổ chức/quỹ đầu tư uy tín.
  * **M (Market Direction):** Xu hướng thị trường chung đang ở trạng thái Tăng giá (Uptrend).
* **Quy tắc Cắt lỗ Kỷ luật:** Cắt lỗ máy móc tuyệt đối khi khoản đầu tư giảm **7% – 8%** so với giá mua, không có ngoại lệ.

---

## 4. MODULE 3: CHIẾN LƯỢC DÀI HẠN - TRÊN 12 THÁNG (CL3)
* **Khung thời gian nắm giữ:** Ít nhất 1 năm đến nhiều năm.
* **Tần suất theo dõi:** Kiểm tra hằng năm (Annual Review) hoặc hằng tháng.

### 4.1. Value Investing Agent (Đầu tư Giá trị)
* **Triết lý cốt lõi:** Săn cổ phiếu hời (GABP - Growth At a Bargain Price) bị thị trường định giá thấp hơn giá trị nội tại thực tế.
* **Định nghĩa & Ngưỡng Chỉ số (Valuation Metrics):**
  * $P/E_{	ext{Current}} < 	ext{Tỷ lệ tăng trưởng EPS dự kiến}$.
  * Relative P/E: $P/E_{	ext{Current}} < P/E_{	ext{Historical Average}}$ của chính công ty đó.
  * Sector P/E: $P/E_{	ext{Current}} \le P/E_{	ext{Industry Average}}$ hoặc $S\&P 500$.
* **Cảnh báo Bẫy Giá trị (Value Trap Warning):** Phân biệt cổ phiếu giá trị thực sự với "Bẫy giá trị" (Value Trap - cổ phiếu P/E thấp do dòng sản phẩm suy giảm hoặc triển vọng kinh doanh đi xuống).
* **Tín hiệu Mua đảo chiều (Buy Signal):**
  * Không mua khi cổ phiếu đang rơi do tin xấu. Chỉ mua khi xuất hiện dấu hiệu đảo chiều/phục hồi niềm tin.
  * Dấu hiệu: MACD hàng tháng (Monthly MACD) cắt lên tích cực, Crossover MA 50 ngày cắt lên MA 200 ngày, hoặc giá vượt đường Kháng cự Dài hạn (Long-term Resistance).
* **Tín hiệu Bán (Exit Signal):** Bán khi thị trường nhận ra và khôi phục đầy đủ giá trị cổ phiếu, MACD hàng tuần/tháng tiêu cực, hoặc giá cắt xuống đường kháng cự/hỗ trợ dài hạn.

### 4.2. Asset-Based Fundamental Agent (Đầu tư Cơ bản Dựa trên Tài sản)
* **Bộ lọc Sàng lọc Tài sản:**
  * $P/B$ (Price to Book Value) ở mức rất thấp.
  * Tỷ lệ Tiền mặt / Giá trị vốn hóa cao ($	ext{Cash / Market Cap} > 	ext{High}$).
  * Mức nợ thấp, sở hữu tài sản cố định có giá trị thực tế lớn.
* **Thuật toán Kiểm toán BCTCK (Balance Sheet Audit Engine):**
  * So sánh Tốc độ tăng Doanh thu ($\Delta 	ext{Revenue}$) với Tốc độ tăng Khoản phải thu ($\Delta 	ext{Accounts Receivable}$) và Hàng tồn kho ($\Delta 	ext{Inventory}$).
  * **Cảnh báo Rủi ro (Red Flag Alert):** Nếu **Số ngày thu tiền tồn đọng (DSO - Days Sales Outstanding)** tăng hoặc Hàng tồn kho tăng nhanh hơn Doanh thu $ightarrow$ Phát hiện nguy cơ ứ đọng vốn / rủi ro tín dụng $ightarrow$ Bán / Loại bỏ khỏi danh mục ngay lập tức.

### 4.3. Dividend Growth Agent (Đầu tư Tăng trưởng Cổ tức)
* **Screener:** Doanh nghiệp quy mô lớn, dòng tiền ổn định, có lịch sử **tăng trưởng cổ tức liên tục từng quý/năm trong 5–10 năm liên tiếp** (ví dụ: Conagra Foods CAG).
* **Mục tiêu:** Nhận dòng tiền cổ tức tăng trưởng đều đặn kết hợp cơ hội tăng giá tài sản dài hạn.

### 4.4. Buy and Hold Agent (Chiến lược Mua và Giữ)
* **Thực thi:** Nắm giữ danh mục cổ phiếu hàng đầu xuyên suốt qua nhiều năm, bỏ qua biến động ngắn hạn để đạt mức lợi nhuận bình quân lịch sử 10%–14%/năm.

---

## 5. MODULE 4: CHIẾN LƯỢC ĐẶC BIỆT & THỊ TRƯỜNG TRUNG LẬP (MARKET-NEUTRAL & HEDGING)

### 5.1. Insider Trading Tracking Agent (Theo dõi Giao dịch Nội bộ)
* **Thang điểm ThomsonFN Insider Score:** Theo dõi điểm số giao dịch nội bộ (Score $\ge 60$).
* **Quy tắc Mua/Bán:**
  * Mua khi số lượng mua của thành viên nội bộ tăng mạnh (đặc biệt là Giám đốc Tài chính - CFO, người bảo thủ nhất về tài chính). Đây là dấu hiệu cổ phiếu bị định giá thấp trước 6 tháng.
  * Bán khi thành viên nội bộ bán tháo diện rộng.

### 5.2. Top-Down Sector Rotation Agent (Xoay chuyển Nhóm ngành từ trên xuống)
* **Thực thi:** Theo dõi bảng xếp hạng nhóm ngành hàng tuần/hàng tháng (IBD Industry Group Rank), luân chuyển vốn vào các ngành bắt đầu thu hút dòng tiền.

### 5.3. Market-Neutral & Pair Trading Agent (Thị trường Trung lập & Giao dịch Cặp đôi)
* **Nguyên lý:** Đồng thời mở vị thế Mua (Long) và Bán khống (Short) để triệt tiêu rủi ro biến động toàn thị trường.
* **Giao dịch Cặp đôi (Pair Trading):**
  * Chọn 2 cổ phiếu đối lập trong cùng ngành (ví dụ Dell / Gateway, Intel / KLAC).
  * **Long** cổ phiếu mạnh/định giá thấp + **Short** cổ phiếu yếu/định giá cao.
* **Phân bổ Vốn theo Xác suất:** Nếu dự báo thị trường có 70% khả năng tăng $ightarrow$ Phân bổ 70% vốn cho Long và 30% vốn cho Short.

### 5.4. Option Hedging Agent (Bảo hiểm Vị thế bằng Quyền chọn Bán - Put Option)
* **Bảo vệ Cổ phiếu Đơn lẻ:** Mua **Put Option** (At-the-money hoặc Out-of-the-money) cho cổ phiếu nắm giữ để giới hạn mức lỗ tối đa với chi phí cố định thấp thay vì bán khống trực tiếp.
* **Bảo vệ Toàn bộ Danh mục:** Mua **Index Put Option (ví dụ OEX S&P 100 Put Option)** để phòng hộ cho toàn bộ danh mục dài hạn khi thị trường có rủi ro sụt giảm mạnh.

---

## 6. MODULE 5: PORTFOLIO MANAGEMENT & RISK ENGINE

1. **Phân bổ Vốn & Số lượng Cổ phiếu:**
   * Ngắn hạn (Dưới 3 tháng): Tập trung 4–5 cổ phiếu dẫn đầu.
   * Trung/Dài hạn: Đa dạng hóa hợp lý qua các nhóm ngành không tương quan.
2. **Dự trữ Tiền mặt (Cash Ratio):** Duy trì **10%–30% tiền mặt** khi thị trường chung có dấu hiệu đạt đỉnh hoặc định giá P/E toàn thị trường ở mức quá cao.
3. **Kỷ luật Loại bỏ Cảm xúc:** Thiết lập toàn bộ quy tắc cắt lỗ, dừng lỗ tự động trên hệ thống máy tính; tuyệt đối không can thiệp bằng cảm xúc hay trực giác.

---
*End of AI Specification V3*
