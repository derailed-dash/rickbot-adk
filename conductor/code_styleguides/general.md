# General Code Style Principles

This document outlines general coding principles that apply across all languages and frameworks used in this project.

## Project Specifics
- **Spelling:** Use English UK spelling in responses and documentation, including code comments.
- **Project Plan:** Check for a `TODO.md` file in the current project to determine the overall plan and status.

## Agent and AI Development
- **Libraries:** Agents should be built using the Google ADK (`google-adk`) and the Google Gen AI (`google-genai`) packages.
- **Deprecated:** AVOID using the `google-generativeai` package.
- **Model Versions:** NEVER try to downgrade a Gemini model (e.g., from `gemini-2.5-flash` to `gemini-1.5-flash`).

## Readability
- Code should be easy to read and understand by humans.
- Avoid overly clever or obscure constructs.

## Consistency
- Follow existing patterns in the codebase.
- Maintain consistent formatting, naming, and structure.

## Simplicity
- Prefer simple solutions over complex ones.
- Break down complex problems into smaller, manageable parts.

## Maintainability
- Write code that is easy to modify and extend.
- Minimize dependencies and coupling.

## Documentation
- Document *why* something is done, not just *what*.
- Keep documentation up-to-date with code changes.
