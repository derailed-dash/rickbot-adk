# Rickbot-ADK To-Do List

## Current Stage

Migrate `rickbot` Streamlit UI as `streamlit_fe`.

## Next Steps

- [ ] Migrate `rickbot` Streamlit UI as `streamlit_fe`.
- [ ] Perform UI test for all personalities.
- [ ] Remove sample `frontend`.
- [ ] Create new React UI.
- [ ] Implement OAuth login, potentially as sidecar container.
- [ ] Ensure React UI works on mobile.
- [ ] Add persistence of user configuration and conversations using Firestore.
- [ ] Update privacy policy accordingly.
- [ ] Extend Dazbot to have knowledge.

## Completed Steps

- [x] Create unit test for multi-turn Rickbot conversation.
- [x] Migrate `rickbot` functionality to `rickbot_agent` ensuring that session, short-term memory multi-turn conversations are handled by ADK.
- [x] Create `rickbot_agent`.
- [x] Refactor application into the `/src` folder
- [x] Refactor sample agent `app` to `adk_sample_app`
- [x] Add `setup-env.sh` to configure Google environment.
- [x] Test the sample agent remotely
- [x] Deploy the agent with CI/CD
- [x] Deploy with Terraform
- [x] Test the sample agent locally
- [x] Setup CI/CD using Agent-Starter-Kit
- [x] Setup `.env`
- [x] Create initial project with Agent-Starter-Kit
