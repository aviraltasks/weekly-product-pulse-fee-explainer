"""Domain errors for pulse generation."""


class PulsePipelineError(Exception):
    """User-visible failure (empty CSV, bad LLM output, missing keys)."""

