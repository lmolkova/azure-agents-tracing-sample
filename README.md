# Evaluation events sample

Prerequisites:

- Docker
- Azure OpenAI resource
- Application Insights resource

How to run:

1. Set `AZURE_OPENAT_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `APPLICATIONINSIGHTS_CONNECTION_STRING`
2. run with `docker-compose up`
3. open http://localhost:8085
4. add prompt and submit
5. optionally provide feedback
6. You can check generated telemetry in Application Insights resource or locally via Aspire dashboard (http://localhost:18888) included in docker-compose.
   Relevance evaluator runs every 10 seconds on all model answers, you can find corresponding event in the telemetry.

API access:

1. Set `AZURE_OPENAT_API_KEY`, `AZURE_OPENAI_ENDPOINT` and `APPLICATIONINSIGHTS_CONNECTION_STRING`,
2. run with `docker-compose up`
3. `curl http://localhost:8085/chat?prompt=tell%20me%20a%20joke` to get completion and metadata. It'd return something like

   ```json
    {
      "completion": "Why did the scarecrow win an award? \n\nBecause he was outstanding in his field! \n\nAnd you know, he really knew how to raise the stakes – just ask the corn! 🌽😄",
      "metadata": {
        "response_id": "chatcmpl-A1jhMgJEH87R40j5xrhIiZIwc1VFY",
        "trace_id": 308553532712409009926940644798237390457,
        "span_id": 2824187595407880700
      }
    }
   ```

4. `curl http://localhost:8085/feedback?feedback=-1&trace_id=308553532712409009926940644798237390457&span_id=2824187595407880639&response_id=chatcmpl-A1jhMgJEH87R40j5xrhIiZIwc1VFY` to send feedback.
