"""Post-process pandoc's docx so it passes strict OOXML validation: pStyle first in pPr, tblPr child order, 8-hex-digit nsid values."""
import zipfile, shutil, sys, re
from lxml import etree
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"; q = lambda t: f"{{{W}}}{t}"
src = sys.argv[1]; tmp = src + ".tmp"
order_tblPr = ["tblStyle","tblpPr","tblOverlap","bidiVisual","tblStyleRowBandSize","tblStyleColBandSize","tblW","jc","tblCellSpacing","tblInd","tblBorders","shd","tblLayout","tblCellMar","tblLook","tblCaption","tblDescription"]
PPR = ["pStyle","keepNext","keepLines","pageBreakBefore","framePr","widowControl","numPr","suppressLineNumbers","pBdr","shd","tabs","suppressAutoHyphens","kinsoku","wordWrap","overflowPunct","topLinePunct","autoSpaceDE","autoSpaceDN","bidi","adjustRightInd","snapToGrid","spacing","ind","contextualSpacing","mirrorIndents","suppressOverlap","jc","textDirection","textAlignment","textboxTightWrap","outlineLvl","divId","cnfStyle","rPr","sectPr","pPrChange"]
def reorder(parent, order):
    kids = list(parent); keyed = sorted(kids, key=lambda e: order.index(etree.QName(e).localname) if etree.QName(e).localname in order else 99)
    if keyed != kids:
        for k in kids: parent.remove(k)
        for k in keyed: parent.append(k)
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/document.xml":
            root = etree.fromstring(data, etree.XMLParser(remove_blank_text=True))
            for ppr in root.iter(q("pPr")): reorder(ppr, PPR)
            for tp in root.iter(q("tblPr")): reorder(tp, order_tblPr)
            for tc in root.iter(q("tcPr")): reorder(tc, ["cnfStyle","tcW","gridSpan","hMerge","vMerge","tcBorders","shd","noWrap","tcMar","textDirection","tcFitText","vAlign","hideMark"])
            data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        if item.filename == "word/styles.xml":
            root = etree.fromstring(data, etree.XMLParser(remove_blank_text=True)); order = ["name","aliases","basedOn","next","link","autoRedefine","hidden","uiPriority","semiHidden","unhideWhenUsed","qFormat","locked","personal","personalCompose","personalReply","rsid","pPr","rPr","tblPr","trPr","tcPr","tblStylePr"]
            for st in root.iter(q("style")):
                kids = list(st); keyed = sorted(kids, key=lambda e: order.index(etree.QName(e).localname) if etree.QName(e).localname in order else 99)
                if keyed != kids:
                    for k in kids: st.remove(k)
                    for k in keyed: st.append(k)
            for ppr in root.iter(q("pPr")): reorder(ppr, PPR)
            for tc in root.iter(q("tcPr")): reorder(tc, ["cnfStyle","tcW","gridSpan","hMerge","vMerge","tcBorders","shd","noWrap","tcMar","textDirection","tcFitText","vAlign","hideMark"])
            for tp in root.iter(q("tblPr")): reorder(tp, order_tblPr)
            for rp in root.iter(q("rPr")):
                rp.text = None
                for c in rp: c.tail = None
            data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        if item.filename.startswith("word/") and item.filename.endswith(".xml") and item.filename not in ("word/document.xml","word/styles.xml"):
            try:
                root = etree.fromstring(data, etree.XMLParser(remove_blank_text=True))
                for ppr in root.iter(q("pPr")): reorder(ppr, PPR)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            except etree.XMLSyntaxError as e: print("left unchanged (not well-formed XML):", item.filename, e)
        if item.filename == "word/settings.xml":
            root = etree.fromstring(data, etree.XMLParser(remove_blank_text=True))
            head = ["writeProtection","view","zoom","removePersonalInformation","removeDateAndTime","doNotDisplayPageBoundaries","displayBackgroundShape","printPostScriptOverText","printFractionalCharacterWidth","printFormsData","embedTrueTypeFonts","embedSystemFonts","saveSubsetFonts","saveFormsData","mirrorMargins","alignBordersAndEdges","bordersDoNotSurroundHeader","bordersDoNotSurroundFooter","gutterAtTop","hideSpellingErrors","hideGrammaticalErrors","activeWritingStyle","proofState","formsDesign","attachedTemplate","linkStyles","stylePaneFormatFilter","stylePaneSortMethod","documentType","mailMerge","revisionView","trackRevisions","doNotTrackMoves","doNotTrackFormatting","documentProtection","autoFormatOverride","styleLockTheme","styleLockQFSet","defaultTabStop","autoHyphenation","consecutiveHyphenLimit","hyphenationZone","doNotHyphenateCaps","showEnvelope","summaryLength","clickAndTypeStyle","defaultTableStyle","evenAndOddHeaders","bookFoldRevPrinting","bookFoldPrinting","bookFoldPrintingSheets","drawingGridHorizontalSpacing","drawingGridVerticalSpacing","displayHorizontalDrawingGridEvery","displayVerticalDrawingGridEvery","doNotUseMarginsForDrawingGridOrigin","drawingGridHorizontalOrigin","drawingGridVerticalOrigin","doNotShadeFormData","noPunctuationKerning","characterSpacingControl","printTwoOnOne","strictFirstAndLastChars","noLineBreaksAfter","noLineBreaksBefore","savePreviewPicture","doNotValidateAgainstSchema","saveInvalidXml","ignoreMixedContent","alwaysShowPlaceholderText","doNotDemarcateInvalidXml","saveXmlDataOnly","useXSLTWhenSaving","saveThroughXslt","showXMLTags","alwaysMergeEmptyNamespace","updateFields","hdrShapeDefaults","footnotePr","endnotePr","compat","docVars","rsids","mathPr","attachedSchema","themeFontLang","clrSchemeMapping","doNotIncludeSubdocsInStats","doNotAutoCompressPictures","forceUpgrade","captions","readModeInkLockDown","smartTagType","schemaLibrary","shapeDefaults","doNotEmbedSmartTags","decimalSymbol","listSeparator"]
            reorder(root, head); data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        if item.filename == "word/numbering.xml":
            data = re.sub(rb'(<w:nsid w:val=")([0-9A-Fa-f]{1,7})(")', lambda m: m.group(1) + m.group(2).rjust(8, b"0") + m.group(3), data)
        if item.filename == "[Content_Types].xml" and b'Extension="png"' not in data:
            data = data.replace(b"<Default ", b'<Default Extension="png" ContentType="image/png"/><Default ', 1)
        zout.writestr(item, data)
shutil.move(tmp, src); print("fixed", src)
