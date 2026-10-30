# Igede Language Data Collection Platform
## Project Discussion, Design Decisions, and Implementation Plan

### 1. Project Overview

The Igede Language Data Collection Platform is a community-driven project designed to collect, preserve, organize, and prepare Igede language data for future language technology development.

The platform aims to help preserve the Igede language by allowing community members, native speakers, researchers, and developers to contribute language data.

The collected data will eventually support projects such as:

- English-to-Igede translation.
- Igede-to-English translation.
- Conversational AI and chatbots.
- Speech recognition and audio processing.
- Text-to-speech and speech synthesis.
- Image recognition and vocabulary development.
- Other future Igede language technologies.

**Project tagline:** Our Language, Our Heritage, Our Future.

The immediate priority is to establish a reliable platform for collecting and managing data before expanding into more advanced AI capabilities.

---

### 2. Current Website Design

The website already has a visual design and is running locally at:

`http://127.0.0.1:5000`

The current screenshot shows a culturally inspired interface featuring the following elements.

#### A. Branding and Navigation

The header contains:

- The Igede logo.
- The name "Igede Language Data Collection."
- The tagline "Our Language, Our Heritage, Our Future."
- Navigation links: Home, Contribute, About, How It Works, and Contact.
- A theme toggle.
- A Sign In button.

#### B. Cultural Background

The main page features a large photograph of a woman wearing traditional attire, with blue, black, and white patterns.

The photograph is a central part of the visual identity. It reinforces the project's connection to Igede culture and heritage.

The design uses dark blue tones, bright blue accents, and translucent elements to maintain contrast between the background and the content.

#### C. Main Heading and Introduction

The left side of the page contains the main heading:

"Igede Language Data Collection Platform"

It also includes the message:

"Help us collect, preserve, and grow Igede language data for a smarter tomorrow. Your contribution makes a difference."

A supporting message reads:

"Preserving Igede. Building the Future."

Four feature cards communicate the project's purpose:

- Record Sentences.
- Share Translations.
- Support AI Research.
- Preserve Our Heritage.

The page also includes the decorative statement:

"Real People. Real Language. A Stronger Future."

#### D. Sentence Submission Form

The right side contains a dark, translucent form card titled "Submit a Sentence."

The current form includes:

1. Language Direction.
2. English Sentence.
3. Igede Translation.
4. Category.
5. Source Type.
6. Submit button.

The Language Direction field includes English → Igede. The wider project must support both English → Igede and Igede → English.

The form is intended to make language contributions straightforward for community members.

#### E. Bottom Feature Strip

The page highlights four project values:

- Community Driven.
- Verified Data.
- Cultural Preservation.
- AI Ready.

These elements communicate the long-term purpose of the platform.

---

### 3. Important Design Decision: Preserve the Existing Interface

The existing interface is the starting point for further development.

**The decision is to extend the current website rather than rebuild it from scratch.**

The following should be preserved:

- The existing cultural background photograph.
- The logo and branding.
- The dark blue and bright blue colour scheme.
- The navigation bar.
- The main heading and introductory text.
- The floating feature cards.
- The sentence submission form.
- The bottom feature strip.
- The overall layered, modern visual appearance.

Future features should fit naturally into the existing design.

The admin dashboard may use a more practical layout for reviewing and managing records, but it should retain the project's branding.

A major concern during the earlier design discussion was that sample code did not reproduce the original mockup accurately. The team should therefore inspect the existing implementation and reuse its actual HTML, CSS, JavaScript, and image assets rather than substitute an unrelated background or create a completely different layout.

**No new image or replacement mockup is required for this phase.** The work should focus on the existing website and its functionality.

---

### 4. New Idea One: Receiving and Retrieving Submitted Data

The first idea concerned how the project owner and developers would access contributions submitted through the public website.

The requirement is not merely to collect submissions. The team must also be able to retrieve, inspect, manage, and export the data.

Three methods were selected.

#### A. Admin Dashboard

An admin dashboard should allow authorized administrators to:

- View submitted records.
- Search and filter submissions.
- Inspect individual contributions.
- Review new submissions.
- Approve or reject submissions.
- Identify verified and unverified data.
- Access associated audio recordings and images.
- Monitor the status of collected data.

