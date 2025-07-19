from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from schemas.lecture_sse import LectureOutput
from typing import Optional
import io
from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn
from datetime import datetime

router = APIRouter(prefix="/api/v1/lecture-format", tags=["lecture-format"])

def set_cell_border(cell):
    """Set border for a table cell"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    
    # Create borders element
    tcBorders = OxmlElement('w:tcBorders')
    
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '12')  # Border width
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000')  # Black border
        tcBorders.append(border)
    
    tcPr.append(tcBorders)

@router.post("/docx")
async def format_lecture_to_docx(
    lecture: LectureOutput,
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    lesson_name: Optional[str] = None,
    file_name: Optional[str] = "bai_giang.docx"
):
    """
    Format a LectureOutput model into a professional DOCX document using python-docx.
    This is the proper backend formatting endpoint that takes structured data.
    """
    doc = DocxDocument()
    
    # --- Document Styling Setup ---
    styles = doc.styles
    
    # Create custom styles
    try:
        title_style = styles.add_style('LectureTitle', WD_STYLE_TYPE.PARAGRAPH)
        title_style.font.name = 'Times New Roman'
        title_style.font.size = Pt(18)
        title_style.font.bold = True
        title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_style.paragraph_format.space_after = Pt(12)
    except:
        # Style might already exist
        title_style = styles['LectureTitle']
    
    try:
        section_style = styles.add_style('LectureSection', WD_STYLE_TYPE.PARAGRAPH)
        section_style.font.name = 'Times New Roman'
        section_style.font.size = Pt(14)
        section_style.font.bold = True
        section_style.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue
        section_style.paragraph_format.space_before = Pt(12)
        section_style.paragraph_format.space_after = Pt(6)
    except:
        section_style = styles['LectureSection']
    
    try:
        content_style = styles.add_style('LectureContent', WD_STYLE_TYPE.PARAGRAPH)
        content_style.font.name = 'Times New Roman'
        content_style.font.size = Pt(12)
        content_style.paragraph_format.line_spacing = 1.15
        content_style.paragraph_format.space_after = Pt(6)
    except:
        content_style = styles['LectureContent']
    
    # --- Header with metadata ---
    if subject or grade:
        header_section = doc.sections[0]
        header = header_section.header
        header_para = header.paragraphs[0]
        header_text = f"Môn: {subject or 'N/A'} | Lớp: {grade or 'N/A'} | Ngày: {datetime.now().strftime('%d/%m/%Y')}"
        header_para.text = header_text
        header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header_para.style.font.size = Pt(10)
    
    # --- Title ---
    title_para = doc.add_paragraph(lecture.title.upper(), style='LectureTitle')
    
    # --- Goals Section ---
    doc.add_paragraph('MỤC TIÊU BÀI HỌC', style='LectureSection')
    goals_para = doc.add_paragraph(lecture.goals, style='LectureContent')
    
    # --- Equipment Section ---
    doc.add_paragraph('THIẾT BỊ VÀ DỤNG CỤ', style='LectureSection')
    equipment_para = doc.add_paragraph(lecture.equipment, style='LectureContent')
    
    # --- Activities Section ---
    doc.add_paragraph('CÁC HOẠT ĐỘNG HỌC TẬP', style='LectureSection')
    
    for idx, activity in enumerate(lecture.activities, 1):
        # Activity title
        activity_title = f"Hoạt động {idx}: {activity.name}"
        activity_para = doc.add_paragraph(activity_title)
        activity_para.style.font.name = 'Times New Roman'
        activity_para.style.font.size = Pt(13)
        activity_para.style.font.bold = True
        activity_para.style.font.color.rgb = RGBColor(139, 69, 19)  # Brown color
        activity_para.paragraph_format.space_before = Pt(12)
        activity_para.paragraph_format.space_after = Pt(6)
        
        # Activity details
        if activity.goals:
            goals_para = doc.add_paragraph()
            goals_run = goals_para.add_run('Mục tiêu: ')
            goals_run.bold = True
            goals_para.add_run(activity.goals)
            goals_para.style = content_style
        
        if activity.content:
            content_para = doc.add_paragraph()
            content_run = content_para.add_run('Nội dung: ')
            content_run.bold = True
            content_para.add_run(activity.content)
            content_para.style = content_style
        
        if activity.products:
            products_para = doc.add_paragraph()
            products_run = products_para.add_run('Sản phẩm: ')
            products_run.bold = True
            products_para.add_run(activity.products)
            products_para.style = content_style
        
        # Activity table
        if activity.table and len(activity.table) > 0:
            # Create table
            num_rows = len(activity.table) + 1  # +1 for header
            num_cols = 2  # Teacher and student activities
            
            table = doc.add_table(rows=num_rows, cols=num_cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Header row
            header_row = table.rows[0]
            header_row.cells[0].text = 'HOẠT ĐỘNG CỦA GIÁO VIÊN'
            header_row.cells[1].text = 'HOẠT ĐỘNG CỦA HỌC SINH'
            
            # Style header cells
            for cell in header_row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_cell_border(cell)
                # Set background color for header
                cell._element.get_or_add_tcPr().append(
                    OxmlElement('w:shd')).set(qn('w:fill'), '4472C4')
            
            # Data rows
            for row_idx, row_data in enumerate(activity.table, 1):
                table_row = table.rows[row_idx]
                
                # Handle different possible key formats
                teacher_activity = ""
                student_activity = ""
                
                for key, value in row_data.items():
                    if 'giáo viên' in key.lower() or 'teacher' in key.lower():
                        teacher_activity = value
                    elif 'học sinh' in key.lower() or 'student' in key.lower():
                        student_activity = value
                
                table_row.cells[0].text = teacher_activity
                table_row.cells[1].text = student_activity
                
                # Set borders for data cells
                for cell in table_row.cells:
                    set_cell_border(cell)
            
            # Set column widths
            for row in table.rows:
                for cell in row.cells:
                    cell.width = Inches(3.2)
            
            # Add spacing after table
            doc.add_paragraph()
        
        # Add page break between activities (except last one)
        if idx < len(lecture.activities):
            paragraph = doc.add_paragraph()
            run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
            run.add_break(break_type=6)  # Page break
    
    # --- Footer ---
    footer_section = doc.sections[0]
    footer = footer_section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "Bài giảng được tạo bởi Hệ thống AI Giáo dục"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.style.font.size = Pt(9)
    footer_para.style.font.italic = True
    
    # --- Generate file ---
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    # --- Return StreamingResponse ---
    headers = {
        'Content-Disposition': f'attachment; filename="{file_name}"'
    }
    
    return StreamingResponse(
        content=file_stream,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers=headers
    )