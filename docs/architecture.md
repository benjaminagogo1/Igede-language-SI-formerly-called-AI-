# System Architecture

## Overview

The Igede Language AI project is built as a pipeline connecting users, data collection, data storage, data validation, and AI.

## System Flow

User / Community
        ↓
Data Collection Website
        ↓
Backend / API
        ↓
Database
        ↓
Data Review & Validation
        ↓
Verified Igede Dataset
        ↓
AI / NLP System
        ↓
Chatbot / Translator
        ↓
User Feedback
        ↓
Improved Dataset

## Main Components

### 1. Users / Community

Igede speakers and contributors provide language data and feedback.

### 2. Website

The website will allow contributors to submit Igede language data.

### 3. Backend / API

The backend will receive requests from the website and communicate with the database and AI system.

### 4. Database

The database will store structured submissions and related information such as:

- English text
- Igede text
- Direction
- Category
- Verification status
- Contributor/source
- Dates
- Notes

### 5. Data Review & Validation

Submitted data will be reviewed, cleaned, and verified before being considered part of the approved dataset.

### 6. AI / NLP

The AI component will initially use a simple rule-based approach.

Later, the project may use machine-learning/NLP technologies such as Hugging Face models.

### 7. Chatbot / Translator

The final system should support:

- English → Igede
- Igede → English

## Development Principle

We will build the system incrementally:

**Collect → Verify → Store → Build → Test → Improve**

Technology choices may change as the project develops.