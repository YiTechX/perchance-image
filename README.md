<div align="center">

# 🎨 PERCHANCE-IMAGE

**An Advanced, Zero-Config Python Client & CLI for Perchance AI Text-to-Image Generator**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#)
[![Service](https://img.shields.io/badge/engine-perchance.org-orange.svg)](https://perchance.org/ai-text-to-image-generator)
[![Auth](https://img.shields.io/badge/auth-100%25%20Free%20%26%20Zero%20Login-green.svg)](#)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*Generate stunning, high-resolution AI images directly from your terminal or Python scripts without accounts, API keys, or cookies.*

---

</div>

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Installation](#-installation)
- [Command-Line Interface (CLI)](#-command-line-interface-cli)
  - [1. Single-Prompt Generation](#1-single-prompt-generation)
  - [2. Specifying Art Style](#2-specifying-art-style)
  - [3. Choosing Aspect Ratio (Shape)](#3-choosing-aspect-ratio-shape)
  - [4. Negative Prompting](#4-negative-prompting)
  - [5. Batch Generation](#5-batch-generation)
  - [6. Interactive Terminal Session](#6-interactive-terminal-session)
  - [7. Listing Available Styles](#7-listing-available-styles)
- [Python SDK Reference](#-python-sdk-reference)
  - [Basic Text-to-Image](#basic-text-to-image)
  - [Custom Resolution & Style](#custom-resolution--style)
  - [Context Manager (Session Reuse)](#context-manager-session-reuse)
- [Supported Art Styles](#-supported-art-styles)
- [Disclaimer](#-disclaimer)

---

## 🌟 Overview

**`perchance-image`** is an unofficial, production-grade Python client and CLI engineered to interface with [Perchance AI Text-to-Image Generator](https://perchance.org/ai-text-to-image-generator).

Unlike most AI services that require paid API keys, complex OAuth flows, or expiring session cookies, Perchance provides unlimited, high-quality image generation for free. `perchance-image` wraps this engine into a clean Python SDK and a rich terminal interface with automatic Cloudflare Turnstile evasion and zero configuration.

---

## ✨ Key Features

- **⚡ 100% Free & Unlimited**: No API keys, no subscription, and no session cookies required.
- **🛡️ Cloudflare Bot Evasion**: Automated Turnstile bypass powered by DrissionPage.
- **🎨 79+ Art Styles**: Full support for all Perchance art styles (Cinematic, Studio Ghibli, 3D Disney, Anime, Oil Painting, Cyberpunk, etc.).
- **📐 Flexible Aspect Ratios**: Choose between Square (1:1 / 768x768), Portrait (9:16 / 512x768), or Landscape (16:9 / 768x512).
- **🚫 Negative Prompt Support**: Easily filter out undesired features or artifacts.
- **💻 Rich Interactive CLI**: Terminal interface with progress spinners, colorized outputs, style tables, and auto-open viewer support.
- **🔁 Session Warmup & Reuse**: Keeps browser context alive across prompts for ultra-fast repeated generations.

---

## 📦 Installation

### Prerequisites
- Python **3.10** or higher
- Google Chrome or Microsoft Edge installed on your system

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Command-Line Interface (CLI)

The CLI tool is located at [`cli.py`](file:///c:/Users/YİĞİT/Desktop/Yiğit/perchance-image/cli.py).

### 1. Single-Prompt Generation
```bash
python cli.py "A futuristic flying vehicle navigating glowing neon city streets" --open
```

### 2. Specifying Art Style
```bash
python cli.py "A brave cybernetic samurai" --style "Cinematic" --open
python cli.py "Cozy ramen shop in autumn rain" --style "Studio Ghibli" --open
```

### 3. Choosing Aspect Ratio (Shape)
Supports `square` (1:1), `portrait` (9:16), or `landscape` (16:9):
```bash
python cli.py "Breathtaking mountain valley sunset" --shape landscape --open
python cli.py "Elegant fantasy queen portrait" --shape portrait --open
```

### 4. Negative Prompting
```bash
python cli.py "A cute golden retriever puppy" --negative "blurry, low quality, distorted paws" --open
```

### 5. Batch Generation
Generate multiple variations in a single run:
```bash
python cli.py "Mystical dragon perched atop castle ruins" --count 2 --open
```

### 6. Interactive Terminal Session
Run without arguments to enter an interactive session:
```bash
python cli.py
```
Inside the interactive session:
- Enter any prompt to generate immediately.
- Type `style: Anime` to lock the active style.
- Type `shape: landscape` to switch aspect ratio.
- Type `styles` to view the list of 79+ available art styles.
- Type `exit` or `q` to quit.

### 7. Listing Available Styles
```bash
python cli.py --list-styles
```

---

## 🐍 Python SDK Reference

### Basic Text-to-Image
```python
from perchance_client import PerchanceImageClient

client = PerchanceImageClient(headless=True)
try:
    result = client.generate("A majestic glowing deer in an enchanted forest")
    print(f"Saved to: {result['saved_paths'][0]}")
    print(f"Elapsed: {result['elapsed_time']}s")
finally:
    client.close()
```

### Custom Resolution & Style
```python
from perchance_client import PerchanceImageClient

client = PerchanceImageClient(headless=True)
result = client.generate(
    prompt="Cyberpunk street market in the rain",
    style="Cinematic",
    shape="landscape",          # "square", "portrait", "landscape" (or 16:9, 1:1, 9:16)
    negative_prompt="blurry, watermark, distorted",
    disable_safety_settings=True, # Allow uncensored generation
    output_file="outputs/cyberpunk.png"
)
```

### Context Manager (Session Reuse)
```python
from perchance_client import PerchanceImageClient

with PerchanceImageClient(headless=True) as client:
    # First generation initializes the engine
    res1 = client.generate("A cozy winter cabin", style="Oil Painting")
    
    # Subsequent generations run in the existing tab (faster!)
    res2 = client.generate("A sunny tropical beach", style="Casual Photo")
```

---

## 🎨 Supported Art Styles

Perchance supports 79+ built-in art styles, including:
- **Cinematic**
- **Casual Photo / Professional Photo**
- **Painted Anime / Drawn Anime / Studio Ghibli / Vintage Anime**
- **3D Disney Character / 2D Disney Character / Disney Sketch**
- **Digital Painting / Concept Art / Concept Sketch**
- **Oil Painting (Realism, Old, 70s Pulp)**
- **Cyberpunk / Vaporwave**
- **Pixel Art / Retro Game Art**
- **Comic Book / Vintage Comic / Manga**
- **Watercolor / Painterly**
- *(And 60+ more! Run `python cli.py --list-styles` to see all)*

---

## ⚖️ Disclaimer

This is an unofficial client for educational and personal automation purposes. Please adhere to Perchance's terms of service and acceptable use guidelines.
