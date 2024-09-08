from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, FrameBreak, NextPageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import blue
from reportlab.platypus.doctemplate import LayoutError, PageTemplate
from io import BytesIO
import requests
from PIL import Image as PILImage
from parser import process_rss_feed
from datetime import datetime

class PDFWithTOC(SimpleDocTemplate):
    def __init__(self, *args, **kwargs):
        SimpleDocTemplate.__init__(self, *args, **kwargs)
        self.toc = []

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                key = 'h1-%s' % self.seq.nextf('heading1')
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, 0, 0)
                self.toc.append((0, text, self.page))
            elif style == 'Heading2':
                key = 'h2-%s' % self.seq.nextf('heading2')
                self.canv.bookmarkPage(key)
                self.canv.addOutlineEntry(text, key, 1, 0)
                self.toc.append((1, text, self.page))

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 10)
    canvas.drawString(inch, 0.75 * inch, f"Page {doc.page}")
    canvas.restoreState()

def create_pdf(articles_by_source, output_filename):
    page_width, page_height = letter
    margin = 1 * inch  # Increased margin
    
    doc = PDFWithTOC(output_filename, pagesize=letter,
                     rightMargin=margin, leftMargin=margin,
                     topMargin=margin, bottomMargin=margin)
    
    # Two-column layout
    frame1 = Frame(margin, margin, (page_width - 3*margin)/2, page_height - 2*margin, id='col1')
    frame2 = Frame((page_width + margin)/2, margin, (page_width - 3*margin)/2, page_height - 2*margin, id='col2')
    
    two_column_template = PageTemplate(id='TwoColumn', frames=[frame1, frame2], onPage=add_page_number)
    doc.addPageTemplates([two_column_template])
    
    available_width = (page_width - 3*margin) / 2  # Width for each column
    available_height = page_height - 2*margin
    scale_factor = 0.8
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=12, leading=14))  # Increased font size
    styles.add(ParagraphStyle(name='Caption', 
                              parent=styles['Normal'],
                              fontName='Helvetica-Oblique',
                              fontSize=10,
                              leading=12,
                              alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='TOCEntry',
                              parent=styles['Normal'],
                              fontSize=12,
                              leading=14))
    
    # Increase font sizes for headings
    styles['Title'].fontSize = 24
    styles['Heading1'].fontSize = 18
    styles['Heading2'].fontSize = 16
    
    Story = []
    
    # Add title and date
    Story.append(NextPageTemplate('TwoColumn'))
    Story.append(Paragraph("Daily News Summary", styles['Title']))
    Story.append(Spacer(1, 24))
    current_date = datetime.now().strftime("%Y-%m-%d")
    Story.append(Paragraph(f"Generated on: {current_date}", styles['Normal']))
    Story.append(Spacer(1, 24))
    
    # Table of Contents
    Story.append(Paragraph("Table of Contents", styles['Heading1']))
    Story.append(Spacer(1, 12))
    
    for source, articles in articles_by_source.items():
        Story.append(Paragraph(source, styles['TOCEntry']))
        for article in articles:
            Story.append(Paragraph(f"  {article['title']}", styles['TOCEntry']))
    
    Story.append(PageBreak())
    
    # Ensure two-column layout for the main content
    Story.append(NextPageTemplate('TwoColumn'))
    
    for source, articles in articles_by_source.items():
        Story.append(Paragraph(source, styles['Heading1']))
        Story.append(Spacer(1, 12))
        
        for article in articles:
            Story.append(Paragraph(article['title'], styles['Heading2']))
            Story.append(Spacer(1, 12))
            Story.append(Paragraph(f"Published: {article['pubDate']}", styles['Italic']))
            Story.append(Spacer(1, 12))
            
            for item_type, item in article['full_content']:
                if item_type == 'text':
                    Story.append(Paragraph(item, styles['Justify']))
                    Story.append(Spacer(1, 12))
                elif item_type == 'image':
                    try:
                        img_data = requests.get(item['url'], timeout=10).content
                        img = PILImage.open(BytesIO(img_data))
                        
                        img_width, img_height = img.size
                        aspect = img_width / img_height
                        
                        max_width = available_width * scale_factor
                        max_height = available_height * scale_factor
                        
                        if img_width > max_width:
                            img_width = max_width
                            img_height = img_width / aspect
                        
                        if img_height > max_height:
                            img_height = max_height
                            img_width = img_height * aspect
                        
                        if img_width >= 100 and img_height >= 100:
                            img_rl = RLImage(BytesIO(img_data), width=img_width, height=img_height)
                            Story.append(img_rl)
                            Story.append(Spacer(1, 12))
                            caption = item.get('caption') or item.get('alt', '')
                            if caption:
                                Story.append(Paragraph(f"Image: {caption}", styles['Caption']))
                                Story.append(Spacer(1, 12))
                    except Exception as e:
                        print(f"Error processing image: {e}")
                        continue
            
            Story.append(Spacer(1, 24))
            Story.append(FrameBreak())  # Move to next column or page after each article


    try:
        doc.multiBuild(Story)
        print(f"PDF created successfully: {output_filename}")
    except LayoutError as e:
        print(f"LayoutError encountered during build: {e}")
        print("The PDF may be incomplete, but it should still be usable.")

if __name__ == "__main__":
    rss_sources = {
        "La Vanguardia": "https://www.lavanguardia.com/rss/home.xml",
        # Add more sources here
    }
    
    articles_by_source = {}
    for source_name, rss_url in rss_sources.items():
        articles = process_rss_feed(rss_url, hours=24)
        if articles:
            articles_by_source[source_name] = articles
    
    if articles_by_source:
        output_filename = f"daily_news_{datetime.now().strftime('%Y%m%d')}.pdf"
        create_pdf(articles_by_source, output_filename)
    else:
        print("No articles found in the last 24 hours.")