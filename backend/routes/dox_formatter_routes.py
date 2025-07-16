from fastapi import APIRouter
from schemas.docx_model import DocumentRequest
from fastapi.responses import StreamingResponse
import io
from docx import Document as DocxDocument
from docx.shared import Inches
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter(prefix="/api/v1/docx", tags=["docx"])

@router.post("/format-and-download")
async def create_document_from_text(request: DocumentRequest):
    """
    Accepts raw text in a JSON request, formats it into a .docx file in memory,
    and returns it for download. Now with table support!
    """
    doc = DocxDocument()
    
    # --- Formatting Logic ---
    lines = request.raw_text.strip().split('\n')
    i = 0
    
    while i < len(lines):
        stripped_line = lines[i].strip()
        
        if not stripped_line:
            i += 1
            continue
        
        # Check for table start marker
        if stripped_line == '[TABLE_START]':
            # Create table
            table_data = []
            i += 1
            
            # Read table content until TABLE_END
            while i < len(lines) and lines[i].strip() != '[TABLE_END]':
                table_line = lines[i].strip()
                if table_line and table_line != '---|---':  # Skip separator line
                    # Split by | and clean up cells
                    cells = [cell.strip() for cell in table_line.split('|')]
                    table_data.append(cells)
                i += 1
            
            # Create table in document
            if table_data:
                num_rows = len(table_data)
                num_cols = len(table_data[0]) if table_data else 2
                
                table = doc.add_table(rows=num_rows, cols=num_cols)
                table.style = 'Table Grid'
                table.alignment = WD_TABLE_ALIGNMENT.CENTER
                
                # Populate table
                for row_idx, row_data in enumerate(table_data):
                    row = table.rows[row_idx]
                    for col_idx, cell_data in enumerate(row_data[:num_cols]):
                        cell = row.cells[col_idx]
                        cell.text = cell_data
                        
                        # Bold the header row
                        if row_idx == 0:
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.bold = True
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                # Set column widths (optional - adjust as needed)
                for row in table.rows:
                    for idx, cell in enumerate(row.cells):
                        cell.width = Inches(3.0)  # Each column 3 inches wide
            
            # Add spacing after table
            doc.add_paragraph()
            
        # Handle headings
        elif stripped_line.startswith('#### '):
            doc.add_heading(stripped_line.replace('#### ', ''), level=4)
        elif stripped_line.startswith('### '):
            doc.add_heading(stripped_line.replace('### ', ''), level=3)
        elif stripped_line.startswith('## '):
            doc.add_heading(stripped_line.replace('## ', ''), level=2)
        elif stripped_line.startswith('# '):
            doc.add_heading(stripped_line.replace('# ', ''), level=1)
        
        # Handle list items
        elif stripped_line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            clean_line = stripped_line[2:]  # Remove '- '
            parts = clean_line.split('**')
            for j, part in enumerate(parts):
                if j % 2 == 1:
                    p.add_run(part).bold = True
                else:
                    p.add_run(part)
        
        # Handle regular paragraphs
        else:
            p = doc.add_paragraph()
            parts = stripped_line.split('**')
            for j, part in enumerate(parts):
                if j % 2 == 1:
                    p.add_run(part).bold = True
                else:
                    p.add_run(part)
        
        i += 1
    
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