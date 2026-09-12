import subprocess
import sys
from pathlib import Path

import pikepdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas

sys.path.insert(0, str(Path(__file__).parents[1] / 'docassemble_base'))
from docassemble.base.pdftk import fill_template, prepare_accessible_flatten


def make_form(filename):
    canvas = Canvas(str(filename), pagesize=letter)
    canvas.drawString(36, 580, 'Comments')
    canvas.acroForm.textfield(
        name='comments',
        x=36,
        y=500,
        width=180,
        height=60,
        fieldFlags='multiline',
        fontName='Helvetica',
        fontSize=10,
    )
    canvas.acroForm.checkbox(name='agree', x=36, y=450, buttonStyle='check')
    canvas.acroForm.checkbox(name='decline', x=36, y=420, buttonStyle='check')
    canvas.save()


def tag_widget(filename, field_name, struct_parent=42, tooltip=None):
    """Give one reportlab widget the minimal valid Form/OBJR structure anchor."""
    with pikepdf.Pdf.open(str(filename), allow_overwriting_input=True) as pdf:
        widget = next(
            annot
            for page in pdf.pages
            for annot in page.Annots
            if str(annot.get('/T')) == field_name
        )
        page = next(page for page in pdf.pages if widget in page.Annots)
        root = pdf.make_indirect(pikepdf.Dictionary(Type=pikepdf.Name('/StructTreeRoot')))
        element = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name('/StructElem'),
            S=pikepdf.Name('/Form'),
            P=root,
        ))
        element.K = pikepdf.Dictionary(
            Type=pikepdf.Name('/OBJR'),
            Pg=page.obj,
            Obj=widget,
        )
        root.K = pikepdf.Array([element])
        root.ParentTree = pikepdf.Dictionary(
            Nums=pikepdf.Array([struct_parent, element])
        )
        root.ParentTreeNextKey = struct_parent + 1
        widget.StructParent = struct_parent
        if tooltip:
            widget.TU = pikepdf.String(tooltip)
        pdf.Root.StructTreeRoot = root
        pdf.Root.MarkInfo = pikepdf.Dictionary(Marked=True)
        pdf.save()


def printfield_element(pdf):
    return pdf.Root.StructTreeRoot.K[0]


def form_xobjects(pdf):
    for page in pdf.pages:
        for xobject in page.Resources.get('/XObject', {}).values():
            yield xobject.read_bytes()


