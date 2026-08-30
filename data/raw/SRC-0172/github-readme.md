# PDF to JPGs Converter

A Python script that converts PDF files to JPG images with parallel processing support. Each PDF is processed in parallel, and pages are saved as separate JPG files in organized folders.

## Features

- **Parallel Processing**: Process multiple PDF files simultaneously for faster conversion
- **High Quality Output**: 300 DPI conversion with 95% JPEG quality
- **Organized Output**: Each PDF gets its own folder in the outputs directory
- **Python 3.14 Support**: Uses the latest Python version with improved performance
- **Comprehensive Logging**: Detailed logs for monitoring conversion progress
- **Error Handling**: Robust error handling with detailed error messages
- **Command Line Interface**: Flexible CLI with various options

## Requirements

- Python 3.14
- uv package manager
- poppler-utils (for PDF processing)

## Installation

### 1. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install poppler-utils

**macOS (using Homebrew):**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases/) and add to PATH.

## Usage

### Quick Start

1. Place your PDF files in the `inputs/` directory
2. Run the conversion script:

```bash
./run.sh
```

### Advanced Usage

You can also run the Python script directly with various options using `uv run`:

```bash
# Basic usage
uv run python pdf_to_jpg.py

# Specify custom input and output directories
uv run python pdf_to_jpg.py --input-dir /path/to/pdfs --output-dir /path/to/output

# Use specific number of parallel workers
uv run python pdf_to_jpg.py --workers 4

# Enable verbose logging
uv run python pdf_to_jpg.py --verbose

# Show help
uv run python pdf_to_jpg.py --help
```

### Command Line Options

- `--input-dir`, `-i`: Input directory containing PDF files (default: `inputs`)
- `--output-dir`, `-o`: Output directory for JPG files (default: `outputs`)
- `--workers`, `-w`: Number of parallel workers (default: auto)
- `--verbose`, `-v`: Enable verbose logging

## Project Structure

```
pdf-to-jpgs/
├── inputs/                 # Place your PDF files here
├── outputs/                # Converted JPG files will be saved here
│   └── [pdf_name]/         # Each PDF gets its own folder
│       ├── page_001.jpg    # Individual pages as JPG files
│       ├── page_002.jpg
│       └── ...
├── pdf_to_jpg.py          # Main conversion script
├── run.sh                 # Easy execution script
├── pyproject.toml         # Project configuration
├── pdf_conversion.log     # Conversion log file
└── README.md              # This file
```

## Output Format

- Each PDF file is converted to a folder named after the PDF file
- Pages are numbered as `page_001.jpg`, `page_002.jpg`, etc.
- Images are saved in high quality (300 DPI, 95% JPEG quality)

## Example

If you have a PDF file named `document.pdf` in the `inputs/` folder:

```
inputs/
└── document.pdf

# After conversion:
outputs/
└── document/
    ├── page_001.jpg
    ├── page_002.jpg
    └── page_003.jpg
```

## Logging

The script creates detailed logs in `pdf_conversion.log` including:
- Conversion progress
- Error messages
- Summary statistics
- Processing times

## Performance

- Uses Python 3.14's improved threading performance
- Parallel processing for multiple PDF files
- Optimized image compression
- Memory-efficient processing

## Troubleshooting

### Common Issues

1. **"pdf2image package is not installed"**
   - Run: `uv pip install pdf2image`

2. **"PDFInfo not installed"**
   - Install poppler-utils (see Installation section)

3. **"No PDF files found"**
   - Ensure PDF files are in the `inputs/` directory
   - Check file extensions are `.pdf` or `.PDF`

4. **Permission errors**
   - Ensure the script has write permissions to the output directory

### Getting Help

Check the log file `pdf_conversion.log` for detailed error information.

## Development

### Setting up development environment

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black pdf_to_jpg.py

# Lint code
flake8 pdf_to_jpg.py
```

## License

This project is open source and available under the MIT License.
