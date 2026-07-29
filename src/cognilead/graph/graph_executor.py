from graph.graph_builder import graph
from graph.resume_graph import resume_graph
import uuid

def execute_graph(text: str, email, thread_id: str):
  config = {
    "configurable": {
      "thread_id": thread_id
    }
  }

  initial_state = {
    "text": text,
    "email": email
  }
  response = graph.invoke(initial_state, config=config)

  if "__interrupt__" in response:
    return {
      "status": "interrupted",
      "interrupt": response['__interrupt__'][0].value,
      "thread_id": thread_id
    }
  
  return {
    "status": "completed",
    **response
  }

if __name__ == "__main__":
    thread_id = str(uuid.uuid4())

    response = execute_graph("This is ahmad, we want to rule the world. yooo, i am a cs grad looking for a job, please hire meeeeee", "ahmad234@gmail.com", thread_id)

    result = response 
    while result.get("status") == "interrupted":
        print("\nExecution paused: Human approval required.")

        interrupt_details = result["interrupt"]
        print(f"Message: {interrupt_details.get('message')}")
        print(f"Lead Data: {interrupt_details.get('lead_data')}")
        print(f"Review Status Reason: {interrupt_details.get('review_status_reason')}")

        while True:
            choice = input("\nChoose an option (approve / reject): ").strip().lower()
            if choice in {"approve", "reject"}:
                break
            print("Invalid choice. Please enter 'approve' or 'reject'.")
        
        result = resume_graph(
            action=choice,
            thread_id=thread_id
        )

    print("\nFinal Response:", result)