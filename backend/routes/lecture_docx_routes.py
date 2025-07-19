from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from typing import List, Dict, Optional
import io
from docx import Document as DocxDocument
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.shared import OxmlElement, qn

router = APIRouter(prefix="/api/v1/lecture-docx", tags=["lecture-docx"])

class LectureDocxRequest(BaseModel):
    title: str
    goals: str
    equipment: str
    activities: List[Dict]  # List of activity dictionaries
    metadata: Optional[Dict] = None  # Subject, grade, lesson, date info
    file_name: str = "bai_giang.docx"

def add_page_break(doc):
    """Add a page break to the document"""
    paragraph = doc.add_paragraph()
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.add_break(break_type=6)  # Page break

def set_cell_border(cell, **kwargs):
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

@router.post("/format-lecture")
async def create_lecture_docx(request: LectureDocxRequest):
    """
    Create a professionally formatted DOCX document specifically for lectures.
    Optimized for educational content with proper styling, headers, and table formatting.
    """
    doc = DocxDocument()
    
    # --- Document Styling Setup ---
    styles = doc.styles
    
    # Create custom styles
    title_style = styles.add_style('LectureTitle', WD_STYLE_TYPE.PARAGRAPH)
    title_style.font.name = 'Times New Roman'
    title_style.font.size = Pt(18)
    title_style.font.bold = True
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_style.paragraph_format.space_after = Pt(12)
    
    section_style = styles.add_style('LectureSection', WD_STYLE_TYPE.PARAGRAPH)
    section_style.font.name = 'Times New Roman'
    section_style.font.size = Pt(14)
    section_style.font.bold = True
    section_style.font.color.rgb = RGBColor(0, 51, 102)  # Dark blue
    section_style.paragraph_format.space_before = Pt(12)
    section_style.paragraph_format.space_after = Pt(6)
    
    content_style = styles.add_style('LectureContent', WD_STYLE_TYPE.PARAGRAPH)
    content_style.font.name = 'Times New Roman'
    content_style.font.size = Pt(12)
    content_style.paragraph_format.line_spacing = 1.15
    content_style.paragraph_format.space_after = Pt(6)
    
    # --- Header with metadata ---
    if request.metadata:
        header_section = doc.sections[0]
        header = header_section.header
        header_para = header.paragraphs[0]
        header_para.text = f"Môn: {request.metadata.get('subject', '')} | Lớp: {request.metadata.get('grade', '')} | Ngày: {request.metadata.get('created', '')[:10] if request.metadata.get('created') else ''}"
        header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header_para.style.font.size = Pt(10)
    
    # --- Title ---
    title_para = doc.add_paragraph(request.title.upper(), style='LectureTitle')
    
    # --- Goals Section ---
    doc.add_paragraph('MỤC TIÊU BÀI HỌC', style='LectureSection')
    goals_para = doc.add_paragraph(request.goals, style='LectureContent')
    
    # --- Equipment Section ---
    doc.add_paragraph('THIẾT BỊ VÀ DỤNG CỤ', style='LectureSection')
    equipment_para = doc.add_paragraph(request.equipment, style='LectureContent')
    
    # --- Activities Section ---
    doc.add_paragraph('CÁC HOẠT ĐỘNG HỌC TẬP', style='LectureSection')
    
    for idx, activity in enumerate(request.activities, 1):
        # Activity title
        activity_title = f"Hoạt động {idx}: {activity.get('name', f'Hoạt động {idx}')}"
        activity_para = doc.add_paragraph(activity_title)
        activity_para.style.font.name = 'Times New Roman'
        activity_para.style.font.size = Pt(13)
        activity_para.style.font.bold = True
        activity_para.style.font.color.rgb = RGBColor(139, 69, 19)  # Brown color
        activity_para.paragraph_format.space_before = Pt(12)
        activity_para.paragraph_format.space_after = Pt(6)
        
        # Activity details
        if activity.get('goals'):
            goals_para = doc.add_paragraph()
            goals_run = goals_para.add_run('Mục tiêu: ')
            goals_run.bold = True
            goals_para.add_run(activity['goals'])
            goals_para.style = content_style
        
        if activity.get('content'):
            content_para = doc.add_paragraph()
            content_run = content_para.add_run('Nội dung: ')
            content_run.bold = True
            content_para.add_run(activity['content'])
            content_para.style = content_style
        
        if activity.get('products'):
            products_para = doc.add_paragraph()
            products_run = products_para.add_run('Sản phẩm: ')
            products_run.bold = True
            products_para.add_run(activity['products'])
            products_para.style = content_style
        
        # Activity table
        table_data = activity.get('table', [])
        if table_data and len(table_data) > 0:
            # Create table
            num_rows = len(table_data) + 1  # +1 for header
            first_row = table_data[0]
            headers = list(first_row.keys()) if isinstance(first_row, dict) else ['Hoạt động của giáo viên', 'Hoạt động của học sinh']
            num_cols = len(headers)
            
            table = doc.add_table(rows=num_rows, cols=num_cols)
            table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Header row
            header_row = table.rows[0]
            for col_idx, header in enumerate(headers):
                cell = header_row.cells[col_idx]
                cell.text = header.upper()
                # Style header cells
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                # Set background color for header
                set_cell_border(cell)
            
            # Data rows
            for row_idx, row_data in enumerate(table_data, 1):
                table_row = table.rows[row_idx]
                if isinstance(row_data, dict):
                    for col_idx, header in enumerate(headers):
                        cell = table_row.cells[col_idx]
                        cell.text = row_data.get(header, '')
                        set_cell_border(cell)
                
            # Set column widths
            for row in table.rows:
                for cell in row.cells:
                    cell.width = Inches(3.2)
            
            # Add spacing after table
            doc.add_paragraph()
        
        # Add page break between activities (except last one)
        if idx < len(request.activities):
            add_page_break(doc)
    
    # --- Footer ---
    footer_section = doc.sections[0]
    footer = footer_section.footer
    footer_para = footer.paragraphs[0]
    footer_para.text = "Bài giảng được tạo bởi Hệ thống AI Giáo dục"
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_para.style.font.size = Pt(9)
    footer_para.style.font.italic = True
    
    # --- In-Memory File Handling ---
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    # --- Custom Headers ---
    headers = {
        'Content-Disposition': f'attachment; filename="{request.file_name}"'
    }
    
    # --- Return StreamingResponse ---
    return StreamingResponse(
        content=file_stream,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        headers=headers
    )