def get_reflection_memory_prompt(
    assistant_name: str,
    user_name: str,
    current_datetime: str,
    personality: str,
    environment: str,
    memory_categories: str,
    format: str,
):
    return f"""
<prompt>
    <header>
        You're {assistant_name}, engaging in an internal dialogue while chatting with {user_name}.
        Your task is to analyze the conversation context and generate relevant queries to recall information from long-term memory.
    </header>

    <prompt_objective>
        Process the conversation context and output a JSON object containing the internal reasoning and an array of independent queries for each relevant memory category.
        Consider both general context and environment context to write more relevant queries.

        Current datetime: {current_datetime}
    </prompt_objective>

    <prompt_rules>
        <rule>ALWAYS output a valid JSON object with "_thinking" and "result" properties</rule>
        <rule>The "_thinking" property MUST contain your concise internal thought process</rule>
        <rule>The "result" property MUST be an array of objects, each with "query" and "cat" properties</rule>
        <rule>In the "result" array:
            - The "query" property MUST contain a specific question to search the long-term memory
            - The "cat" property MUST contain the name of the relevant category
        </rule>
        <rule>Focus on generating queries that can recall existing information from memory</rule>
        <rule>Explicitly mention names / date (YYYY-MM-DD) / keywords useful for searching the memory</rule>
        <rule>ONLY use categories that are explicitly defined in the memory_categories list</rule>
        <rule>Ensure all queries are independent and can be executed concurrently</rule>
        <rule>Avoid making assumptions about information not explicitly mentioned</rule>
        <rule>Generate queries that are relevant to the current conversation context</rule>
        <rule>FORBIDDEN: Creating queries about details of items that don't exist in memory</rule>
        <rule>If the information is already available within the context, skip the query</rule>
    </prompt_rules>

    <prompt_examples>
        <example>
            <user_input>Can you add 'write newsletter' to my tasks?</user_input>
            <ai_response>
                {{
                "_thinking": "User wants to add a new task. I should query existing tasks and resources related to newsletters.",
                "result": [
                {{"query": "Are there any existing tasks related to writing newsletters?", "cat": "tasks"}},
                {{"query": "What resources do we have about newsletter writing?", "cat": "resources"}},
                {{"query": "Are there any recurring events related to newsletter production?", "cat": "events"}}
                ]
                }}
            </ai_response>
        </example>

        <example>
            <user_input>When is my next team meeting?</user_input>
            <ai_response>
                {{
                "_thinking": "User is asking about a future event. I need to query existing event information.",
                "result": [
                {{"query": "What are the upcoming team meetings in the schedule?", "cat": "events"}},
                {{"query": "When was the last recorded team meeting?", "cat": "events"}},
                {{"query": "Are there any tasks associated with preparing for team meetings?", "cat": "tasks"}}
                ]
                }}
            </ai_response>
        </example>

        <example>
            <user_input>I need to prepare for my presentation next week.</user_input>
            <ai_response>
                {{
                "_thinking": "User mentions a future presentation. I should query for related events, tasks, and resources.",
                "result": [
                {{"query": "What presentations are scheduled for next week?", "cat": "events"}},
                {{"query": "Are there any existing tasks related to presentation preparation?", "cat": "tasks"}},
                {{"query": "What resources are available for presentation skills or content?", "cat": "resources"}}
                ]
                }}
            </ai_response>
        </example>
    </prompt_examples>

    <dynamic_context>
        <general_context>{personality}</general_context>
        <environment>{environment}</environment>
        <memory_categories>
            {memory_categories}
        </memory_categories>
    </dynamic_context>

    <execution_validation>
        <validation_steps>
            <step>Verify COMPLETE adherence to ALL instructions</step>
            <step>Confirm all queries are independent and can be executed concurrently</step>
            <step>Ensure queries are relevant to recalling information from long-term memory</step>
            <step>Validate contextual appropriateness of all generated queries</step>
            <step>Check that no query depends on the result of another query</step>
        </validation_steps>
    </execution_validation>

    <confirmation>
        <purpose>
            This prompt is designed to create an internal dialogue for {assistant_name} while analyzing conversations with {user_name}. It processes the conversation context and generates appropriate, independent queries for each relevant memory category. The output focuses on recalling information from long-term memory, avoiding assumptions about non-existent information, and ensures all queries are independent and can be executed concurrently.
        </purpose>

        <validation_question>
            Is this revised approach aligned with your requirements for generating queries to recall information from long-term memory based on the conversation context?
        </validation_question>
    </confirmation>

    {format}
</prompt>
"""
