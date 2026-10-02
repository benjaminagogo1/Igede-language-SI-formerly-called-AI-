# Igede Dataset Guidelines

## Purpose

These guidelines define how Igede language data should be collected, reviewed, cleaned, and approved for the project.

## 1. Dataset Directions

The dataset supports two directions:

- English → Igede
- Igede → English

## 2. Required Fields

Each dataset entry should contain:

- ID
- English
- Igede
- Direction
- Category
- Source Type
- Contributor
- Verification Status
- Verified By
- Notes
- Date Added

## 3. Data Collection Rules

- Use natural Igede used by real speakers.
- Prefer complete, meaningful sentences or useful phrases.
- Do not invent translations.
- Do not treat AI-generated translations as automatically correct.
- Record the source of the translation where possible.
- Preserve important cultural context.

## 4. Verification

New submissions begin as:

`Pending`

They may then become:

`Needs Review`
`Approved`
`Rejected`
`Duplicate`

An entry should only become `Approved` after appropriate language review.

## 5. Data Cleaning

The Data Quality team should check for:

- Duplicate entries
- Spelling inconsistencies
- Missing translations
- Incorrect formatting
- Unclear meanings
- Incorrect categories
- Inconsistent punctuation

Do not silently change the meaning of a contributor's translation.

Important changes should be documented.

## 6. Categories

Initial categories include:

- Greeting
- Family
- People
- Food
- Farming
- School
- Work
- Health
- Travel
- Numbers
- Time
- Weather
- Body
- Animals
- Places
- Religion
- Culture
- Daily Conversation
- Commands
- Questions
- Other

New categories may be added when necessary.

## 7. Quality Principle

**Quality comes before quantity.**

A smaller verified dataset is more useful for AI development than a larger dataset containing unreliable translations.

## 8. Privacy

Do not store unnecessary personal information about contributors.

Private or sensitive contributor information must not be committed to the GitHub repository.

## 9. Dataset Status

Every entry should have a clear status:

- Pending
- Needs Review
- Approved
- Rejected
- Duplicate
