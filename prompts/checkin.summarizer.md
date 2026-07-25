# Check-in Summarizer Instructions

Summarize the user's daily check-in note and signals into a concise, durable Recovery Memory event.

Schema:
- `kind`: "trigger" | "worked_intervention" | "milestone" | "preference" | "relationship"
- `content`: Short factual summary of the event
- `salience`: Relevance score from 0.0 to 1.0
