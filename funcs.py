from pdfminer.pdfpage import PDFPage
from pytesseract import Output

import pdf2image
import PyPDF2
import pytesseract


def get_pdf_searchable_pages(fname):
    searchable_pages = []
    non_searchable_pages = []
    page_num = -1
    with open(fname, 'rb') as infile:
        for page in PDFPage.get_pages(infile):
            page_num += 1
            if 'Font' in page.resources.keys():
                searchable_pages.append(page_num)
            else:
                non_searchable_pages.append(page_num)
    return searchable_pages, non_searchable_pages


def init_tesseract(tes_path=r'C:\Program Files\Tesseract-OCR\tesseract'):
    pytesseract.pytesseract.tesseract_cmd = tes_path


def get_bytes_from_scan_page(filename, page_numbers, lang):
    # images = pdf2image.convert_from_path(filename) # only for linux systems using
    images = pdf2image.convert_from_path(
        filename, poppler_path=r'C:\Program Files\poppler-0.68.0\bin')  # only for windows system using
    for p in page_numbers:
        pil_im = images[p]

        ocr_dict = pytesseract.image_to_data(
            pil_im, output_type=Output.DICT, lang=lang)

        text = " ".join(ocr_dict['text'])
        yield text


def get_from_nosearchable(filename, page_numbers, lang):
    data = []
    if page_numbers:
        init_tesseract()  # only for windows system using
        for text in get_bytes_from_scan_page(filename, page_numbers, lang):
            data.append(text)
    return data


def get_from_searchable(filename, page_numbers):
    data = []
    if page_numbers:
        reader = PyPDF2.PdfReader(filename)
        for p in page_numbers:
            page = reader.pages[p]
            extracted = page.extract_text()
            data.append(extracted)
    return data


def prettify_text(text):
    text_splines = text.splitlines()
    text_stspaces = map(lambda el: el.strip(), text_splines)
    text_sspaces = tuple(filter(lambda el: el != '', text_stspaces))
    joined = ' '.join(text_sspaces).lower()
    return joined


def extracter_pdf(src, lang='nor'):
    text_pages, scan_pages = get_pdf_searchable_pages(src)
    text_ext = get_from_searchable(src, text_pages)
    scan_ext = get_from_nosearchable(src, scan_pages, lang)
    full_text = text_ext + scan_ext
    joined = ' '.join(full_text)
    formated = prettify_text(joined)
    return formated


if __name__ == '__main__':
    file = "png2pdf.pdf"
    extracted = extracter_pdf(file)
    print(extracted)
