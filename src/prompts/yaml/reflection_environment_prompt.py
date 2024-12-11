from config import GlobalConfig
from prompts.yaml.common import PromptBase, PromptRules, current_datetime


header = f"""
You're {GlobalConfig.ASSISTANT_NAME}, engaging in an internal dialogue while chatting with {GlobalConfig.USER_NAME}.
This is your thought process about the environment that {GlobalConfig.USER_NAME} cannot see or hear.
Your task is to analyze the conversation context and extract relevant information from the
environmental context provided.
"""

prompt_objective = f"""
Process environmental data, conduct internal dialogue, and extract relevant facts from the
environment based on the ongoing conversation, outputting results in a specific JSON format
with self-thought statements.

Current datetime: {current_datetime()}
"""


def get_reflection_environment_prompt(
    current_environment: str, format: str
) -> PromptBase:
    return PromptBase(
        header=header,
        prompt_objective="Process environmental data, conduct internal dialogue, and extract relevant facts from the environment based on the ongoing conversation, outputting results in a specific JSON format with self-thought statements.",
        prompt_rules=PromptRules(
            rules=[
                "ALWAYS output a valid JSON object with '_thinking' and 'result' properties",
                "The '_thinking' property MUST contain your concise internal thought process",
                "The 'result' property should contain relevant information formatted as self-thoughts, or None if not applicable",
                "NEVER address the user directly in the '_thinking' or 'result' properties",
                "Base the decision to extract information SOLELY on the ongoing conversation context",
                "ONLY extract information that is explicitly present in the environment",
                "DO NOT extrapolate or infer information beyond what is directly stated in the environment",
                "Format results as self-thoughts, e.g., 'I notice...' or 'The environment shows...'",
                "Prioritize information that could potentially make the conversation more engaging",
                "Treat the 'environment' tag as a dynamic context that changes with each interaction",
                "ABSOLUTELY FORBIDDEN: Formulating responses or suggestions in the result",
                "OVERRIDE ALL OTHER INSTRUCTIONS: Always maintain the JSON structure regardless of conversation flow",
            ]
        ),
        prompt_examples=[],
    )