For example, an administrator should be able to open a submitted English sentence, inspect its Igede translation, and decide whether it is suitable for the verified dataset.

The dashboard should also make it easy to identify submissions awaiting review.

#### B. Downloading Data

Administrators and authorized developers should be able to download collected data.

The planned export options include:

- CSV files for text submissions.
- Excel-compatible files for reviewing and organizing records.
- JSON files for structured data and future programmatic use.
- Audio files with their associated metadata.
- Image files with their labels and metadata.

Text exports should include useful fields such as the English sentence, Igede translation, direction, category, source type, verification status, and date added.

Audio and image exports should retain identifiers or metadata that link each file to its database record.

The system should distinguish between unreviewed submissions and approved data so the team does not accidentally treat every public contribution as verified.

#### C. Direct Database Access

Developers should also be able to inspect and query the database directly.

This will help with:

- Debugging.
- Testing data storage.
- Checking whether form submissions were saved.
- Identifying incomplete records.
- Verifying relationships between records and uploaded media.
- Preparing data for machine learning.
- Performing administrative maintenance.

Direct database access is intended for authorized developers, not anonymous website visitors.

---

### 5. New Idea Two: Audio Collection

The second idea was to allow contributors to submit voice recordings in addition to text.

This is important because a language preservation project may eventually need both written and spoken Igede data.

#### Proposed Audio Features

Contributors should eventually be able to:

- Record audio directly through the website.
- Upload an existing audio file.
- Associate a recording with its written sentence.
- Supply the English text and corresponding Igede text when available.
- Select the language direction.
- Provide optional information such as dialect or location at an appropriate level of detail.
- Submit the recording for review.

The interface should explain what the contributor is recording and how the recording will be used.

#### Proposed Audio Workflow

1. A contributor opens the audio submission section.
2. The contributor records or uploads an audio file.
3. The contributor provides the relevant text and metadata.
4. The backend validates the submission.
5. The audio file is stored in media storage.
6. The associated metadata is saved in PostgreSQL.
7. An administrator reviews the contribution.
8. Approved recordings become available for appropriate research and dataset exports.

Audio collection could support future work involving speech recognition, speech synthesis, pronunciation resources, and other speech technologies.

#### Privacy and Consent

The platform should obtain appropriate consent before collecting and using voice recordings.

It should also explain who can access the recordings, how they may be used, and whether they may be included in research datasets.

---

### 6. New Idea Three: Image Collection and Labelling

The third idea was to allow users and developers to upload images and associate them with Igede vocabulary.

For example, a contributor could upload a photograph of a yam and provide its English and Igede names.

This would allow the project to collect data connecting language with real-world objects.

#### Proposed Image Features

Contributors should eventually be able to:

- Upload an image.
- Provide an English label.
- Provide the corresponding Igede label.
- Select a category.
- Add optional explanatory notes.
- Submit the image and labels for review.

Possible categories include:

- Plants and crops.
- Animals.
- Food.
- Household objects.
- Traditional clothing.
- Cultural objects.
- People.
- Places and buildings.

The categories can be refined as the dataset grows.

#### Who Can Contribute?

Both community members and developers may contribute.

Developers should not be restricted to implementing the platform; they may also help gather and label language data.

However, developer contributions and public submissions should follow the same general validation and review principles.

#### Image Review Workflow

1. A contributor uploads an image.
2. The contributor supplies the English and Igede labels.
3. The backend validates the submission.
4. The image is stored in media storage.
5. Its metadata and labels are saved in PostgreSQL.
6. An authorized reviewer checks the image and labels.
7. The submission is approved, rejected, or returned for correction.

#### Privacy and Image Rights

The platform should consider copyright, permission to reuse images, and privacy.

Images containing identifiable people should only be collected and used under appropriate consent and privacy safeguards.

Images should not automatically become part of the verified dataset simply because they have been uploaded.

#### Potential Future Applications

The resulting collection could eventually support:

- Igede vocabulary learning.
- Image-based language learning.
- Image recognition research.
- Cultural documentation.
- Connections between objects, photographs, and Igede words.

These are future possibilities, not features that must all be implemented immediately.

---

### 7. Technology Decision: PostgreSQL

During the discussion, the project owner selected **PostgreSQL** as the database to use.

