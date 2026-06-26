from docx.oxml.section import CT_SectPr
from docx.oxml.table import CT_Tbl
from docxcompose.composer import Composer

def fix_subdoc(masterdoc, subdoc_info):
    """Fix the images, styles, references, shapes, etc of a subdoc"""
    for section in masterdoc.sections:
        for part in section.part.package.parts:
            if part.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml" and not isinstance(part._blob, bytes):
                part._blob = part._blob.encode('utf-8')
    subdoc = subdoc_info['subdoc']
    change_numbering = subdoc_info['change_numbering']
    composer = Composer(masterdoc)  # Using docxcompose
    composer.reset_reference_mapping()

    # This is the same as the docxcompose function, except it doesn't copy the elements over.
    # Copying the elements over is done by returning the subdoc XML in this function.
    # Both sd.subdocx and the master template file are changed with these functions.
    composer._create_style_id_mapping(subdoc)
    for element in subdoc.element.body:
        if isinstance(element, CT_SectPr):
            continue
        composer.add_referenced_parts(subdoc.part, masterdoc.part, element)
        composer.add_styles(subdoc, element)
        if change_numbering and not isinstance(element, CT_Tbl):
            try:
                composer.add_numberings(subdoc, element)
                composer.restart_first_numbering(subdoc, element)
            except:
                pass
        composer.add_images(subdoc, element)
        composer.add_shapes(subdoc, element)
        composer.add_footnotes(subdoc, element)
        composer.remove_header_and_footer_references(subdoc, element)

    composer.add_styles_from_other_parts(subdoc)
    composer.renumber_bookmarks()
    composer.renumber_docpr_ids()
    composer.fix_section_types(subdoc)
