# PLN Billing System

A web-based electricity billing system designed to implement Object-Oriented Programming (OOP) principles.

## Overview

This project provides a billing calculator for 13 different PLN (Perusahaan Listrik Negara) tariff categories. It processes various billing requirements including regular usage, WBP/LWBP (Waktu Beban Puncak / Luar Waktu Beban Puncak) pricing structures, and kVArh penalties for specific customer segments.

The core application logic is built with Python and Flask, utilizing OOP concepts such as Abstraction and Polymorphism to handle the distinct calculation rules across different tariff types. The frontend provides a user interface to input electricity usage data and view detailed billing results.

## Features

- **OOP Architecture**: Implements inheritance, polymorphism, and abstraction to cleanly manage diverse tariff logic.
- **Comprehensive Tariff Support**: Supports billing calculations for multiple PLN customer categories including Household, Business, Industry, Government, and Multipurpose.
- **Advanced Calculations**: Handles multi-tier pricing, WBP/LWBP variations, and kVArh penalty logic.
- **Web Interface**: HTML/JS frontend for data entry and calculation visualization.

## Structure

- `app.py`: Main Flask application and routing.
- `models/`: Core OOP business logic and class definitions for customer types.
- `static/`: Frontend assets (CSS and JavaScript).
- `templates/`: HTML templates.

## Setup Instructions

1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open your browser and navigate to `http://127.0.0.1:5000`.