def test_flattened_multiline_field_uses_wrapping(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    output = fill_template(
        str(template),
        data_strings=[('comments', 'This is a long value that should wrap automatically across multiple lines.')],
        data_names={},
        editable=False,
        images=[],
        use_pdftk=False,
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            assert not any(
                annot.get('/Subtype') == '/Widget'
                for page in pdf.pages
                for annot in page.get('/Annots', [])
            )
            acroform = pdf.Root.get('/AcroForm')
            assert acroform is None or not acroform.get('/Fields')
            content = subprocess.check_output(['pdftotext', '-layout', output, '-']).decode()
            assert 'This is a long value that should wrap' in content
            assert 'automatically across multiple lines.' in content
    finally:
        Path(output).unlink(missing_ok=True)


def test_flattened_checkbox_labels_follow_checked_state(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    output = fill_template(
        str(template),
        data_strings=[('agree', 'Yes'), ('decline', 'Off')],
        data_names={},
        editable=False,
        images=[],
        use_pdftk=False,
        flattened_checkbox_label='[X]',
        flattened_checkbox_unselected_label='[ ]',
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            content = b'\n'.join(form_xobjects(pdf))
            assert b'[X]' in content
            assert b'[ ]' in content
    finally:
        Path(output).unlink(missing_ok=True)


def test_flattened_checkbox_actual_text_supports_unicode(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    output = fill_template(
        str(template),
        data_strings=[('agree', 'Yes'), ('decline', 'Off')],
        data_names={},
        editable=False,
        images=[],
        flattened_checkbox_label='case à cocher, cochée',
        flattened_checkbox_unselected_label='case à cocher, non cochée',
    )
    try:
        content = subprocess.check_output(['pdftotext', '-layout', output, '-']).decode()
        assert 'case à cocher, cochée' in content
        assert 'case à cocher, non cochée' in content
    finally:
        Path(output).unlink(missing_ok=True)


def test_tagged_checkbox_becomes_printfield_on_the_painted_xobject(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    tag_widget(template, 'agree', tooltip='I agree to the terms')
    output = fill_template(
        str(template),
        data_strings=[('comments', 'Two lines\nof accessible text'), ('agree', 'Yes'), ('decline', 'Off')],
        data_names={},
        editable=False,
        images=[],
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            element = printfield_element(pdf)
            appearance = element.K.Stm
            assert element.A.O == '/PrintField'
            assert element.A.Role == '/cb'
            assert element.A.get('/checked') == '/on'
            assert str(element.A.Desc) == 'I agree to the terms'
            assert appearance.get('/StructParents') == 42
            assert appearance.get('/StructParent') is None
            assert element.K.Type == '/MCR'
            assert element.K.MCID == 0
            assert element.K.Stm.objgen == appearance.objgen
            assert element.K.get('/Obj') is None
            assert pdf.Root.StructTreeRoot.ParentTree.Nums[1][0].objgen == element.objgen
            assert b'/MCID 0' in appearance.read_bytes()
            assert any(
                item.objgen == appearance.objgen
                for item in pdf.pages[0].Resources.XObject.values()
            )
            assert not any(
                annot.get('/Subtype') == '/Widget'
                for page in pdf.pages
                for annot in page.get('/Annots', [])
            )
    finally:
        Path(output).unlink(missing_ok=True)


def test_tagged_unchecked_checkbox_uses_off_state_without_fallback_text(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    # Some real court forms draw the empty box in the page content and provide
    # only an on-state appearance for the widget.
    with pikepdf.Pdf.open(template, allow_overwriting_input=True) as pdf:
        agree = next(annot for annot in pdf.pages[0].Annots if str(annot.get('/T')) == 'agree')
        del agree.AP.N[pikepdf.Name('/Off')]
        pdf.save()
    tag_widget(template, 'agree')
    output = fill_template(
        str(template),
        data_strings=[('agree', 'Off'), ('decline', 'Off')],
        data_names={},
        editable=False,
        images=[],
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            assert printfield_element(pdf).A.get('/checked') == '/off'
        content = subprocess.check_output(['pdftotext', output, '-']).decode()
        # Only the untagged second checkbox needs text fallback.
        assert content.count('checkbox, unchecked') == 1
    finally:
        Path(output).unlink(missing_ok=True)


def test_shared_appearance_xobjects_are_given_separate_structure_identity(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    with pikepdf.Pdf.open(template, allow_overwriting_input=True) as pdf:
        widgets = [
            annot for annot in pdf.pages[0].Annots
            if str(annot.get('/T')) in ('agree', 'decline')
        ]
        for widget in widgets:
            widget.AS = pikepdf.Name('/Yes')
        widgets[1].AP.N[pikepdf.Name('/Yes')] = widgets[0].AP.N[pikepdf.Name('/Yes')]
        root = pdf.make_indirect(pikepdf.Dictionary(Type=pikepdf.Name('/StructTreeRoot')))
        elements = []
        numbers = pikepdf.Array()
        for index, widget in enumerate(widgets, start=42):
            element = pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name('/StructElem'),
                S=pikepdf.Name('/Form'),
                P=root,
            ))
            element.K = pikepdf.Dictionary(
                Type=pikepdf.Name('/OBJR'), Pg=pdf.pages[0].obj, Obj=widget
            )
            widget.StructParent = index
            elements.append(element)
            numbers.extend([index, element])
        root.K = pikepdf.Array(elements)
        root.ParentTree = pikepdf.Dictionary(Nums=numbers)
        pdf.Root.StructTreeRoot = root

        prepare_accessible_flatten(pdf)

        appearances = [widget.AP.N[widget.AS] for widget in widgets]
        assert appearances[0].objgen != appearances[1].objgen
        assert [appearance.StructParents for appearance in appearances] == [42, 43]
        assert [element.K.Stm.objgen for element in elements] == [
            appearance.objgen for appearance in appearances
        ]
        assert [element.K.MCID for element in elements] == [0, 0]
        assert [root.ParentTree.Nums[index][0].objgen for index in (1, 3)] == [
            element.objgen for element in elements
        ]


def test_pdftk_flatten_preserves_non_widget_annotations(tmp_path):
    template = tmp_path / 'template.pdf'
    canvas = Canvas(str(template), pagesize=letter)
    canvas.drawString(36, 700, 'Website')
    canvas.linkURL('https://example.com', (36, 695, 100, 715), relative=0)
    canvas.acroForm.checkbox(name='agree', x=36, y=650, buttonStyle='check')
    canvas.save()
    output = fill_template(
        str(template),
        data_strings=[('agree', 'Yes')],
        data_names={},
        editable=False,
        images=[],
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            annotations = list(pdf.pages[0].get('/Annots', []))
            assert [annot.get('/Subtype') for annot in annotations] == ['/Link']
            assert str(annotations[0].A.URI) == 'https://example.com'
    finally:
        Path(output).unlink(missing_ok=True)


def make_button_form(filename):
    """A form with a radio group and a checkbox whose export value is /On."""
    canvas = Canvas(str(filename), pagesize=letter)
    canvas.drawString(36, 700, 'Choices')
    canvas.acroForm.checkbox(name='onbox', x=36, y=650, buttonStyle='check')
    canvas.acroForm.radio(name='color', value='red', selected=True, x=36, y=600, buttonStyle='circle')
    canvas.acroForm.radio(name='color', value='green', selected=False, x=66, y=600, buttonStyle='circle')
    canvas.acroForm.radio(name='color', value='blue', selected=False, x=96, y=600, buttonStyle='circle')
    canvas.save()
    with pikepdf.Pdf.open(str(filename), allow_overwriting_input=True) as pdf:
        for page in pdf.pages:
            for annot in page.Annots:
                if annot.get('/T') is not None and str(annot.T) == 'onbox':
                    states = annot.AP.N
                    states[pikepdf.Name('/On')] = states[pikepdf.Name('/Yes')]
                    del states[pikepdf.Name('/Yes')]
                    # The default appearance an authoring tool gives a checkbox names
                    # the font the check mark is drawn in, which cannot render a label.
                    annot.DA = pikepdf.String('/ZaDb 0 Tf 0 g')
        pdf.save()


def flattened_content(filename):
    with pikepdf.Pdf.open(filename) as pdf:
        return b'\n'.join(form_xobjects(pdf))


def test_flattened_radio_group_labels_only_the_selected_option(tmp_path):
    template = tmp_path / 'template.pdf'
    make_button_form(template)
    output = fill_template(
        str(template),
        data_strings=[('color', 'green'), ('onbox', 'Off')],
        data_names={},
        editable=False,
        images=[],
        use_pdftk=False,
        flattened_checkbox_label='[X]',
        flattened_checkbox_unselected_label='[ ]',
    )
    try:
        content = subprocess.check_output(['pdftotext', '-layout', output, '-']).decode()
        assert content.count('radio button, selected') == 1
        assert content.count('radio button, unselected') == 2
        assert content.count('[ ]') == 1
    finally:
        Path(output).unlink(missing_ok=True)


def test_flattened_checkbox_with_on_export_value_reads_as_unchecked(tmp_path):
    template = tmp_path / 'template.pdf'
    make_button_form(template)
    output = fill_template(
        str(template),
        data_strings=[('onbox', 'No'), ('color', 'Off')],
        data_names={},
        editable=False,
        images=[],
        use_pdftk=False,
    )
    try:
        content = flattened_content(output)
        assert b'checkbox, unchecked' in content
        assert b'checkbox, checked' not in content
        # ZapfDingbats cannot draw the label, so the widget's own default appearance
        # must not be what the label is rendered with.
        assert b'/ZaDb' not in content
    finally:
        Path(output).unlink(missing_ok=True)


def test_editable_output_asks_the_viewer_to_regenerate_appearances(tmp_path):
    template = tmp_path / 'template.pdf'
    make_form(template)
    output = fill_template(
        str(template),
        data_strings=[('comments', 'Ünïcødé — beyond what qpdf can render')],
        data_names={},
        editable=True,
        images=[],
        use_pdftk=False,
    )
    try:
        with pikepdf.Pdf.open(output) as pdf:
            assert pdf.Root.AcroForm.get('/NeedAppearances') is True
    finally:
        Path(output).unlink(missing_ok=True)


def test_flattened_checkbox_label_is_invisible_and_does_not_need_to_fit(tmp_path):
    template = tmp_path / 'template.pdf'
    canvas = Canvas(str(template), pagesize=letter)
    canvas.drawString(36, 700, 'Small')
    canvas.acroForm.checkbox(name='tiny', x=36, y=650, size=9, buttonStyle='check')
    canvas.save()
    output = fill_template(
        str(template),
        data_strings=[('tiny', 'Yes')],
        data_names={},
        editable=False,
        images=[],
        use_pdftk=False,
    )
    try:
        content = flattened_content(output)
        assert b'checkbox, checked' in content
        assert b'3 Tr' in content
    finally:
        Path(output).unlink(missing_ok=True)
