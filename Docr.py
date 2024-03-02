import ddddocr

def docr_decoder(img_file):
    ocr = ddddocr.DdddOcr()
    with open(img_file, 'rb') as f:
        image = f.read()
        res = ocr.classification(image)
    return res