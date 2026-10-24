import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_header_callout(doc, text, bold_prefix=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1B365D"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        r_b.font.name = "Times New Roman"
        r_b.font.size = Pt(10.5)
        r_b.font.bold = True
        r_b.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(10.5)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def format_run(run, font_name="Times New Roman", size_pt=11, bold=False, italic=False, color_rgb=(0x22, 0x22, 0x22)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_p(doc, text="", font_name="Times New Roman", size_pt=11, bold=False, italic=False, color_rgb=(0x22, 0x22, 0x22), align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        r = p.add_run(text)
        format_run(r, font_name, size_pt, bold, italic, color_rgb)
    return p

def add_h1(doc, text):
    return add_p(doc, text, font_name="Times New Roman", size_pt=15, bold=True, color_rgb=(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6)

def add_h2(doc, text):
    return add_p(doc, text, font_name="Times New Roman", size_pt=13, bold=True, color_rgb=(0x2B, 0x6C, 0xB0), align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4)

def add_h3(doc, text):
    return add_p(doc, text, font_name="Times New Roman", size_pt=11.5, bold=True, italic=True, color_rgb=(0x2D, 0x37, 0x48), align=WD_ALIGN_PARAGRAPH.LEFT, space_before=6, space_after=2)

def add_bullet(doc, bold_prefix="", text=""):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_b = p.add_run(bold_prefix)
        format_run(r_b, font_name="Times New Roman", size_pt=10.5, bold=True, color_rgb=(0x1B, 0x36, 0x5D))
    if text:
        r = p.add_run(text)
        format_run(r, font_name="Times New Roman", size_pt=10.5, color_rgb=(0x22, 0x22, 0x22))
    return p

def add_image_with_caption(doc, img_path, caption_text, width_inch=5.5):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        r_img = p_img.add_run()
        r_img.add_picture(img_path, width=Inches(width_inch))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        r_cap = p_cap.add_run(caption_text)
        format_run(r_cap, font_name="Times New Roman", size_pt=9.5, italic=True, color_rgb=(0x55, 0x55, 0x55))

def create_document():
    doc = docx.Document()
    
    # 1 inch margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)

    # Header / Title
    p_meta = add_p(doc, "BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU KHOA HỌC — ĐỀ TÀI TRAVEL PLANNING AGENT", size_pt=9.5, bold=True, color_rgb=(0x71, 0x80, 0x96), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    p_title = add_p(doc, "Weekly report – Travel planning agent in Viet Nam", size_pt=18, bold=True, color_rgb=(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=4)
    p_sub = add_p(doc, "Đánh giá Thực trạng LLM Agents trên Benchmark TravelPlanner (ICML 2024), Giải phẫu Hệ thống Lỗi và Định hướng Bản địa hóa cho Thị trường Du lịch Việt Nam", size_pt=11.5, italic=True, color_rgb=(0x4A, 0x55, 0x68), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    p_author = add_p(doc, "Nguyễn Tiến Hoàng * Lê Minh Đức *", size_pt=11, bold=True, color_rgb=(0x2B, 0x6C, 0xB0), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    p_unit = add_p(doc, "CLB Lập Trình PTIT (PROPTIT) & Học viện Công nghệ Bưu chính Viễn thông — Tháng 10/2026", size_pt=9.5, italic=True, color_rgb=(0x71, 0x80, 0x96), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    # 1. Mở đầu & Đặt vấn đề
    add_h1(doc, "1. Mở đầu & Đặt vấn đề (Introduction & Motivation)")
    
    add_p(doc, "Việt Nam đang dần trở thành một quốc gia du lịch nổi tiếng, là lựa chọn không thể làm ngơ cho các du khách quốc tế và thậm chí cả người Việt. Bằng chứng từ Cục Du lịch Quốc gia Việt Nam cho thấy lượt khách du lịch nội địa tính từ năm 2022 đến 2025 tăng mạnh từ 101,3 triệu lượt lên tới hơn 110 triệu lượt mỗi năm. Theo thời gian, các khu du lịch được quy hoạch và thành lập ngày một nhiều, đi cùng với đó là mạng lưới dịch vụ lưu trú, ẩm thực và trải nghiệm địa phương phát triển bùng nổ xung quanh.")
    
    add_p(doc, "Từ đây ta thấy được một vấn đề tồn đọng len lỏi trong các ý định du lịch của mọi người: đa số chúng ta khi muốn đi du lịch, khám phá và trải nghiệm ở những địa điểm trong nước mà mình chưa biết hoặc chưa từng đi bao giờ đều sẽ phải dành ra rất nhiều thời gian để tự tay lên kế hoạch. Tuy nhiên, kế hoạch du lịch tự lập đó của bản thân rất hiếm khi hoàn hảo vì nhiều lý do. Đa số sự thất bại trong kế hoạch lên sẵn đều xuất phát từ việc thiếu hụt và bất đối xứng thông tin:")
    
    add_bullet(doc, "Bất cập về dịch vụ lưu trú: ", "Tại khách sạn A không có chỗ vệ sinh cho thú cưng dù trên Google Maps hay OTA lại miêu tả là cho phép mang thú cưng, hoặc phụ thu đột xuất khi nhận phòng.")
    add_bullet(doc, "Bất cập về lựa chọn di chuyển: ", "Để bay từ Hà Nội vào Đà Nẵng, du khách chọn vé VietJet thay vì Vietnam Airlines vì giá niêm yết ban đầu rẻ hơn, nhưng sau khi cộng hành lý ký gửi và thời gian chờ trễ chuyến thì chi phí thực tế lại đắt hơn mà dịch vụ không tương xứng.")
    add_bullet(doc, "Xung đột lịch trình và thời gian: ", "Điểm tham quan đóng cửa vào ngày thứ Hai, hoặc khoảng cách di chuyển thực tế giữa hai địa điểm trong giờ cao điểm vượt xa ước tính lý thuyết của bản đồ trực tuyến.")

    add_p(doc, "Hiện nay ta đã có các AI mới và rất thông minh. Nhưng nếu ngay bây giờ ta prompt cho chúng các yêu cầu siêu chi tiết về một chuyến đi với hàng tá các ràng buộc chồng chéo (ngân sách trần, khẩu vị ăn uống, quy định số đêm lưu trú, loại phòng, thời gian bay), những thông tin mà chúng đưa ra chưa chắc đã sát với sự thật. Mô hình có xu hướng 'làm mềm' hoặc âm thầm bóp méo dữ liệu thực tế để thỏa mãn câu lệnh đầu vào:")
    
    add_bullet(doc, "Hiện tượng Ảo giác (Hallucination) và Bóp méo thực tế: ", "Tình trạng HALU dữ liệu này ta rất thường thấy ở các LLM lớn. Khi bí thông tin, mô hình tự bịa ra số hiệu chuyến bay không tồn tại, tự hạ giá phòng khách sạn trên giấy, hoặc xếp lịch trình cho du khách di chuyển giữa hai thành phố cách nhau 500 km chỉ trong… 1 giờ đồng hồ để kịp lịch trình.")
    add_bullet(doc, "Thách thức Tối ưu hóa Tổ hợp Đa ràng buộc: ", "Lập kế hoạch du lịch không phải là bài toán sinh văn bản đơn thuần mà là bài toán tối ưu hóa tổ hợp có ràng buộc toàn cục (combinatorial constrained optimization). Các nghiên cứu của Huang et al. (2023) và Valmeekam et al. (2023) đã chỉ ra rằng các LLM dù rất giỏi sinh ngôn ngữ nhưng cực kỳ yếu kém trong việc duy trì tính nhất quán logic trên một chuỗi hành động dài hạn.")

    add_p(doc, "Để giải quyết khoảng trống đánh giá này, nhóm nghiên cứu từ OSU NLP Group đã giới thiệu TravelPlanner tại hội nghị ICML 2024 (Rank A*). TravelPlanner là bộ công cụ benchmark tiêu chuẩn đầu tiên trên thế giới mô phỏng môi trường du lịch thế giới thực trên một sandbox đóng (closed sandbox gồm hơn 4 triệu bản ghi dữ liệu thực tế tại Mỹ) và xây dựng hệ thống đánh giá tự động đa tầng (Environment, Commonsense, Hard Constraints).")

    add_header_callout(doc, 
        "Bài báo cáo tuần này nhằm đánh giá trực tiếp vào các mô hình AI lớn vào năm 2026 (Gemini 3.8 Flash High, Gemini 3.8 Flash Low, Gemini 3.1 Pro Low, Claude Sonnet 4.5), so sánh chỉ số giữa các mô hình, tìm hiểu nguyên nhân tác động đến chỉ số đánh giá, giải phẫu từng họ lỗi theo phân loại của bài báo và đi tìm điểm hạn chế của TravelPlanner trước khi chính thức áp dụng công cụ vào cụ thể môi trường du lịch tại Việt Nam.", 
        "Mục tiêu Báo cáo: ")

    # 2. Tổng quan Nghiên cứu Liên quan (Related Work)
    add_h1(doc, "2. Tổng quan Nghiên cứu Liên quan (Related Work)")
    
    add_p(doc, "Nghiên cứu về đại lý lập kế hoạch du lịch tự hành giao thoa giữa ba trụ cột chính trong lĩnh vực Trí tuệ Nhân tạo hiện đại:")
    
    add_h2(doc, "2.1. Tự trị dựa trên LLM và Tương tác Công cụ (LLM-based Autonomous Agents & Tool-use)")
    add_p(doc, "Sự phát triển từ mô hình ngôn ngữ đơn thuần sang hệ thống đại lý tự hành (Agent) được thúc đẩy bởi các khung điều phối suy luận như ReAct (Yao et al., 2022) kết hợp luồng suy nghĩ (Reasoning) và hành động (Action) theo vòng lặp. Để tương tác với thế giới bên ngoài, các kiến trúc Tool-augmented LLMs (Schick et al., 2023; Qin et al., ToolBench, 2023) cho phép mô hình truy vấn cơ sở dữ liệu và gọi API ngoài. Tuy nhiên, việc duy trì sự chính xác về tham số và tránh rơi vào bẫy gọi công cụ vô tận vẫn là một thách thức mở.")

    add_h2(doc, "2.2. Năng lực Quy hoạch và Giải quyết Bài toán Ràng buộc (Planning & Constrained Problem Solving)")
    add_p(doc, "Khác với các tác vụ hỏi đáp thông thường, lập kế hoạch yêu cầu agent phải nhìn về phía trước (look-ahead) và kiểm soát ràng buộc toàn cục. Nghiên cứu của Valmeekam et al. (PlanBench, 2023) chứng minh rằng các LLMs tự thân (zero-shot/few-shot) có tỷ lệ lập kế hoạch hợp lệ dưới 10% trong các bài toán khối hộp cổ điển (Blocks World). Trong bài toán du lịch, các ràng buộc như ngân sách trần (Budget) hay số đêm lưu trú tối thiểu (Minimum Nights) đòi hỏi khả năng backtracking và tối ưu hóa mà các bộ sinh token tự hồi quy thuần túy thường xuyên thất bại.")

    add_h2(doc, "2.3. Các Benchmark Đánh giá Năng lực Du lịch Thực tế (Travel Evaluation Benchmarks)")
    add_p(doc, "Trước TravelPlanner, các benchmark như WebArena (Zhou et al., 2023) đánh giá agent tương tác web nhưng phụ thuộc nặng nề vào DOM và dễ bị ảnh hưởng bởi biến động mạng. TravelPlanner (Xie et al., ICML 2024) đã tạo ra một môi trường sandbox đóng cô lập, chuẩn hóa dữ liệu chuyến bay, khách sạn, nhà hàng, điểm tham quan và khoảng cách lái xe. Gần đây, các benchmark khu vực như ChinaTravel (2024) hay TripTailor (2025) cũng bắt đầu xuất hiện, củng cố tính cấp thiết của việc xây dựng một bộ benchmark bản địa hóa cho du lịch Việt Nam.")

    # 3. Khung Đánh giá Hai Giai đoạn
    add_h1(doc, "3. Khung Đánh giá Hai Giai đoạn (Two-Stage Evaluation Framework)")
    
    add_p(doc, "Trong bài báo TravelPlanner, nhóm tác giả đề xuất hai chế độ vận hành chính: Sole-Planning (chỉ lập kế hoạch thuần túy khi được cung cấp sẵn thông tin) và Two-Stage (đại lý vừa tự thu thập thông tin qua công cụ, vừa lập kế hoạch). Nghiên cứu tuần này tập trung hoàn toàn vào chế độ Two-Stage vì đây là kịch bản sát thực tế nhất với một trợ lý du lịch tự hành:")
    
    add_bullet(doc, "Giai đoạn 1 — Thu thập Thông tin qua Vòng lặp ReAct: ", "Agent nhận câu hỏi của người dùng và được cấp 6 công cụ tìm kiếm: FlightSearch, GoogleDistanceMatrix, AccommodationSearch, RestaurantSearch, AttractionSearch, CitySearch. Trong tối đa 30 bước, agent phải tương tác với môi trường và ghi lại thông tin đã kiểm chứng vào sổ tay thông qua công cụ NotebookWrite.")
    add_bullet(doc, "Giai đoạn 2 — Hoạch định Lịch trình Toàn diện (Planner): ", "Sau khi hoàn tất thu thập, agent gọi công cụ Planner[query]. Toàn bộ dữ liệu trong Notebook được nạp vào mô hình hoạch định để kết xuất ra lịch trình từng ngày (Day 1... Day N) chứa đầy đủ thông tin về di chuyển, khách sạn, bữa ăn, điểm tham quan và chi phí.")

    add_image_with_caption(doc, "tmp_media/image1.png", "Hình 1: Bảng Two-Stage từ bài báo TravelPlanner (Xie et al., ICML 2024)")

    add_p(doc, "Hạ tầng thực nghiệm của nhóm được triển khai thông qua cổng điều phối 9Router nội bộ (endpoint http://127.0.0.1:20128/v1), cho phép định tuyến linh hoạt tới các backend LLMs cao cấp (Antigravity, GitHub Models) với độ ổn định cao. Thí nghiệm được thực hiện trên tập validation chuẩn gồm 180 query (chia đều thành 60 Easy, 60 Medium, 60 Hard với độ dài chuyến đi từ 3, 5 đến 7 ngày).")

    # 4. Kết quả Thực nghiệm & Phân tích Đánh giá Đa mô hình
    add_h1(doc, "4. Kết quả Thực nghiệm & Phân tích Đánh giá Đa mô hình")
    
    add_p(doc, "Dưới đây là bảng tổng hợp các chỉ số cốt lõi thu được từ quá trình kiểm thử thực tế của nhóm trên tập validation (180 query), đặt cạnh số liệu chuẩn của bài báo TravelPlanner:")

    # Table of results
    table_data = [
        ["Mô hình (Model)", "Tập mẫu", "Delivery Rate", "Commonsense Micro / Macro", "Hard Constraint Micro / Macro", "Final Pass Rate"],
        ["GPT-4-Turbo (Paper ICML 2024)", "1.000 test", "~50.2%", "— / 16.2%", "— / 3.4%", "0.60%"],
        ["Gemini-Pro (Paper ICML 2024)", "1.000 test", "~48.5%", "— / 11.8%", "— / 1.7%", "0.20%"],
        ["gemini-3.1-pro-low (Thực nghiệm)", "180 valid", "47.22%", "34.58% / 15.00%", "18.53% / 13.89%", "11.11%"],
        ["gemini-3.8-flash-low (Thực nghiệm)", "180 valid", "73.89%", "64.58% / 35.00%", "42.86% / 25.56%", "17.22%"],
        ["gemini-3.8-flash-high (Thực nghiệm)", "118 valid", "66.10%", "59.96% / 32.20%", "36.36% / 35.59%", "25.42%"],
        ["claude-sonnet-4.5 (Thực nghiệm)", "115 valid", "31.30%", "24.24% / 5.22%", "11.67% / 6.09%", "3.48%"]
    ]
    
    tbl = doc.add_table(rows=len(table_data), cols=6)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            
            if r_idx == 0:
                set_cell_background(cell, "1B365D")
                r = p.add_run(val)
                format_run(r, font_name="Times New Roman", size_pt=9.5, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F7FAFC")
                r = p.add_run(val)
                is_bold = (c_idx == 5 or c_idx == 0)
                color = (0x1B, 0x36, 0x5D) if c_idx == 5 else (0x22, 0x22, 0x22)
                format_run(r, font_name="Times New Roman", size_pt=9.5, bold=is_bold, color_rgb=color)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(4)

    # 4.1 Gemini 3.8 Flash High
    add_h2(doc, "4.1. Đánh giá Chi tiết Mô hình gemini-3.8-flash-high (118 queries validate)")
    
    add_p(doc, "Kết quả chạy benchmark cho 118 query validate đầu tiên (gồm 60 câu Easy và 58 câu Medium) của gemini-3.8-flash-high được ghi nhận qua hai hình ảnh chụp trực tiếp từ hệ thống đánh giá:")
    
    add_image_with_caption(doc, "tmp_media/image2.png", "Hình 2: Kết quả chạy benchmark cho 118 query validate của gemini-3.8-flash-high (chấm trên toàn bộ 118 câu)")
    add_image_with_caption(doc, "tmp_media/image3.png", "Hình 3: Kết quả chạy cho các query pass delivery rate của gemini-3.8-flash-high (chỉ chấm trên tập 78 câu đã giao plan)")

    add_p(doc, "Nhận xét phân tích: Trong 118 query được giao nhiệm vụ, tỷ lệ mà gemini-3.8-flash-high được chấp nhận câu trả lời (Delivery Rate) đạt 66,1% (78/118 câu). Tức là có tới 33,9% số ca bị đánh rớt ngay từ vòng tương tác môi trường mà chưa kịp nộp bài. Dưới đây là các nguyên nhân kỹ thuật cụ thể:")

    add_bullet(doc, "Gọi quá 30 bước mà chưa gọi Planner (Deadloop): ", "Trong bài báo, Planner là công cụ tối hậu để kết xuất lịch trình. Do kẹt vào các vòng lặp tìm kiếm không lối thoát, agent tiêu tốn hết 30 bước cho phép và bị hệ thống ngắt đột ngột.")
    add_image_with_caption(doc, "tmp_media/image4.png", "Hình 4: Minh họa lỗi gọi quá 30 bước mà chưa gọi Planner (Deadloop)", width_inch=5.8)

    add_bullet(doc, "Tốn quá 30.000 token trên một bước gọi tool: ", "Agent không phân tách rành mạch giữa các lượt suy nghĩ và gọi công cụ. Tại một số bước, nội dung suy nghĩ phình to dữ dội dẫn đến tràn giới hạn token của proxy gateway. Điển hình ở plan thứ 24 step 2, agent sinh hơn 400 thought trong một step duy nhất.")
    add_image_with_caption(doc, "tmp_media/image5.jpeg", "Hình 5: Minh họa lỗi phình to token trên một bước gọi tool (hơn 400 thoughts)", width_inch=4.2)

    add_bullet(doc, "Lỗi tham số và mâu thuẫn giữa hành động và suy nghĩ: ", "Agent gọi vào công cụ một thực thể không tồn tại hoặc sai định dạng. Ví dụ điển hình: agent nghĩ trong đầu là tìm 'St. Louis' nhưng câu lệnh hành động thực tế lại sinh ra chuỗi 'St .\\u4e92', hoàn toàn không có trong cơ sở dữ liệu.")
    add_image_with_caption(doc, "tmp_media/image6.png", "Hình 6: Minh họa lỗi tham số mâu thuẫn (tìm kiếm 'st .\\u4e92' thay vì 'St. Louis')", width_inch=4.8)

    add_bullet(doc, "Dừng bước suy nghĩ quá sớm (Early Stopping): ", "Dẫn đến việc thiếu hụt thông tin trầm trọng, từ đó rơi vào ảo giác khi lập kế hoạch. Nguyên nhân sâu xa là do gemini-3.8-flash-high có thói quen không ngắt dòng '\\n' khi suy nghĩ, khiến suy nghĩ và hành động bị gộp dính chùm vào 1 step. Minh chứng ở plan số 102: khi đã suy nghĩ hết ở thought step 2, agent đã tự gọi Planner vì ngộ nhận mình đã tìm và ghi hết vào notebook.")
    add_bullet(doc, "Nghĩ nhưng không làm (Thought vs Action Inconsistency): ", "Agent tự nhủ trong thought là sẽ ghi thông tin vào Notebook, nhưng action kế tiếp lại không hề gọi NotebookWrite mà nhảy sang tìm kiếm khác. Minh chứng rõ rệt ở plan số 55.")

    # 4.2 Claude Sonnet 4.5
    add_h2(doc, "4.2. Đánh giá Chi tiết Mô hình claude-sonnet-4.5 (115 queries validate)")
    
    add_p(doc, "Claude Sonnet 4.5 là một mô hình thế hệ mới không xuất hiện trong bài báo gốc năm 2024. Việc kiểm thử mô hình này mang lại góc nhìn độc lập về khả năng thích ứng của các họ mô hình Anthropic trước chuẩn đánh giá TravelPlanner:")

    add_image_with_caption(doc, "tmp_media/image7.png", "Hình 7: Kết quả chạy benchmark cho 115 query validate của claude-sonnet-4.5 (chấm trên toàn bộ 115 câu)")
    add_image_with_caption(doc, "tmp_media/image8.png", "Hình 8: Kết quả chạy cho các query pass delivery rate của claude-sonnet-4.5 (chỉ chấm trên tập 36 câu đã giao plan)")

    add_p(doc, "Nhận xét phân tích: Claude Sonnet 4.5 có tỷ lệ Delivery Rate rất thấp, chỉ đạt 31,3% (36/115 câu). Nguyên nhân chủ yếu xuất phát từ tính cách thận trọng quá mức của mô hình: Claude Sonnet 4.5 liên tục thực hiện các bước kiểm tra chéo và đối soát thông tin qua lại giữa các thành phố, dẫn đến việc cạn kiệt 30 bước ReAct trước khi kịp tổng hợp kế hoạch. Tuy nhiên, ở các câu giao được plan, Final Pass Rate đạt 11,11% — cao gấp gần 20 lần so với GPT-4-Turbo thời điểm 2024 (0,6%).")

    # 4.3 Khám phá bước ngoặt: Delivery Rate Masking
    add_h2(doc, "4.3. Khám phá Bước ngoặt: Hiện tượng 'Delivery Rate Masking' & Lỗ hổng Metric của TravelPlanner")
    
    add_p(doc, "Một phát hiện mang tính học thuật cực kỳ quan trọng của nhóm nghiên cứu là việc vạch trần: Cách thức tính điểm của bài báo TravelPlanner đang che giấu và bóp méo nghiêm trọng năng lực suy luận thực sự của các LLM.")
    
    add_p(doc, "Trong mã nguồn evaluation/eval.py, khi một query không giao được kế hoạch (Delivery = False), hàm đánh giá tự động gán giá trị vi phạm (Fail) cho toàn bộ các ràng buộc Commonsense và Hard Constraints. Sau đó, tỷ lệ Pass Rate tổng thể được tính bằng cách chia số câu đạt cho TỔNG SỐ QUERY NẠP VÀO (118 hoặc 180 câu), thay vì chia cho số kế hoạch thực tế được tạo ra.")

    add_header_callout(doc,
        "Khi nhóm tiến hành bóc tách và chỉ chấm trên tập các câu giao plan thành công (Delivered Subset), các chỉ số Pass Rate tăng vọt ngoạn mục: Commonsense Micro của Gemini 3.8 tăng từ 59.96% lên 90.71%; Hard Constraint Micro tăng từ 36.36% lên 57.14%; Final Pass Rate tăng từ 25.42% lên 38.46%. Ở Claude Sonnet 4.5, Commonsense Micro tăng từ 24.24% lên 77.43%!",
        "Phát hiện Nghịch lý Metric: ")

    add_p(doc, "Bảng đối chiếu sự biến thiên giữa hai cách chấm cho thấy rõ mức độ che giấu năng lực:")

    # Table comparison
    table_mask = [
        ["Mô hình", "Chỉ số đánh giá (Metric)", "Chấm tất cả (All Queries)", "Chỉ chấm câu giao được (Delivered)", "Mức độ biến thiên"],
        ["Gemini 3.8 Flash High\n(78/118 delivered)", "Commonsense Micro Pass Rate\nCommonsense Macro Pass Rate\nHard Constraint Micro Pass Rate\nHard Constraint Macro Pass Rate\nFinal Pass Rate", "59.96%\n32.20%\n36.36%\n35.59%\n25.42%", "90.71%\n48.72%\n57.14%\n53.85%\n38.46%", "+30.75%\n+16.52%\n+20.78%\n+18.26%\n+13.04%"],
        ["Claude Sonnet 4.5\n(36/115 delivered)", "Commonsense Micro Pass Rate\nCommonsense Macro Pass Rate\nHard Constraint Micro Pass Rate\nHard Constraint Macro Pass Rate\nFinal Pass Rate", "24.24%\n5.22%\n11.67%\n6.09%\n3.48%", "77.43%\n16.67%\n28.57%\n19.44%\n11.11%", "+53.19%\n+11.45%\n+16.90%\n+13.35%\n+7.63%"],
        ["Gemini 3.1 Pro Low\n(85/180 delivered)", "Commonsense Micro Pass Rate\nHard Constraint Micro Pass Rate\nFinal Pass Rate", "34.58%\n18.53%\n11.11%", "73.24%\n33.51%\n23.53%", "+38.66%\n+14.98%\n+12.42%"]
    ]

    tbl_m = doc.add_table(rows=len(table_mask), cols=5)
    tbl_m.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_m)
    
    for r_idx, row in enumerate(table_mask):
        for c_idx, val in enumerate(row):
            cell = tbl_m.cell(r_idx, c_idx)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            
            if r_idx == 0:
                set_cell_background(cell, "1B365D")
                r = p.add_run(val)
                format_run(r, font_name="Times New Roman", size_pt=9.5, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F7FAFC")
                r = p.add_run(val)
                is_bold = (c_idx == 4)
                color = (0x2B, 0x6C, 0xB0) if c_idx == 4 else (0x22, 0x22, 0x22)
                format_run(r, font_name="Times New Roman", size_pt=9.0, bold=is_bold, color_rgb=color)

    add_p(doc, "Ý nghĩa phản biện: Kết quả này chứng minh điểm nghẽn thực sự của các LLM hiện đại KHÔNG PHẢI là khả năng suy luận logic hay thỏa hiệp ràng buộc khi lập kế hoạch, mà nằm ở KHÂU TƯƠNG TÁC MÔI TRƯỜNG (Tool Interaction Failure). Một khi đã vượt qua được cửa ải thu thập công cụ và nạp dữ liệu vào Planner, khả năng tuân thủ logic đời thường của Gemini 3.8 đạt trên 90%!")

    # 5. Phân tích Đối chiếu Lỗi Hệ thống theo Bài báo TravelPlanner
    add_h1(doc, "5. Phân tích Đối chiếu Lỗi Hệ thống theo Bài báo TravelPlanner (Error Taxonomy)")
    
    add_p(doc, "Để bảo đảm tính khách quan và khoa học, nhóm đối chiếu toàn bộ các lỗi thực nghiệm với hệ thống phân loại lỗi được nhóm tác giả TravelPlanner công bố tại Mục 5, Figure 2, Figure 3, Table 4 và Table 5:")

    # 5.1 Nhóm lỗi tương tác công cụ
    add_h2(doc, "5.1. Nhóm Lỗi Tương tác Công cụ (Tool-use Trajectory Failures)")
    
    add_h3(doc, "Mã T3 — Chạm Số bước Tối đa (Max Step Limit, Figure 2, Mục 3.4)")
    add_bullet(doc, "Trong bài báo: ", "Giới hạn mỗi phiên ReAct là 30 bước. Vượt quá 30 bước mà chưa gọi Planner thì bị đánh rớt. Bài báo ghi nhận lỗi này chiếm 56,7% số ca không giao được plan ở GPT-4-Turbo và 66,7% ở Gemini-Pro.")
    add_bullet(doc, "Dữ liệu thực nghiệm của nhóm: ", "Ở Model A (Gemini 3.8 Flash Low), có 43/44 ca rớt delivery do hết 30 bước (97,7%). Ở Model B (Flash High), 39/39 ca rớt delivery đều do chạm trần 30 bước (100%). Ở Gemini 3.1 Pro Low, 60/91 ca rớt delivery là do hết bước (65,93%, rất sát con số 66,7% của bài báo).")
    add_bullet(doc, "Dẫn chứng thực tế: ", "Model A câu 29, 30, 35, 42, 45, 47, 48... Quỹ đạo của các câu trên dài đúng 30 bước mà không hề có lệnh Planner. Trung bình trong 30 bước lãng phí, agent gọi NotebookWrite 10,6 lần, FlightSearch 8,2 lần, AccommodationSearch 3,3 lần.")

    add_h3(doc, "Mã T2 — Kẹt Vòng lặp Giả / Không Điều chỉnh theo Phản hồi (Dead Loop, Mục 5.1 ý 2, Figure 2)")
    add_bullet(doc, "Trong bài báo: ", "Dù môi trường báo action không hợp lệ hoặc trả kết quả rỗng (Unavailable Transportation), agent vẫn ngoan cố lặp lại hành động tương tự mà không chịu đổi chiến lược.")
    add_bullet(doc, "Dữ liệu thực nghiệm của nhóm: ", "Dẫn chứng kinh điển ở Model A, Câu 29 (Easy, 5 ngày, Richmond -> 2 thành phố Tennessee): Sau bước 1 gọi CitySearch, 29 bước còn lại agent chỉ chăm chăm gọi FlightSearch. Riêng lệnh FlightSearch[Richmond, Nashville, 2022-03-05] được gọi tới 13 lần dù môi trường liên tục báo không có chuyến bay! Agent xoay vòng giữa Nashville, Knoxville, Memphis mà tuyệt đối không gọi GoogleDistanceMatrix để chuyển sang tự lái.")
    add_bullet(doc, "Điểm khác biệt với bài báo: ", "Trong code gốc, cơ chế Same Action Dead Loop chỉ kích hoạt khi một lệnh lặp lại 3 lần LIÊN TIẾP. Agent lách luật bằng cách gọi xen kẽ (A -> B -> A -> B) khiến bộ đếm bị reset liên tục. Vì vậy, về bản chất đây là lỗi T2 nhưng trong thống kê số liệu lại bị gộp vào mã T3 (Max Step Limit).")

    add_h3(doc, "Mã T1 — Lỗi Tham số khi Gọi Tool (Argument Error, Mục 5.1 ý 1, Figure 2)")
    add_bullet(doc, "Đối chiếu: ", "Các mô hình 2026 hầu như đã làm chủ hoàn toàn cú pháp tool. Model A đạt 0 lỗi tham số trên gần 4.000 bước gọi tool. Model B chỉ có 8 bước lỗi ở 7 câu (chủ yếu do ký tự Unicode như 'st .\\u4e92').")

    # 5.2 Nhóm lỗi lập kế hoạch & thu thập thông tin
    add_h2(doc, "5.2. Nhóm Lỗi Lập kế hoạch & Thu thập Thông tin (Planning & Information Gathering)")
    
    add_h3(doc, "Mã P2 — Thu thập Thông tin Không đủ dẫn tới Bịa đặt (Mục 5.2 nhận xét 2, Table 5)")
    add_p(doc, "Table 5 trong bài báo chứng minh số mục agent ghi vào Notebook tỉ lệ nghịch với mức độ ảo giác. Đối chiếu số mục ghi vào Notebook trung bình mỗi câu giữa bài báo và nhóm thực nghiệm (độ dài chuyến đi 3 / 5 / 7 ngày):")

    # Table 5 comparison
    tbl_t5_data = [
        ["Công cụ tìm kiếm", "Plan Tham chiếu", "GPT-4-Turbo (Paper)", "Model A (Flash Low)", "Model B (Flash High)"],
        ["FlightSearch", "2 / 3 / 4", "0.7 / 1.2 / 0.8", "1.7 / 2.1 / 1.9", "1.8 / 1.3 / 1.1 (giảm dần)"],
        ["DistanceMatrix", "2 / 3 / 4", "0.3 / 0.6 / 1.2", "0.6 / 2.2 / 2.4", "0.8 / 1.4 / 1.4"],
        ["RestaurantSearch", "1 / 2 / 3", "0.9 / 1.5 / 2.4", "1.0 / 1.9 / 2.5", "1.0 / 0.9 / 1.1"],
        ["AccommodationSearch", "1 / 2 / 3", "0.9 / 1.6 / 2.5", "1.0 / 2.1 / 3.0", "1.0 / 1.0 / 1.3"],
        ["Tỷ lệ đạt Within Sandbox", "—", "95% / 65% / 42%", "100% / 77% / 48%", "98% / 62% / 37%"]
    ]
    tbl_t5 = doc.add_table(rows=len(tbl_t5_data), cols=5)
    tbl_t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_t5)
    for r_idx, row in enumerate(tbl_t5_data):
        for c_idx, val in enumerate(row):
            cell = tbl_t5.cell(r_idx, c_idx)
            set_cell_margins(cell, top=90, bottom=90, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            if r_idx == 0:
                set_cell_background(cell, "1B365D")
                r = p.add_run(val)
                format_run(r, font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F7FAFC")
                r = p.add_run(val)
                format_run(r, font_name="Times New Roman", size_pt=9.0, bold=(r_idx == 5), color_rgb=(0x22, 0x22, 0x22))

    add_bullet(doc, "Dẫn chứng thực tế: ", "Ở Model B, có 21 câu gọi Planner ngay từ bước 1–4 khi chưa hề tìm kiếm chuyến bay lần nào (câu 27, 30, 35, 38, 43...). Kết quả là trong 27 plan trượt Within Sandbox của Model B, có tới 25 plan sai số hiệu chuyến bay do Planner phải tự bịa ra.")

    add_h3(doc, "Mã P3 — Ràng buộc Toàn cục: Budget và Minimum Nights Stay (Mục 5.2 nhận xét 3)")
    add_bullet(doc, "Vỡ ngân sách (Budget Overrun): ", "Là nguyên nhân gây trượt đơn lẻ phổ biến nhất. Ở Model A, có 17/35 câu 'gần đạt' (thỏa mãn hết mọi ràng buộc khác) nhưng rớt chung cuộc chỉ vì vượt ngân sách vài chục USD (ví dụ câu 5: chi phí 939 USD, ngân sách 900 USD). Ở Model B, có 7/15 câu gần đạt trượt đúng Budget. Ở Gemini 3.1 Pro, có tới 52/180 câu (28,89%) vỡ ngân sách.")
    add_bullet(doc, "Vi phạm số đêm tối thiểu (Minimum Nights Stay): ", "Xuất hiện ở 24 câu tại Model A và C. Điển hình ở Câu 11 (đi Seattle 3 ngày - 2 đêm): Agent đặt phòng Airbnb 'private spacious LES bedroom, Seattle' có quy định minimum_nights = 3. Do chuyến đi chỉ ở 2 đêm, kế hoạch bị đánh trượt logic đời thường.")

    add_h3(doc, "Mã P1 — Độ khó Tăng làm Suy giảm Hiệu năng (Mục 5.2 nhận xét 1, Table 4)")
    add_bullet(doc, "Đối chiếu: ", "Xu hướng giảm từ Easy xuống Medium xuất hiện rõ rệt ở cả hai mô hình (Model A: 35.0% -> 28.3%; Model B: 31.7% -> 19.0%), hoàn toàn trùng khớp với kết luận của bài báo: số lượng hard constraint tăng lên làm bùng nổ không gian tìm kiếm.")

    # 5.3 Nhóm lỗi suy luận & case study
    add_h2(doc, "5.3. Nhóm Lỗi Suy luận & Sai lệch Hành vi (Reasoning & Case Study Failures)")
    
    add_h3(doc, "Mã C2 — Nhầm lẫn Thông tin dẫn tới Câu trả lời Bịa (Mục 5.3 đoạn 2, Figure 3 giữa)")
    add_bullet(doc, "Bản chất lỗi: ", "Agent có đủ thông tin trong Notebook nhưng lại lấy thông tin của thực thể này gán cho thực thể khác.")
    add_bullet(doc, "Dẫn chứng thực tế: ", "Model B câu 20: Chuyến về Orlando -> Providence bị ghi số hiệu F3567591, vốn là mã hiệu của chuyến đi Providence -> Orlando mà agent tìm được ở bước trước. Model B câu 72: Chuyến bay F3923931 (Houston -> Wichita) bị gán ngược cho chiều về Wichita -> Houston. Model A câu 26: Mã F3725699 (Chicago -> Orlando) bị gán cho chặng Rockford -> Chicago.")

    add_h3(doc, "Mã C3 — Hành động Không khớp với Suy nghĩ (Mục 5.3 đoạn 3, Figure 3 phải)")
    add_bullet(doc, "Bản chất lỗi: ", "Phần Thought suy nghĩ một đằng nhưng câu lệnh Action ngay sau đó lại làm một nẻo.")
    add_bullet(doc, "Dẫn chứng thực tế: ", "Model B câu 45 bước 12: Thought ghi 'Cần tìm chuyến bay từ Devils Lake đến Alamosa', nhưng Action lại gọi GoogleDistanceMatrix[Denver, Colorado Springs, driving]. Tương tự ở Model B câu 55: Thought tự nhủ cần lưu khách sạn vào Notebook nhưng Action lại nhảy sang tìm nhà hàng.")

    # 6. Các Hiện tượng Dị thường Ngoài Phạm vi Bài báo
    add_h1(doc, "6. Các Hiện tượng Dị thường Ngoài Phạm vi Bài báo (System & Data Artifacts)")
    
    add_p(doc, "Quá trình kiểm toán kỹ thuật chuyên sâu của nhóm đã phát hiện 5 hiện tượng dị thường mang tính hệ thống mà bài báo gốc hoàn toàn chưa đề cập:")

    add_h2(doc, "6.1. Hiện tượng 1: Tự viết 'Observation' Giả & Sự Sụp đổ Giao thức Ngắt nhịp ReAct (Turn-taking Protocol Breakdown)")
    
    add_h3(doc, "6.1.1. Khái niệm & Cơ chế Vận hành ReAct trong Benchmark TravelPlanner")
    add_p(doc, "Benchmark TravelPlanner (ICML 2024) kế thừa khung ReAct (Yao et al., 2023) trong kiến trúc đánh giá hai giai đoạn (Two-Stage Mode). Ở Giai đoạn 1 (Thu thập Thông tin), đại lý không được phép lập kế hoạch ngay mà phải tương tác luân phiên 3 pha (Thought t -> Action t -> Observation t) với môi trường sandbox qua 8 công cụ (FlightSearch, DistanceMatrix, AccommodationSearch, RestaurantSearch, AttractionSearch, CitySearch, NotebookWrite, Planner). Mọi thông tin hợp lệ phải được ghi chép tường minh vào Notebook trước khi công cụ Planner được kích hoạt.")
    add_p(doc, "Về mặt bản chất kiến trúc, TravelPlanner sử dụng Text-completion ReAct (mớm prompt văn bản tự do dựa trên quy ước định dạng), hoàn toàn không tích hợp Native Tool Calling / Structured Function Calling (giao thức JSON Schema do API và Tokenizer của nhà cung cấp mô hình trực tiếp kiểm soát). Hệ thống phân định các lượt tương tác hoàn toàn dựa vào thao tác nối chuỗi văn bản vào biến scratchpad.")

    add_h3(doc, "6.1.2. Căn nguyên Kỹ thuật: Sự Bất đối xứng giữa Bài báo và Mã nguồn Thực tế")
    add_p(doc, "Đối chiếu trực tiếp giữa bài báo học thuật và mã nguồn chính thức (agents/tool_agents.py) đã bộc lộ lỗ hổng thiết kế nghiêm trọng trong giao thức ngắt nhịp (Turn-taking Protocol):")
    add_bullet(doc, "Sự lệ thuộc tuyệt đối vào Stop Token phía Server: ", "Trong mã nguồn gốc (dòng 96–158), tác giả cài cứng tham số model_kwargs={'stop': ['\n']} cho toàn bộ các mô hình và khoán trắng trách nhiệm ngắt nhịp cho server OpenAI (GPT-3.5/GPT-4), mặc định rằng API sẽ luôn ngắt luồng sinh của LLM ngay khi chạm ký tự xuống dòng '\n'.")
    add_bullet(doc, "Hàm xử lý chuỗi 'mù màu' (Format Step Vulnerability): ", "Tại dòng 621 của agents/tool_agents.py, hàm xử lý kết quả trả về được viết như sau: return step.strip('\n').strip().replace('\n', ''). Thay vì áp dụng cơ chế phòng thủ client-side bằng cách chỉ trích xuất dòng đầu tiên (step.split('\n')[0]), mã nguồn lại xóa sạch toàn bộ ký tự xuống dòng, ép toàn bộ văn bản đa dòng thành một dòng dính liền.")
    add_bullet(doc, "Cơ chế Tự hồi quy (Autoregressive In-Context Continuation): ", "Khi triển khai các mô hình suy luận sâu (Thinking Models như Gemini 3.8 Flash) qua Gateway (9Router / Antigravity), tham số stop: ['\n'] bị hệ thống backend bỏ qua (đã được nhóm kiểm chứng thực nghiệm qua truy vấn HTTP độc lập). Đứng trước dấu nhắc dở dang (Thought t:), theo quy luật phân phối xác suất văn bản của mẫu ReAct trong prompt, mô hình tự động sinh tiếp Action t:. Khi không bị ngắt nhịp, mô hình tiếp tục đóng vai Môi trường (Role-playing) và tự bịa ra nhãn Observation t: cùng toàn bộ dữ liệu giả lập, kéo dài chuỗi độc thoại khép kín qua hàng chục bước.")
    add_bullet(doc, "Hậu quả dán dính vào Bộ nhớ: ", "Khi khối văn bản tự biên tự diễn dài hàng chục nghìn ký tự trả về, hàm format_step xóa sạch dấu xuống dòng và dán dính toàn bộ kịch bản giả lập này vào trường thought của bước hiện tại, khiến ngữ cảnh của đại lý bị nhiễm độc hoàn toàn.")

    add_h3(doc, "6.1.3. Thống kê Thực nghiệm Định lượng trên 3 Mô hình Gemini")
    add_p(doc, "Nhóm đã tiến hành kiểm toán tự động toàn bộ các file log thực nghiệm (generated_plan_*.json) trên 3 mô hình để lượng hóa mức độ ảnh hưởng của hiện tượng Runaway Simulation:")

    # Bảng 7: Thống kê Runaway Simulation
    table_runaway = [
        ["Chỉ số Kỹ thuật Thực nghiệm", "Gemini 3.8 Flash High (117 files)", "Gemini 3.8 Flash Low (180 files)", "Gemini 3.1 Pro Low (180 files)"],
        ["Tỷ lệ query dính Observation giả", "114 / 117 (97,44%)", "179 / 180 (99,44%)", "180 / 180 (100,0%)"],
        ["Tổng số bước tự sinh Observation giả", "279 bước", "752 bước", "1.816 bước"],
        ["Độ dài trường Thought cực đại (ký tự)", "213.930 (Query 118)", "33.104 (Query 68)", "1.381 (Query 140)"],
        ["Số bước có Thought > 5.000 ký tự", "147 bước", "246 bước", "0 bước"],
        ["Số bước bùng nổ ngữ cảnh (> 20.000 ký tự)", "86 bước", "4 bước", "0 bước"],
        ["Biến động dung lượng file log", "Phình to 100 KB – 218 KB", "Dao động 20 KB – 40 KB", "Chuẩn ~15 KB – 25 KB"]
    ]
    
    tbl_r = doc.add_table(rows=len(table_runaway), cols=4)
    tbl_r.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_r)
    col_r_widths = [Inches(2.4), Inches(1.4), Inches(1.35), Inches(1.35)]
    
    for r_idx, row in enumerate(table_runaway):
        for c_idx, val in enumerate(row):
            cell = tbl_r.cell(r_idx, c_idx)
            cell.width = col_r_widths[c_idx]
            set_cell_margins(cell, top=100, bottom=100, left=110, right=110)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            
            if r_idx == 0:
                set_cell_background(cell, "1B365D")
                r = p.add_run(val)
                format_run(r, font_name="Times New Roman", size_pt=9.0, bold=True, color_rgb=(0xFF, 0xFF, 0xFF))
            else:
                if r_idx % 2 == 1:
                    set_cell_background(cell, "F7FAFC")
                r = p.add_run(val)
                is_bold = (c_idx == 0)
                format_run(r, font_name="Times New Roman", size_pt=9.0, bold=is_bold, color_rgb=(0x22, 0x22, 0x22))

    p_sp7 = doc.add_paragraph()
    p_sp7.paragraph_format.space_before = Pt(3)
    p_sp7.paragraph_format.space_after = Pt(4)

    add_p(doc, "Phân tích số liệu: Ở Gemini 3.8 Flash High, ngân sách suy luận lớn (high thinking budget) kết hợp với việc mất stop token đã khiến hiện tượng runaway bùng nổ dữ dội nhất. Có tới 86 bước vượt ngưỡng 20.000 ký tự (đỉnh điểm Query 118 đạt 213.930 ký tự), làm file log phình to gấp 10-15 lần mức bình thường. Ngược lại, Gemini 3.1 Pro Low tuy dính 100% câu nhưng độ dài cực đại chỉ 1.381 ký tự do kiến trúc mô hình không kéo dài chuỗi tự sinh.")

    add_h3(doc, "6.1.4. Bằng chứng Thực nghiệm Dị thường Trích xuất từ Log")
    add_p(doc, "Dưới đây là hai trích đoạn điển hình được trích xuất nguyên văn từ file log generated_plan_100.json (dung lượng 151 KB) minh chứng cho mức độ giả lập tinh vi của mô hình:")
    
    add_header_callout(doc,
        "Action 7: GoogleDistanceMatrix[Myrtle Beach, Knoxville, self-driving]\n"
        "Observation 7: {'distance': {'text': '377 mi', 'value': 606708}, 'duration': {'text': '6 hours 18 mins', 'value': 22699}, 'cost': 66.86, 'origin': 'Myrtle Beach', 'destination': 'Knoxville', 'mode': 'self-driving'}\n"
        "Action 8: NotebookWrite[Driving from Myrtle Beach to Knoxville]\n"
        "Observation 8: Driving from Myrtle Beach to Knoxville has been recorded in the Notebook.",
        "Trích đoạn 1 (Plan 100, Step 2) — Đại lý tự giả lập API GoogleDistanceMatrix và tự xác nhận lưu Notebook:\n")
        
    add_p(doc, "Phân tích Trích đoạn 1: Sandbox môi trường hoàn toàn chưa nhận được yêu cầu tính khoảng cách. Đại lý tự sinh cự ly 377 dặm (value: 606708), tự ước tính chi phí 66.86 USD, và tự đóng vai hệ thống Notebook phát ra thông báo xác nhận đã lưu dữ liệu.")

    add_header_callout(doc,
        "Action 46: AccommodationSearch[Nashville]\n"
        "Observation 46: [{'_id': '657ae06db8cf402324dfab30', 'NAME': 'Modern East Nashville Suite with Patio', 'price': 204, 'room type': 'entire room', 'house type': 'condo', 'rating': 4.8, 'reviews': 77, 'has kitchen': 'Yes', 'city': 'Nashville'}, {'_id': '657ae06db8cf402324dfab31', 'NAME': 'Vibrant Nashville Loft near Broadway', 'price': 185, 'room type': 'entire room', 'house type': 'loft', 'rating': 4.9, 'reviews': 120, 'has kitchen': 'Yes', 'city': 'Nashville'}]",
        "Trích đoạn 2 (Plan 100, Step 2) — Đại lý tự bịa Cơ sở Dữ liệu Khách sạn với mã MongoDB ObjectId:\n")

    add_p(doc, "Phân tích Trích đoạn 2: Đại lý tự sinh cấu trúc JSON hoàn chỉnh của một bản ghi cơ sở dữ liệu MongoDB Airbnb, bao gồm cả mã hash ObjectId 24 ký tự hex chuẩn xác (_id: '657ae06db8cf402324dfab30'), giá phòng 204 USD và điểm đánh giá 4.8, trong khi cơ sở dữ liệu thực của benchmark không hề tồn tại bản ghi này.")

    add_h3(doc, "6.1.5. Hậu quả Hệ thống đối với Đánh giá Hiệu năng")
    add_bullet(doc, "Ngộ nhận Trạng thái (Delusional State): ", "Do nhìn thấy các dòng Observation ảo trong chính trường thought của mình, mô hình tin rằng đã tích lũy đầy đủ 40–50 thực thể vào Notebook. Tuy nhiên, biến lưu trữ thực tế notebook.list_all() trong môi trường Python hoàn toàn rỗng. Khi chuyển sang giai đoạn Planner, đại lý rơi vào trạng thái thiếu hụt dữ liệu trầm trọng.")
    add_bullet(doc, "Bùng nổ Giới hạn Ngữ cảnh (Context Explosion): ", "Với các bước suy nghĩ dài hơn 38.000 đến 213.000 ký tự (tương đương 8.000 – 50.000 tokens), hệ thống benchmark lập tức kích hoạt điều kiện ngắt khẩn cấp len(self.enc.encode(prompt)) > self.max_token_length (30.000 tokens), khiến đại lý bị dừng đột ngột mà không kịp kết xuất lịch trình.")
    add_bullet(doc, "Méo mó Năng lực Thực tế: ", "Hiện tượng này chứng minh rằng việc đánh rớt đại lý trong Two-Stage Mode phần lớn không phản ánh năng lực lập kế hoạch của LLM, mà xuất phát từ sự sụp đổ của giao thức tương tác phân lượt do benchmark thiết kế thiếu phòng vệ.")

    add_h2(doc, "6.2. Hiện tượng 2: Rò rỉ Logits / MCTS Search Traces từ Server Backend")
    add_p(doc, "Phát hiện tại log 3.8 flash high/generated_plan_101.json, ngay tại Bước 1:")
    add_header_callout(doc,
        "Thought 1: Action 1: CitySearch[Michigan]Child 1: 0.17700287518556667Children:- CitySearch[Michigan] (0.17700287518556667)Explanation:\nAction 1: CitySearch[Michigan]",
        "Trích đoạn Log rò rỉ nguyên văn: ")
    add_p(doc, "Bản chất Kỹ thuật: Trong quá trình suy luận sâu của mô hình Gemini Thinking, các cấu trúc đánh giá cây tìm kiếm nội bộ (Monte Carlo Tree Search / Beam Search) cùng điểm số xác suất nhánh (0.17700287518556667) của engine suy luận phía máy chủ đã bị rò rỉ trực tiếp vào luồng văn bản completion trả về qua gateway, gây sai lệch cấu trúc câu lệnh mà benchmark có thể bóc tách.")

    add_h2(doc, "6.3. Hiện tượng 3: Lỗi Regex Cắt cụt Ngoặc vuông ']' làm Sập oan 30 Query")
    add_p(doc, "Chiếm đúng 30 / 180 query (16,67%) ở mô hình gemini-3.1-pro-low. Trong file agents/tool_agents.py, hàm bóc tách hành động dùng regex khắt khe: ^(\\w+)\\[(.+)\\]$. Khi Gemini 3.1 Pro sinh action bị ngắt nhịp thiếu dấu đóng ']' (ví dụ: Action 10: GoogleDistanceMatrix[Minneapolis, St. Louis,), regex trả về None và môi trường ghi nhận là invalidAction. Sau 3 lần liên tiếp, hệ thống kích hoạt illegal_early_stop_patience và ngắt phiên làm việc, khiến 30 kế hoạch bị trả về rỗng một cách oan uổng do bộ lọc chuỗi.")

    add_h2(doc, "6.4. Hiện tượng 4: Schema Hijacking làm Sập Hàm Đánh giá (KeyError: 'current_city')")
    add_p(doc, "Tại query 121 và 126 của gemini-3.1-pro-low, agent dừng ngang khi đang so sánh phòng khách sạn. Parser GPT-4.1 thay vì trích xuất lịch trình từng ngày thì lại bóc tách ra một mảng JSON thông tin phòng khách sạn ([{'name': ..., 'price': ...}]). Khi chạy file eval, hàm is_reasonable_visiting_city() gọi day['current_city'] gây văng lỗi KeyError và làm crash toàn bộ tiến trình đánh giá ở mốc 67%. Nhóm đã trực tiếp can thiệp patch defensive code vào element_extraction.py và eval.py để xử lý triệt để lỗi này.")

    add_h2(doc, "6.5. Hiện tượng 5: Sai lệch Định dạng trong Chính Cơ sở Dữ liệu Gốc của Benchmark")
    add_p(doc, "Phát hiện độc quyền từ nhóm: Ở Model A, có 10 / 14 plan trượt tiêu chí Within Sandbox hoàn toàn là bị trượt oan do lỗi dữ liệu của bài báo:")
    add_bullet(doc, "Lỗi khoảng trắng kép: ", "Tên khách sạn trong SQLite gốc bị dính 2 dấu cách liền nhau: 'BKLYN Brownstone-  Glam Getaway'.")
    add_bullet(doc, "Lỗi ký tự xuống dòng: ", "Chứa ký tự '\\n' nằm giữa tên nhà hàng.")
    add_bullet(doc, "Lỗi mã hóa dấu nháy: ", "Dữ liệu gốc dùng dấu nháy đơn cong '’' thay vì nháy thẳng ''' (các câu 22, 27, 33, 55, 93, 97, 115, 130, 154, 176). Do evaluator so khớp chuỗi tuyệt đối (string == string), mô hình bị đánh rớt oan uổng.")

    # 7. Đúc kết & Hàm ý cho Dự án Travel Planning tại Việt Nam
    add_h1(doc, "7. Đúc kết & Hàm ý cho Dự án Travel Planning tại Việt Nam")
    
    add_p(doc, "Từ những phát hiện thực nghiệm trên TravelPlanner, nhóm rút ra 4 trụ cột kiến trúc sống còn cho việc thiết kế Agent và xây dựng Benchmark du lịch tại Việt Nam:")
    
    add_bullet(doc, "Trụ cột 1 — Chuẩn hóa & Làm sạch Thực thể Địa phương: ", "Tiếng Việt có dấu và địa giới hành chính phức tạp rất dễ gây vỡ so khớp chuỗi. Hệ thống đánh giá tại Việt Nam tuyệt đối không dùng so khớp chuỗi tuyệt đối mà phải gán Unique Entity ID và hỗ trợ tìm kiếm mờ (Fuzzy Matching).")
    add_bullet(doc, "Trụ cột 2 — Cơ chế Fallback Vận tải Đa phương thức: ", "Khi tìm kiếm vé máy bay trả về rỗng, hệ thống phải tự động kích hoạt fallback sang xe khách liên tỉnh, tàu hỏa Bắc - Nam hoặc xe tự lái, tránh để agent rơi vào vòng lặp chết như trường hợp chuyến bay Richmond -> Nashville.")
    add_bullet(doc, "Trụ cột 3 — Bộ Giám sát Ngân sách Thời gian thực (Dynamic Cost Calculator): ", "Vỡ ngân sách là nguyên nhân gây rớt đài lớn nhất (gần 30%). Cần tích hợp một module tính toán tài chính chạy ngầm trong suốt quá trình ghi chép Notebook để cảnh báo agent khi chi phí chạm ngưỡng 80% ngân sách trần.")
    add_bullet(doc, "Trụ cột 4 — Kiểm soát Tầng Giao tiếp Hạ tầng (Gateway Control): ", "Cài đặt bộ lọc cắt chuỗi client-side chặt chẽ để triệt tiêu hoàn toàn hiện tượng tự viết Observation giả và rò rỉ token suy luận, bảo đảm agent luôn hoạt động trong kỷ luật tương tác môi trường nghiêm ngặt.")

    # Next steps
    add_h2(doc, "Kế hoạch Tuần Tiếp theo (Next Steps)")
    add_bullet(doc, "Nhiệm vụ 1: ", "Hoàn tất đánh giá nốt 62 câu Hard của mô hình gemini-3.8-flash-high để hoàn thiện bức tranh 180 query.")
    add_bullet(doc, "Nhiệm vụ 2: ", "Xây dựng bộ dữ liệu du lịch mẫu tại Việt Nam (sandbox 3 tỉnh thành tiêu biểu: Hà Nội, Đà Nẵng, TP.HCM) và thiết kế hệ thống ràng buộc đặc thù.")
    add_bullet(doc, "Nhiệm vụ 3: ", "Thử nghiệm tích hợp module Dynamic Cost Calculator vào pipeline điều phối đại lý.")

    # Save documents
    dest_path_desktop = "C:/Users/Nayn/Desktop/Weekly_report_TravelPlanner_Final.docx"
    dest_path_attach = "C:/Users/Nayn/AppData/Local/hermes/attachments/Weekly report.docx"
    
    doc.save(dest_path_desktop)
    print(f"Saved to {dest_path_desktop}")
    
    try:
        doc.save(dest_path_attach)
        print(f"Saved to {dest_path_attach}")
    except PermissionError:
        print(f"Notice: {dest_path_attach} is currently opened in Word/another application, skipped overwriting attachments.")

if __name__ == "__main__":
    create_document()
