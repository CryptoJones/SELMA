"""Tests for SELMA prompt formatting — covers bugs fixed 2026-05-11."""

import sys
sys.path.insert(0, ".")

from src.selma.prompts import format_analysis_prompt, SYSTEM_PROMPT


def test_format_analysis_prompt_structure():
    messages = format_analysis_prompt("A suspect stole a vehicle.")
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"


def test_format_analysis_prompt_contains_incident():
    incident = "A suspect broke a window and entered a home."
    messages = format_analysis_prompt(incident)
    assert incident in messages[1]["content"]


def test_thinking_mode_uses_real_newlines():
    """Regression test: \\n\\n (escaped) was used instead of actual newlines.

    The thinking-mode suffix in model.py must produce real newlines so the
    instruction is separated from the system prompt when the chat template is
    applied. Literal backslash-n would appear verbatim in the rendered prompt.
    """
    suffix = "\n\nThink step by step through your analysis before presenting conclusions."
    # Confirm the suffix contains real newline characters, not escaped ones.
    assert "\n" in suffix
    assert "\\n" not in suffix

    messages = format_analysis_prompt("Test incident.")
    augmented = messages[0]["content"] + suffix
    # The augmented system prompt should contain real newlines before the instruction.
    assert augmented.count("\n") >= 2
    assert "\\n" not in augmented


def test_system_prompt_is_non_empty():
    assert len(SYSTEM_PROMPT) > 100


def test_system_prompt_emphasizes_criminal_primacy():
    """Criminal charges must be the stated primary output; civil must be labeled secondary."""
    assert "primary" in SYSTEM_PROMPT.lower() or "primary output" in SYSTEM_PROMPT.lower()
    assert "CIVIL" in SYSTEM_PROMPT
    assert "Not a criminal charge" in SYSTEM_PROMPT


def test_analysis_template_has_civil_section():
    from src.selma.prompts import ANALYSIS_TEMPLATE, CIVIL_PARALLEL_TEMPLATE
    assert "Civil Parallels" in ANALYSIS_TEMPLATE
    assert "civil_parallels" in ANALYSIS_TEMPLATE
    assert "CIVIL" in CIVIL_PARALLEL_TEMPLATE
    assert "not a criminal charge" in CIVIL_PARALLEL_TEMPLATE


def test_training_instruction_covers_civil():
    from src.selma.prompts import TRAINING_INSTRUCTION
    assert "civil" in TRAINING_INSTRUCTION.lower()
    assert "CIVIL" in TRAINING_INSTRUCTION


if __name__ == "__main__":
    test_format_analysis_prompt_structure()
    test_format_analysis_prompt_contains_incident()
    test_thinking_mode_uses_real_newlines()
    test_system_prompt_is_non_empty()
    test_system_prompt_emphasizes_criminal_primacy()
    test_analysis_template_has_civil_section()
    test_training_instruction_covers_civil()
    print("All prompt tests passed!")
