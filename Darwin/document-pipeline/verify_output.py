from docx import Document

doc = Document('output/darwin-reformatted-ca_discovery-1784762004390.docx')

print("=== Document Content ===")
for i, para in enumerate(doc.paragraphs):
    runs = para.runs
    formatting = ""
    if runs:
        run = runs[0]
        formatting = f"[Bold={run.bold}, Size={run.font.size}, Font={run.font.name}]"
    print(f"Para {i}: {para.text[:60]:<60} {formatting}")

print("\n=== Margins ===")
sections = doc.sections
for section in sections:
    margins = section.margins
    print(f"Top: {margins.top}, Bottom: {margins.bottom}, Left: {margins.left}, Right: {margins.right}")
