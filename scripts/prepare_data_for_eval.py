import asyncio
import json
import os
from typing import Callable
from src.kb_service.graph_module import KnowledgeGraphModule
from src.agents.master_agent.agent import create_agent
from google.adk.agents import Agent
from src.core.config import PROJECT_ROOT
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from src.core.logger import logger


# ---- Dummy functions (replace with your real logic or API calls) ---- #
async def baseline_system(graph: KnowledgeGraphModule, question: str) -> str:
    response = graph.query(question, mode="hybrid", **{"top_k": 40})
    return response.response

async def proposed_system(runner: Runner, user_id: str, session_id: str, question: str) -> str:
     # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=f"Combine internal knowledge and internet search. {question}")])
    
    # Run the agent and iterate through events
    events_async = runner.run_async(
        session_id=session_id, user_id=user_id, new_message=content
    )

    event_count = 0
    async for event in events_async:
        event_count += 1
        if event_count % 5 == 0:  # Progress indicator every 5 events
            print(f"  📊 Processing... ({event_count} events)")

        logger.debug(f"Event received: {event}")

        # Check if this is the final response
        if event.is_final_response():
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "parts") and event.content.parts:
                    final_response_text = event.content.parts[0].text
                    break

    return final_response_text

# ---- Main Evaluation Logic with Resume Support ---- #
async def evaluate_systems_with_resume(
    input_file: str,
    output_file: str,
    baseline_fn: Callable[[KnowledgeGraphModule, str], str],
    proposed_fn: Callable[[Agent, str], str]
):
    baseline_graph = KnowledgeGraphModule()
    master_agent, _ = await create_agent()
    session_service = InMemorySessionService()
    session = session_service.create_session(
            app_name="master_agent", user_id="user", session_id="session"
        )
    master_agent_runner = Runner(
            agent=master_agent,
            app_name="master_agent",
            session_service=session_service,
        )

    # Step 1: Load all questions
    with open(input_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # Step 2: Load existing results if available
    results = []
    completed_questions = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
                completed_questions = {item["question"] for item in results}
                print(f"🔁 Resuming from checkpoint. Loaded {len(completed_questions)} completed questions.")
            except Exception:
                print("⚠️ Could not parse existing results file. Starting from scratch.")

    # Step 3: Loop and process remaining questions
    for idx, q in enumerate(questions, start=1):
        question = q["question"]
        expect_answer = q["expect_answer"]

        if question in completed_questions:
            print(f"[{idx}] ✅ Skipped (already done): {question}")
            continue

        print(f"[{idx}] 🔄 Processing: {question}")
        try:
            response_baseline = await baseline_fn(baseline_graph, question)
        except Exception as e:
            response_baseline = f"[ERROR] {str(e)}"

        try:
            response_proposed = await proposed_fn(master_agent_runner, user_id="user", session_id="session", question=question)
        except Exception as e:
            response_proposed = f"[ERROR] {str(e)}"

        result_item = {
            "question": question,
            "expect_answer": expect_answer,
            "response_baseline": response_baseline,
            "response_proposed_system": response_proposed
        }

        results.append(result_item)

        # Step 4: Save progress after each question
        with open(output_file, "w", encoding="utf-8") as fout:
            json.dump(results, fout, indent=2, ensure_ascii=False)

    print(f"\n✅ Evaluation complete. Results saved to: {output_file}")

# ---- Run the script ---- #
if __name__ == "__main__":
    asyncio.run(evaluate_systems_with_resume(
        input_file=f"{PROJECT_ROOT}/eval/questions.json",
        output_file=f"{PROJECT_ROOT}/eval/results.json",
        baseline_fn=baseline_system,
        proposed_fn=proposed_system
    ))
