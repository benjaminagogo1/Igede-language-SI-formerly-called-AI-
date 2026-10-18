# Igede Language AI Dataset — Database Schema

## 1. Purpose

This document describes the initial relational database structure for collecting, reviewing, verifying and preparing Igede language data for AI development.

The database supports the project's two translation directions:

- English → Igede
- Igede → English

The initial dataset target is 1,000 or more verified sentence pairs.

## 2. Database technology

**Proposed database:** PostgreSQL

PostgreSQL provides relational integrity, primary keys, foreign keys, constraints, indexing and transaction support.

The schema is an initial proposal and should be reviewed against the project's existing infrastructure before implementation.

## 3. Database tables

### 3.1 `actors`

Stores internal identifiers and roles for people who interact with the dataset.

Fields:
- `actor_id`: Unique identifier and primary key.
- `role`: Contributor, reviewer or administrator.

Personal information and account credentials should be managed separately by the project's controlled application environment.

### 3.2 `sentence_pairs`

Stores the core bilingual dataset.

Fields:
- `pair_id`: Unique sentence-pair identifier.
- `english_text`: English source sentence.
- `igede_text`: Corresponding Igede sentence.
- `category`: Subject or usage category.
- `verification_status`: Current data status.
- `submitted_by`: Reference to the submitting actor.
- `created_at`: Record creation timestamp.
- `updated_at`: Last modification timestamp.

Both language texts are required. Empty or whitespace-only sentences and categories are rejected by database constraints.

### 3.3 `review_records`

Stores the history of review decisions.

Fields:
- `review_id`: Unique review identifier.
- `pair_id`: Sentence pair being reviewed.
- `reviewer_id`: Actor who performed the review.
- `decision`: Review decision.
- `comments`: Optional feedback or correction notes.
- `reviewed_at`: Review timestamp.

Keeping review records separate allows multiple decisions to be recorded for the same sentence pair.

## 4. Relationships

- One actor may submit multiple sentence pairs.
- One sentence pair may have multiple review records.
- One reviewer may create multiple review records.
- Foreign keys prevent review records from referencing nonexistent sentence pairs or actors.

## 5. Verification workflow

The proposed statuses are:

- `pending`: Submitted and awaiting review.
- `needs_revision`: Requires correction or clarification.
- `verified`: Linguistically reviewed and accepted.
- `approved`: Accepted for inclusion in an approved dataset release.
- `rejected`: Not accepted for use.

Verification and approval are distinct. A linguistically verified sentence pair should not automatically be treated as approved for a training dataset.

Only authorized reviewers and administrators should be allowed to make verification and approval decisions. The application must enforce these permissions.

Every review decision should record the reviewer, decision, timestamp and any relevant comments.

## 6. Translation direction

Each record stores both the English and Igede versions.

The dataset preparation process can generate:
- English input with Igede output.
- Igede input with English output.

Direction labels can be added during export, avoiding unnecessary duplication in the source database.

## 7. Data quality and privacy

Before a sentence pair is approved for AI training, it should pass the project's collection, review, cleaning, verification, approval and dataset-preparation process.

Quality checks should consider:
- Correctness of the Igede translation.
- Accuracy of the English equivalent.
- Spelling and consistency.
- Completeness and meaningfulness.
- Duplicate or near-duplicate sentence pairs.
- Appropriate categorization.
- Permission to use the data for its intended purpose.

Raw contributor submissions and personal information must not be committed to the repository. The working dataset should remain in the project's controlled database or data workspace.

Only approved sample data and appropriate documentation should be committed.

## 8. Implementation considerations

The SQL schema defines the initial tables, relationships, constraints and indexes. Additional implementation work is needed to enforce role-based permissions, synchronize review decisions with the current sentence-pair status, maintain modification timestamps and test the workflow.

The schema should be applied to a clean PostgreSQL database and tested before integration.

## 9. Future improvements

Possible future extensions include:
- Audio recordings and pronunciation data.
- Igede dialect and regional variation support.
- Source citations and collection provenance.
- Revision history for modified sentence pairs.
- Dataset versioning and export manifests.
- Automated duplicate detection and linguistic quality checks.

## 10. Acceptance criteria

The initial database design is ready for review when:
1. All three tables and their fields are documented.
2. Primary keys and foreign-key relationships are defined.
3. Invalid statuses and empty text fields are rejected.
4. Verification decisions and reviewer references can be recorded.
5. English–Igede sentence pairs support both translation directions.
6. Privacy and approval requirements are documented.
7. The SQL runs successfully against a clean PostgreSQL database.
8. Database constraints and key relationships are covered by tests.