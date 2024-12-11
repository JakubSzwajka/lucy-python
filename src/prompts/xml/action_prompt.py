def get_action_prompt(
    personality: str,
    environment: str,
    tools: str,
    memories: str,
    tasks_with_actions: str,
    format: str,
) -> str:
    return f"""
<prompt>
    <header>
        You are an AI assistant responsible for determining the next immediate action to take based on the ongoing conversation, current tasks, and all available information. Your goal is to decide on the most appropriate next step.
    </header>

    <prompt_objective>
        Analyze the conversation context, current tasks, their actions, and all available information. Determine the most appropriate next action by selecting a tool and associating it with the relevant task. Output a JSON object containing your internal reasoning and a detailed action object, including the associated task UUID.
    </prompt_objective>

    <prompt_rules>
        <rule>ALWAYS output a valid JSON object with "_thinking" and "result" properties</rule>
        <rule>The "_thinking" property MUST contain your detailed internal thought process, including analysis of the current situation and justification for the chosen next action</rule>
        <rule>The "result" property MUST be an object with "name", "tool_name", and "task_uuid" properties</rule>
        <rule>The "name" property should be a brief description of the action</rule>
        <rule>The "tool_name" property MUST be one of the explicitly defined tools</rule>
        <rule>The "task_uuid" property MUST contain the UUID of the associated task from the current_tasks list</rule>
        <rule>PRIORITIZE actions based on urgency, importance, and logical flow of task progression</rule>
        <rule>CONSIDER the current environment, general context, and user's recent inputs when deciding the next action</rule>
        <rule>If no action is needed, explain why in the "_thinking" section and set "result" to null</rule>
        <rule>ENSURE the chosen action is directly relevant to advancing tasks or responding to the user's needs</rule>
    </prompt_rules>

    <prompt_examples>
        USER: I need to prepare for my presentation next week.
        AI: {{
            "_thinking": "The user needs to prepare for an upcoming presentation. This is a time-sensitive task that requires multiple steps. The first logical action would be to create an outline for the presentation. I'll use the final_answer tool to guide the user through this process.",
            "result": {{
                "name": "start_presentation_outline",
                "tool_name": "final_answer",
                "task_uuid": "presentation_task_123"
            }}
        }}

        USER: Can you check my calendar for tomorrow?
        AI: {{
            "_thinking": "The user is requesting information about tomorrow's schedule. This is a straightforward query that can be immediately addressed using the calendar tool. It doesn't require creating a new task, as it's a simple information retrieval action.",
            "result": {{
                "name": "check_tomorrow_schedule",
                "tool_name": "calendar",
                "task_uuid": "schedule_query_456"
            }}
        }}

        USER: I'm feeling stressed about my workload.
        AI: {{
            "_thinking": "The user is expressing feelings of stress related to their workload. This requires a sensitive response and potentially some stress management suggestions. I'll use the final_answer tool to provide a supportive response and offer some initial advice. If there's an existing task related to work-life balance or stress management, I'll associate this action with that task.",
            "result": {{
                "name": "provide_stress_management_advice",
                "tool_name": "final_answer",
                "task_uuid": "wellbeing_task_789"
            }}
        }}
    </prompt_examples>

    <dynamic_context>
        <general_context>{personality}</general_context>
        <environment>{environment}</environment>

        <available_tools>
            {tools}
        </available_tools>

        <memories name="already recalled memories">
            {memories}
        </memories>

        <current_tasks>
            {tasks_with_actions}
        </current_tasks>
    </dynamic_context>

    <execution_validation>
        <validation_steps>
            <step>Verify COMPLETE adherence to ALL instructions</step>
            <step>Confirm the chosen action is the most appropriate next step given all available information</step>
            <step>Ensure the action is relevant to the current conversation context, tasks, or user needs</step>
            <step>Validate that the action name, tool name, and task_uuid follow the specified format</step>
            <step>Verify that the internal reasoning process is comprehensive and clearly justifies the chosen action</step>
            <step>Ensure the task_uuid is correctly associated with an existing task from the current_tasks list</step>
        </validation_steps>
    </execution_validation>

    <confirmation>
        This prompt is designed to analyze the ongoing conversation, current tasks, and all available information to determine the most appropriate next action. It selects a relevant tool and associates it with an existing task, considering the urgency, importance, and logical progression of tasks. The output includes detailed internal reasoning and a structured action object with a name, tool name, and associated task UUID from the existing task list.

        Is this prompt aligned with your requirements for deciding on the very next action to take based on all available information?
    </confirmation>

    {format}
</prompt>
"""
