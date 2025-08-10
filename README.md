<div align="center">
  <img src="https://raw.githubusercontent.com/drona-gyawali/My-Github-Assest/refs/heads/main/dumps/focusTube.png" width="300" />
</div>


# FocusTube Server

FocusTube is a productivity-focused YouTube wrapper that helps users stay focused by minimizing distractions. This repository contains the backend server for FocusTube, built with FastAPI.

## What is FocusTube?

FocusTube provides a simple workflow: users paste a YouTube link, and the server delivers the video content without distractions—no shorts, no reels, no recommendations, and no clutter. The goal is to help you watch only what you intend, boosting productivity and focus.

## Features

- Minimal, distraction-free API for YouTube content
- Paste a YouTube link and get only the main video—no reels, no shorts, no recommendations
- FastAPI-based backend
- Linting and formatting with `black` and `isort`

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
  ```bash
  git clone https://github.com/username/FocusTube.git
  cd FocusTube/server
  ```

2. **Create and activate a virtual environment (optional but recommended):**
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  ```

3. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

### Running the Server

Start the FastAPI server with:

```bash
uvicorn app.config.server:app
```

### Code Quality

- **Format code with [black](https://black.readthedocs.io/en/stable/):**
  ```bash
  black .
  ```
- **Sort imports with [isort](https://pycqa.github.io/isort/):**
  ```bash
  isort .
  ```

## Contributing

Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

## License

[MIT License](LICENSE)

---
