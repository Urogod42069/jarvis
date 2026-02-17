"""Tool: search the web using Gemini API with Google Search grounding."""

from __future__ import annotations

import os
from typing import Any

from .base import Tool


class WebSearchTool(Tool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information using Google Search. "
            "Returns a grounded answer with source URLs. "
            "Use for questions about recent events, live data, or anything "
            "beyond your knowledge cutoff."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up on the web.",
                },
            },
            "required": ["query"],
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    def execute(self, *, query: str) -> str:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            return "Error: GEMINI_API_KEY is not set in .env"

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            return "Error: google-genai package is not installed. Run: pip install google-genai"

        client = genai.Client(api_key=api_key)

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
        except Exception as exc:
            return f"Error during web search: {exc}"

        # Extract answer text
        answer = response.text or "(no answer returned)"

        # Extract source URLs from grounding metadata
        sources: list[str] = []
        try:
            metadata = response.candidates[0].grounding_metadata
            if metadata and metadata.grounding_chunks:
                for chunk in metadata.grounding_chunks:
                    if chunk.web and chunk.web.uri:
                        url = chunk.web.uri
                        title = chunk.web.title or url
                        sources.append(f"- {title}: {url}")
        except (AttributeError, IndexError):
            pass

        result = answer
        if sources:
            result += "\n\nSources:\n" + "\n".join(sources)

        return result
