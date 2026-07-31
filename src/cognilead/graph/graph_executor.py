from graph.graph_builder import graph
from graph.resume_graph import resume_graph
import uuid

def execute_graph(lead_text: str, email):
  lead_id = str(uuid.uuid4())
  print("Thread ID: ", lead_id)

  config = {
    "configurable": {
      "thread_id": lead_id
    }
  }

  initial_state = {
    "text": lead_text,
    "email": email,
    "lead_id": lead_id
  }
  response = graph.invoke(initial_state, config=config)

  if "__interrupt__" in response:
    return {
      "status": "interrupted",
      "interrupt": response['__interrupt__'][0].value,
      "thread_id": lead_id
    }
  
  return {
    "status": "completed",
    **response
  }

if __name__ == "__main__":

    result = resume_graph(thread_id="9a52c16e-ec1c-48c0-8e60-cd604d6d2038", action="approve")
    print("Workflow completed successfully.")
    print(f"Response: {result}")

    # response = execute_graph("Hi, I'm the operations manager at Summit Group. We're a small consulting firm, about 12 people, and we're looking for a way to automate how we screen inbound client inquiries.", "ops@summitgroupconsulting.co")

    # result = response 
    # while result.get("status") == "interrupted":
    #     print("\nExecution paused: Human approval required.")

    #     interrupt_details = result["interrupt"]
    #     print(f"Message: {interrupt_details.get('message')}")
    #     print(f"Lead Data: {interrupt_details.get('lead_data')}")
    #     print(f"Review Status Reason: {interrupt_details.get('review_status_reason')}")

    #     while True:
    #         choice = input("\nChoose an option (approve / reject): ").strip().lower()
    #         if choice in {"approve", "reject"}:
    #             break
    #         print("Invalid choice. Please enter 'approve' or 'reject'.")
        
    #     result = resume_graph(
    #         action=choice,
    #         thread_id=result['thread_id']
    #     )

    # print("\nFinal Response:", result)