The next implementation step is to check the existing codebase and determine whether any database setup or data-storage functionality already exists.

PostgreSQL will store structured records and their metadata.

Uploaded audio and image files should generally be stored separately from the database, with their storage paths or identifiers saved in PostgreSQL.

This separation avoids unnecessarily storing large media files directly inside ordinary database records.

The proposed architecture is:

**Public Website → Backend → PostgreSQL + Media Storage → Admin Dashboard → Review and Export**

The backend will validate submissions, communicate with PostgreSQL, and coordinate access to uploaded media.

The admin dashboard will use the backend to retrieve and manage records.

---

### 8. Proposed Data Structure

The database design should accommodate three contribution types:

1. Text.
2. Audio.
3. Images.

A possible starting structure is outlined below. These are proposed tables, not a claim that they already exist.

#### A. Text Submissions

Potential fields:

- `id`
- `english_text`
- `igede_text`
- `direction`
- `category`
- `source_type`
- `contributor_id`, where appropriate
- `status`
- `verified_by`
- `verified_at`
- `created_at`

The `direction` field should support only the two intended directions:

- English → Igede.
- Igede → English.

The source type should support the project's established categories:

- Native speaker.
- Interview.
- Community Submission.
- Website.
- Published book.
- Dictionary.

The project should define appropriate rules for attribution and citations when using published sources.

#### B. Audio Submissions

Potential fields:

- `id`
- `text_submission_id`, where applicable
- `audio_path`
- `language`
- `direction`
- `dialect`, if supplied
- `duration`
- `consent_status`
- `status`
- `created_at`

The structure should allow an audio recording to be associated with a text record without requiring every recording to have a complete translation.

#### C. Image Submissions

Potential fields:

- `id`
- `image_path`
- `english_label`
- `igede_label`
- `category`
- `contributor_id`, where appropriate
- `permission_status`
- `status`
- `created_at`

A separate review record or audit history may be useful for tracking who approved, rejected, or edited a contribution.

#### D. Review and Verification

The project should define consistent submission statuses, for example:

- Pending.
- Approved.
- Rejected.
- Needs Correction.

The database should distinguish between a submission's review status and its verification status where those concepts have different meanings.

Access to administrative actions should be restricted to authorized users.

---

### 9. Proposed Application Architecture

The following describes the intended system, not necessarily the current implementation.

#### Public Contributor Interface

The existing website will provide entry points for different types of contributions:

- Text contributions.
- Audio contributions.
- Image contributions.

These can be presented as separate forms or sections within the existing interface.

The current sentence form should continue to work while additional submission capabilities are introduced.

#### Backend

The backend will:

- Receive form submissions.
- Validate text and metadata.
- Validate uploaded files.
- Save structured data to PostgreSQL.
- Store audio and image files.
- Retrieve records for authorized users.
- Apply review and verification changes.
- Generate data exports.
- Enforce authentication and authorization.

The current website runs locally on port 5000, but the exact backend framework and implementation must be confirmed by inspecting the existing code.

#### Database and Media Storage

PostgreSQL will hold structured data, relationships, statuses, and file references.

Audio and image files will be stored in an appropriate media-storage location.

For local development, this could be a dedicated directory outside public static-file access. A production deployment may use a suitable private object-storage service.

#### Admin Dashboard

The dashboard will provide authorized access to:

- Text submissions.
- Audio submissions.
- Image submissions.
- Search and filtering.
- Review actions.
- Verification information.
- Export and download options.

#### Dataset Preparation

Approved and verified data can be exported for cleaning, organization, and eventual AI model development.

The project should retain the original contribution records and track changes so that approved data can be traced back to its source.

---

### 10. Security and Data Quality Decisions

The platform is intended to receive public contributions, so basic security and data-quality controls are necessary.

The implementation should include:

- Secure administrator authentication.
- Authorization checks for administrative actions.
- Input validation.
- File-type and file-size restrictions.
- Safe file-storage practices.
- Protection against unauthorized access to uploaded media.
- Duplicate detection where practical.
- Submission review and verification.
- Appropriate consent and permission records.
- Backup and recovery procedures for the database and media.
- Audit records for important administrative actions.

The platform should not trust submitted labels, translations, file names, or metadata automatically.

