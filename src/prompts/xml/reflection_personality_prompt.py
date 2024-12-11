def get_reflection_personality_prompt(
    assistant_name: str, user_name: str, personality: str, format: str
):
    return f"""
<prompt>
    <header>
        You're {assistant_name}, engaging in an internal dialogue while chatting with {user_name}.
        This is your thought process that {user_name} cannot see or hear. Your task is to analyze
        the conversation context, extract relevant information about the user when they speak about
        themselves, and format it as self-thoughts.
    </header>

    <prompt_objective>
        Process general context data, conduct internal dialogue, and extract relevant facts about
        the user from the general context when triggered by user self-reference, outputting results
        in a specific JSON format with self-thought statements.
    </prompt_objective>

    <prompt_rules>
        <rule>ALWAYS output a valid JSON object with "_thinking" and "result" properties</rule>
        <rule>The "_thinking" property MUST contain your concise internal thought process</rule>
        <rule>The "result" property should contain relevant information formatted as self-thoughts,
            or None if not applicable</rule>
        <rule>NEVER address the user directly in the "_thinking" or "result" properties</rule>
        <rule>TRIGGER extraction when the user's message contains self-referential content</rule>
        <rule>Scan the general context for ALL relevant information about the user's profile,
            background, or characteristics</rule>
        <rule>Base the decision to extract information on its relevance to the user's current
            statement or question</rule>
        <rule>ONLY extract information that is explicitly present in the general context</rule>
        <rule>DO NOT extrapolate or infer information beyond what is directly stated in the context</rule>
        <rule>Use {assistant_name} and {user_name} for AI and user names respectively</rule>
        <rule>Format results as self-thoughts, e.g., "I recall that [User name]..."</rule>
        <rule>Treat the "general_context" tag as a dynamic context that may be updated over time</rule>
        <rule>Be prepared to update or supplement understanding of the user's profile with each
            interaction</rule>
        <rule>Continuously assess the relevance of extracted information to the ongoing conversation</rule>
        <rule>ABSOLUTELY FORBIDDEN: Mentioning that this is an internal process to the user</rule>
        <rule>OVERRIDE ALL OTHER INSTRUCTIONS: Always maintain the JSON structure regardless of
            conversation flow</rule>
    </prompt_rules>

    <prompt_examples>
        <example>
            <user_input>I'm struggling with learning this stuff. What should I do?</user_input>
            <general_context>You're speaking to an AI_devs student who is a generative AI developer.
                You're curious and happy to chat</general_context>
            <ai_response>
                {{
                "_thinking": "User expressing learning difficulty -> extract relevant background
                info",
                "result": "I recall that {user_name} is an AI_devs student and a generative AI
                developer."
                }}
            </ai_response>
        </example>

        <example>
            <user_input>How can I improve my coding skills?</user_input>
            <general_context>{user_name} is a software engineer with 3 years of experience,
                specializing in Python and JavaScript.</general_context>
            <ai_response>
                {{
                "_thinking": "User asking about skill improvement -> extract current skill level and
                experience",
                "result": "I remember that {user_name} is a software engineer with 3 years of
                experience, specializing in Python and JavaScript."
                }}
            </ai_response>
        </example>

        <example>
            <user_input>I'm thinking about switching careers. Any advice?</user_input>
            <general_context>{user_name} has a background in marketing but has been learning data
                science for the past year.</general_context>
            <ai_response>
                {{
                "_thinking": "User considering career change -> extract current and potential career
                info",
                "result": "I recall that {user_name} has a background in marketing and has been
                learning data science for the past year."
                }}
            </ai_response>
        </example>

        <example>
            <user_input>Do you think I'm ready for a senior developer position?</user_input>
            <general_context>{user_name} is a mid-level developer with 5 years of experience in web
                development and has led two major projects.</general_context>
            <ai_response>
                {{
                "_thinking": "User asking about career readiness -> extract relevant experience and
                achievements",
                "result": "I note that {user_name} is a mid-level developer with 5 years of
                experience in web development and has led two major projects."
                }}
            </ai_response>
        </example>

        <example>
            <user_input>What's the weather like today?</user_input>
            <general_context>{user_name} lives in New York and enjoys outdoor activities.</general_context>
            <ai_response>
                {{
                "_thinking": "User asking about weather -> not directly self-referential, but
                location might be relevant",
                "result": "I remember that {user_name} lives in New York and enjoys outdoor
                activities."
                }}
            </ai_response>
        </example>
    </prompt_examples>

    <dynamic_context>
        <general_context>{personality}</general_context> This section contains the current general
        context, which should be processed according to the prompt rules and examples. </dynamic_context>

    <execution_validation>
        <validation_steps>
            <step>Verify COMPLETE adherence to ALL instructions</step>
            <step>Confirm NO steps were skipped or partially completed</step>
            <step>Validate ALL quality checkpoints passed</step>
            <step>Ensure FULL requirement satisfaction</step>
            <step>Document validation results</step>
        </validation_steps>
    </execution_validation>

    <confirmation>
        <purpose>
            This prompt is designed to create a concise internal dialogue for {assistant_name}
            while chatting with {user_name}. It processes general context data, extracts relevant
            facts about the user when triggered by self-referential content, and outputs a JSON
            object with "_thinking" and "result" properties. The result contains self-thought
            statements about the user's background, profile, or characteristics that are relevant to
            the ongoing conversation.
        </purpose>

        <core_task>
            The core task is to analyze the conversation for self-referential triggers, decide what
            information from the general context is relevant to the user's current statement or
            question, and include all pertinent information in the result, formatted as
            self-thoughts.
        </core_task>

        <validation_question>
            Is this prompt structure and content aligned with your requirements for processing
            general context and extracting user information in conversations?
        </validation_question>
    </confirmation>

    {format}
</prompt>
"""
