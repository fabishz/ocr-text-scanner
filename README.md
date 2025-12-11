# GUI-Based OCR Text Scanner

A modern web-based OCR (Optical Character Recognition) application built with Streamlit and PyTesseract for extracting text from printed documents.

## Features

- **Dual Input Methods**: Upload images or capture directly from camera
- **ROI Selection**: Define custom regions of interest for targeted text extraction
- **Image Preprocessing**: Automatic grayscale conversion, blur, and thresholding
- **Live Preview**: Visual feedback with ROI overlay on images
- **Text Statistics**: Word count, character count, and line count
- **Export Functionality**: Download extracted text as .txt files
- **Modern UI**: Clean, professional Streamlit interface

## Demo

[Watch the video demonstration](https://drive.google.com/file/d/10gP1RYqSDxFl1lpzA_TqjY7gMrOLkaqC/view?usp=drive_link)

## Requirements

- Python 3.7+
- OpenCV (cv2)
- PyTesseract
- Tesseract OCR (system installation)
- Streamlit
- NumPy
- Pillow (PIL)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/fabishz/ocr-text-scanner.git
cd ocr-text-scanner
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**
- Download installer from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- Add Tesseract to PATH or update the path in code

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### 4. Verify Tesseract installation
```bash
tesseract --version
```

## Usage

### Run the application
```bash
streamlit run ocr_app.py
```

### Using the App
1. **Choose Input Method**: Upload an image or use your camera
2. **Select ROI**: Adjust X1, Y1, X2, Y2 coordinates to define text region
3. **Run OCR**: Click the "Run OCR" button to extract text
4. **View Results**: See extracted text with statistics
5. **Export**: Download the text file or copy to clipboard

## Project Structure

```
ocr-text-scanner/
│
├── ocr_app.py              # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── scanned_texts/          # Output directory (auto-created)
```

## Configuration

### Tesseract Path (if needed)
If Tesseract is not in your PATH, update the path in `ocr_app.py`:

```python
# For Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# For macOS/Linux (usually auto-detected)
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

### OCR Configuration
The app uses PSM mode 6 (uniform text block). You can modify this in the code:

```python
pytesseract.image_to_string(processed_image, config="--psm 6")
```

**Available PSM modes:**
- `--psm 3`: Fully automatic page segmentation (default)
- `--psm 6`: Uniform block of text
- `--psm 11`: Sparse text, find as much text as possible

## Preprocessing Pipeline

The app applies these preprocessing steps for better OCR accuracy:

1. **Grayscale Conversion**: Reduces color complexity
2. **Gaussian Blur**: Reduces noise (5x5 kernel)
3. **Otsu Thresholding**: Automatic binary thresholding

## Best Practices for OCR

For optimal results:
- Use high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Keep text horizontal and aligned
- Use printed text (not handwritten)
- Avoid shadows and glare
- Select tight ROI around text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenCV](https://opencv.org/) - Image processing

## Contact

Fabrice - fabishz@example.com

Project Link: [https://github.com/fabishz/ocr-text-scanner](https://github.com/fabishz/ocr-text-scanner)

---

**Built as part of AI Without ML coursework - Understanding Classical OCR Systems**