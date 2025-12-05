#!/usr/bin/env python
import warnings
import json
import os
from script_writer.crew import ScriptWriter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """Automated and ITERATIVE script transformation loop."""

    os.makedirs("output", exist_ok=True)

    initial_script = """
INT. BANK – NIGHT

A group of masked robbers bursts into the bank, guns drawn.  
Civilians scream and duck for cover.

LEAD ROBBER
Everyone on the ground! Now!

SECURITY GUARD
Please… don’t hurt anyone!

The tension is high, the situation extremely dangerous.
"""
    target_genre = "Comedy"
    script_to_rewrite = initial_script
    
    iteration = 0
    max_iterations = 3

    while iteration < max_iterations:
        iteration += 1
        print(f"\n====================\n=== ITERATION {iteration} ===\n====================\n")

        crew = ScriptWriter().crew()

        inputs = {
            "original_script": script_to_rewrite,
            "genre": target_genre,
        }

        supervisor_results = crew.kickoff(inputs=inputs)

        print("\n\n########################")
        print(f"## Crew Execution for Iteration {iteration} Finished!")
        print("########################\n")
        print("Supervisor's decision for this iteration:")
        print(supervisor_results.raw)
        rewritten_script = crew.tasks[0].output.raw
        review_report = crew.tasks[1].output.raw
        
        try:
            supervisor_data = json.loads(supervisor_results.raw)
        except json.JSONDecodeError:
            print("\n⚠️ Supervisor output not valid JSON. Stopping loop.")
            with open(f"output/final_script_iter_{iteration}.md", "w", encoding="utf-8") as f:
                f.write(rewritten_script)
            with open(f"output/final_review_iter_{iteration}.md", "w", encoding="utf-8") as f:
                f.write(review_report)
            break

        if supervisor_data.get("ready", False):
            print("\n🎬 Script is ready for production!")
            with open("output/final_script_approved.md", "w", encoding="utf-8") as f:
                f.write(rewritten_script)
            with open("output/final_review_approved.md", "w", encoding="utf-8") as f:
                f.write(review_report)
            break
        else:
            rewrite_instructions = supervisor_data.get("rewrite_instructions", "")
            script_to_rewrite = f"### PREVIOUS SCRIPT VERSION:\n{rewritten_script}\n\n### INSTRUCTIONS FOR NEXT REWRITE:\n{rewrite_instructions}"
            print("\n🔄 Script not ready. Preparing for next iteration with new instructions.")

    print("\n✅ Iterative process complete. Check the 'output/' folder for all generated files.")


if __name__ == "__main__":
    run()