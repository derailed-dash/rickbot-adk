# Rickbot-ADK To-Do List

## Next Steps

- [ ] Add lifecycle policy to buckets - delete older data.
- [ ] Add persistence of user configuration and conversations using Firestore.
- [ ] Update privacy policy accordingly.
- [ ] Extend Dazbot to have knowledge.
- [ ] Restrict access to certain personalities.
- [ ] Create new React UI.
- [ ] Implement OAuth login, potentially as sidecar container.
- [ ] Investigate adding other auth methods.
- [ ] Ensure React UI works on mobile.

## Completed Steps

- [x] Refactor logging setup to eliminate duplication.
- [x] Perform project review.
- [x] Readme needs a good cover pic.
- [x] Investigate mapping domains in Terraform.
- [x] Decomm original Rickbot and update repo documentation accordingly.
- [x] Perform OAuth App Verification with Google for Prod.
- [x] Implement a way to test authentication for local dev
- [x] Check Cloud Run instance size and optimise.
- [x] Create `staging` subdomain and map to our Dev Cloud Run service.
- [x] Add `staging` URL to allowed OAuth URIs.
- [x] Update DNS to point to Prod Rickbot Streamlit service
- [x] Configure OAuth Client in Prod project.
- [x] Ensure OAuth secrets are set.
- [x] Update CI/CD to deploy to Prod
- [x] Update dockerfile and deployment to deploy Streamlit_fe
- [x] Remove sample `frontend`.
- [x] Create and execute Streamlit UI test for all personalities.
- [x] Check for any missing logic in the original Rickbot - like rate limiting.
- [x] Configure OAuth Client in Staging project.
- [x] Add OAuth secret to Secret Manager
- [x] Set Prod service to `--allow-unauthenticated` since it will be public facing and use OAuth. Staging service will require IAP.
- [x] Set session information - like user - appropriately.
- [x] Add GenerateContentConfig
- [x] Evaluate frontend UI options, e.g. Streamlit and React.
- [x] Migrate `rickbot` Streamlit UI as `streamlit_fe`.
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
