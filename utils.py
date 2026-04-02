import fitz  # PyMuPDF — reads PDF files


def extract_text_from_pdf(uploaded_file):
    """
    Reads all the text from a PDF file.

    Think of this like a person flipping through each page of a document
    and typing out everything written on it.
    """
    try:
        uploaded_file.seek(0)  # Rewind to the start (like rewinding a tape)
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""
        for page in doc:
            text += page.get_text()

        doc.close()  # Good practice: close the file after we're done

        # Some PDFs are scanned images — PyMuPDF can't read those as text
        if not text.strip():
            return None, "empty"

        return text, "text"

    except Exception as e:
        # If something goes wrong (corrupted PDF, weird format, etc.),
        # we catch the error instead of crashing the whole app
        return None, f"error: {str(e)}"


def extract_bytes_from_image(uploaded_file):
    """
    Reads an image file as raw bytes so Gemini can look at it directly.

    Gemini's vision feature can "see" images — we just need to hand it
    the raw image data (bytes), not the file object itself.
    """
    try:
        uploaded_file.seek(0)  # Rewind to the start
        image_bytes = uploaded_file.read()
        return image_bytes, "image"

    except Exception as e:
        return None, f"error: {str(e)}"


def get_file_content(uploaded_file):
    """
    The main function your app.py calls.

    It looks at what kind of file was uploaded, then calls the right
    helper function above. Returns the content + a label for what type it is.

    Returns:
        content  -> the text (str) or image bytes (bytes), or None if failed
        kind     -> "text", "image", "unsupported", or "error: ..."
    """
    file_type = uploaded_file.type  # e.g. "application/pdf" or "image/jpeg"

    if file_type == "application/pdf":
        return extract_text_from_pdf(uploaded_file)

    elif file_type in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        return extract_bytes_from_image(uploaded_file)

    else:
        # We don't support this file type (e.g. Excel, Word doc, etc.)
        return None, "unsupported"