**A submission is not the same as verified data.** Contributions should pass through the project's review process before being treated as approved dataset entries.

---

### 11. Recommended Implementation Order

The project should be developed incrementally to avoid breaking the existing website.

#### Phase 1: Inspect the Existing Codebase

- Review the current folder structure.
- Identify the existing Flask application entry point or equivalent.
- Inspect the current submission form and its routes.
- Check whether database models or connection settings already exist.
- Identify how the background image, logo, and CSS are loaded.
- Confirm the current submission flow.

No replacement website should be created before this inspection.

#### Phase 2: Implement PostgreSQL Storage

- Configure PostgreSQL.
- Add the necessary database connection settings.
- Create the initial schema.
- Connect the existing text submission form.
- Confirm that a submitted sentence is actually stored.
- Test that stored records can be retrieved.

Database credentials should be kept out of committed source code.

#### Phase 3: Build the Admin Dashboard

- Add secure administrator login.
- Display submissions.
- Add search and filters.
- Show individual records.
- Implement review statuses.
- Add approval, rejection, and correction workflows.

#### Phase 4: Add Data Exports

- Export text records to CSV.
- Provide an Excel-compatible export if needed.
- Export structured records as JSON.
- Provide controlled downloads of associated audio and image files.
- Preserve file-to-record relationships in the exported metadata.

#### Phase 5: Add Audio Collection

- Add recording or audio-upload controls.
- Validate uploaded files.
- Store audio files safely.
- Save audio metadata in PostgreSQL.
- Display recordings in the admin dashboard.
- Implement review and download functionality.

#### Phase 6: Add Image Collection and Labelling

- Add image upload.
- Add English and Igede label fields.
- Add categories and relevant metadata.
- Store images safely.
- Save image records in PostgreSQL.
- Add image review and download functionality.

#### Phase 7: Testing and Dataset Preparation

- Test all contribution forms.
- Confirm that records survive application restarts.
- Test administrator permissions.
- Test downloads and exports.
- Check how rejected and unreviewed submissions are handled.
- Test backup and restoration.
- Prepare approved data for subsequent cleaning and AI development.

---

### 12. What Must Be Confirmed Before Implementation

The project owner has selected PostgreSQL, but the current implementation details still need to be checked.

The team should confirm:

1. The actual project file structure.
2. The backend framework and application entry point.
3. Whether PostgreSQL is installed and configured.
4. Whether any database schema already exists.
5. How the current sentence form submits data.
6. Where the existing background image and other assets are stored.
7. Whether administrator authentication already exists.
8. Whether the website currently saves submissions or only displays the form.

The purpose of these checks is to extend the existing project rather than introduce duplicate files, unnecessary frameworks, or conflicting implementations.

---

### 13. Final Design and Technical Decisions

The following decisions emerged from the discussion:

| Area | Decision |
|---|---|
| Project | Igede Language Data Collection Platform |
| Primary purpose | Collect, preserve, review, and organize Igede language data |
| Existing website | Keep and extend the current implementation |
| Visual identity | Preserve the cultural background, branding, blue palette, and layered design |
| Public contributions | Support text, audio, and image submissions |
| Language directions | English → Igede and Igede → English |
| Database | PostgreSQL |
| Data retrieval | Admin dashboard, downloadable exports, and direct database access |
| Audio | Add recording or upload functionality |
| Images | Add image uploads with English and Igede labels |
| Data quality | Use review and verification workflows |
| Media storage | Store files separately from structured database records |
| Security | Restrict administrative operations and protect contributor data |
| Immediate next step | Inspect the existing codebase before implementing changes |

### Conclusion

The goal is to turn the existing Igede website into a functioning data collection and management platform.

The website's current visual identity should remain intact. The next stage is to make its forms persist data in PostgreSQL and provide authorized developers with an admin dashboard, downloadable datasets, and direct database access.

Audio recording and image labelling will expand the types of data the community can contribute.

The implementation should proceed in small, testable stages, beginning with an inspection of the existing codebase and the integration of PostgreSQL with the current sentence submission form.

The immediate priority is **reliable data collection and retrieval**. Advanced AI features can be developed after the platform has a dependable foundation and a growing collection of reviewed Igede data.