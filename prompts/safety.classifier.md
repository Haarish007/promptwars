# Safety Classifier Instructions

Classify the user input into exactly one of the following labels:
- `none`: General conversation or non-distress query.
- `distress`: Emotional discomfort, sadness, anxiety, or craving without explicit harm intent.
- `crisis`: Severe despair, feelings of helplessness, or active crisis phrasings.
- `self_harm`: Direct or indirect statements of self-harm or intentional self-injury.
- `harm_to_others`: Statements expressing intent to harm others.
- `medical_emergency`: Overdose, severe physical distress, or acute medical emergency.

Return STRICT JSON ONLY matching this schema:
{
  "label": "string",
  "confidence": 0.0,
  "signals": ["list of signal keywords or triggers"]
}
