# Client-side Azure Agents example

Prerequisites:

- Azure Foundry project
  - It should be connected to OpenAI deployment. `gpt-4o` model is used by default
- Application Insights resource (connected to the project)

How to run:

0. Install dependencies with `python -m pip install requirements.txt`
1. Set environment variables:
   - `PROJECT_CONNECTION_STRING` for your project,
   - `OTEL_SERVICE_NAME` to `agent-client` or any other service name you like
   - `AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED` to `true`.
   - If you want to use another model (not `gpt-4o`), set `MODEL`
2. run with `python manage.py runserver 0.0.0.0:8000`
3. open http://localhost:8000
4. pick one of the examples
5. add prompt and submit
6. optionally provide feedback
7. You can check generated telemetry in Azure Foundry UI or in Application Insights resource
