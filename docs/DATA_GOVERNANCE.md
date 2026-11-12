# Data governance

## Default policy

Treat benchmark tasks, repository snapshots, source code, embeddings, issue text, patches, and test artifacts as third-party material until their license and permitted use are verified.

## Before downloading or committing data

Record:

1. Dataset/repository name and canonical source URL.
2. Version, release, commit SHA, and retrieval date.
3. License and terms governing use, modification, and redistribution.
4. Whether the content may contain secrets, personal data, or proprietary code.
5. Whether the artifact is permitted in a public repository or notebook.
6. SHA-256 checksum for immutable source artifacts where possible.

## Repository policy

- Do not commit full benchmark repositories or raw repository archives by default.
- Do not commit private or hidden tests, reference patches, credentials, model weights, or API tokens.
- Store local raw data outside the repository in ignored paths.
- Publish only aggregate outputs, derived annotations, or small examples when licenses permit.
- Explain any filtering, normalization, deduplication, or exclusion.

## Reproducible access

Prefer scripts that download data from canonical sources and verify expected hashes over checking large data files into Git. If access requires Kaggle authentication, document the expected environment variable or CLI setup; never include credentials in code or notebook output.
