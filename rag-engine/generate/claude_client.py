"""
claude_client.py — Claude API Integration
Sends the augmented prompt to Claude and returns the response.

Requires: ANTHROPIC_API_KEY environment variable
"""

import os
import logging

logger = logging.getLogger(__name__)


def get_client():
    """Initialize the Anthropic client."""
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not set!\n"
            "Run: export ANTHROPIC_API_KEY='sk-ant-...'\n"
            "Get your key at: https://console.anthropic.com/"
        )
    return anthropic.Anthropic(api_key=api_key)


def generate_response(
    system_prompt: str,
    user_message: str,
    config: dict,
    stream: bool = True,
) -> str:
    """
    Send the augmented prompt to Claude and get a response.
    
    Args:
        system_prompt: The system instructions
        user_message: The context + question
        config: Parsed config.yaml
        stream: Whether to stream the response (prints as it generates)
    
    Returns:
        Claude's full response text
    """
    gen_cfg = config["generation"]
    client = get_client()

    logger.info(f"Sending to Claude ({gen_cfg['model']})...")

    if stream:
        # Stream response — prints tokens as they arrive
        full_response = []
        with client.messages.stream(
            model=gen_cfg["model"],
            max_tokens=gen_cfg["max_tokens"],
            temperature=gen_cfg["temperature"],
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        ) as response:
            for text in response.text_stream:
                print(text, end="", flush=True)
                full_response.append(text)
        print()  # newline after stream ends
        return "".join(full_response)
    else:
        # Non-streaming — wait for full response
        response = client.messages.create(
            model=gen_cfg["model"],
            max_tokens=gen_cfg["max_tokens"],
            temperature=gen_cfg["temperature"],
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
