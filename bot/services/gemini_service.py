import google.generativeai as genai
import logging
import json
import io
import html
import asyncio
from PIL import Image
from config import GEMINI_API_KEY, GEMINI_MODEL
from database.db_utils import get_chat_history, add_to_chat_history

# Կոնֆիգուրացիան կատարում ենք պարզ եղանակով։
# Գրադարանը ինքնուրույն կվերցնի Proxy-ն միջավայրի փոփոխականներից, եթե դրանք սահմանված են։
genai.configure(api_key=GEMINI_API_KEY)


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    async def _safe_generate(
        self, prompt, use_json_config: bool = True, temperature: float = 0.4
    ) -> str | None:
        try:
            config_params = {"temperature": temperature}
            if use_json_config:
                config_params["response_mime_type"] = "application/json"

            config = genai.GenerationConfig(**config_params)
            response = await self.model.generate_content_async(
                prompt, generation_config=config
            )

            if not response.candidates:
                logging.warning("Gemini returned no candidates.")
                return None
            return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API error in _safe_generate: {e}")
            if hasattr(e, 'response'):
                logging.error(f"Gemini response: {e.response.text}")
            return None

    def _parse_json_response(self, response_text: str) -> dict | None:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Gemini JSON: {e}\n{response_text}")
            return None

    async def get_text_from_image(
        self, image_bytes: io.BytesIO, target_lang: str
    ) -> dict | None:
        try:
            img = Image.open(image_bytes)
        except Exception as e:
            logging.error(f"Pillow could not open image bytes: {e}")
            return None
        prompt = [
            (
                f"Analyze this image. Identify all text. Then, translate it to "
                f"{target_lang}. Format as JSON: "
                f'{{"found_text": "...", "translated_text": "...", "detected_language_name": "..."}}'
            ),
            img
        ]
        response_str = await self._safe_generate(prompt, temperature=0.1)
        if not response_str:
            return None
        return self._parse_json_response(response_str)

    async def translate_text(
        self, text: str, target_language: str, source_language: str = "auto"
    ) -> dict | None:
        prompt = (
            f'Translate "{text}" into {target_language}. Source language is '
            f'{source_language}. Respond in JSON: '
            f'{{"detected_language_name": "...", "translated_text": "..."}}'
        )
        response_str = await self._safe_generate(prompt, temperature=0.2)
        if not response_str:
            return None
        return self._parse_json_response(response_str)

    async def get_learning_item(
        self, item_type: str, mode: str, lang_info: dict, level: str,
        recent_items: list | None = None
    ) -> dict | None:
        recent_prompt = ""
        if recent_items:
            items_str = ", ".join(f'"{item}"' for item in recent_items)
            recent_prompt = (
                "\nIMPORTANT: Do not generate any of the following, which the "
                f"user has seen: {items_str}."
            )

        academic_prompt = (
            "\nEnsure the explanation is academically sound, clear, and "
            "suitable for a university-level student, but adapt the core "
            "complexity to the user's selected proficiency level."
        )

        if mode == 'human':
            prompt = self._get_human_lang_prompt(
                item_type, lang_info, level, recent_prompt
            )
        elif mode == 'programming':
            prompt = self._get_programming_lang_prompt(
                item_type, lang_info, level, recent_prompt, academic_prompt
            )
        else:
            return None

        response_str = await self._safe_generate(prompt, temperature=0.95)
        if not response_str:
            return None
        return self._parse_json_response(response_str)

    def _get_human_lang_prompt(
        self, item_type: str, lang_info: dict, level: str, recent_prompt: str
    ) -> str | None:
        native, learning = lang_info['native'], lang_info['learning']
        if item_type == 'word':
            return (
                f"Generate one interesting word in {learning} for a {level} "
                f"learner. Provide its translation in {native}.{recent_prompt}\n"
                f"JSON response: {{\"item\": \"...\", \"translation\": \"...\"}}"
            )
        if item_type == 'quiz':
            return (
                f"Create a multiple-choice quiz about {learning} for a {native} "
                f"speaker at {level} level.{recent_prompt}\nJSON response: "
                f"{{\"question\": \"...\", \"options\": [...], "
                f"\"correct_answer_text\": \"...\"}}"
            )
        return None

    def _get_programming_lang_prompt(
        self, item_type: str, lang_info: dict, level: str,
        recent_prompt: str, academic_prompt: str
    ) -> str | None:
        prog_lang = lang_info['programming']
        interface_lang = lang_info.get('interface_lang_name', 'English')
        lang_instruction = (
            f"CRITICAL INSTRUCTION: The entire response MUST be exclusively in "
            f"the {interface_lang} language. DO NOT mix languages. Use correct "
            "and natural-sounding terminology."
        )

        if item_type == 'concept':
            return (
                f"Generate a core concept for a {prog_lang} developer at "
                f"'{level}' level. {academic_prompt}{recent_prompt} "
                f"{lang_instruction}\nProvide an explanation and a code example."
                f"\nJSON response: {{\"item\": \"...\", \"explanation\": \"...\", "
                f"\"code_example\": \"...\"}}"
            )
        if item_type == 'quiz':
            return (
                f"Create a quiz about {prog_lang} for a developer at '{level}' "
                f"level. {academic_prompt}{recent_prompt} {lang_instruction}\n"
                f"JSON response: {{\"question\": \"...\", \"options\": [...], "
                f"\"correct_answer_text\": \"Exact text of correct option.\"}}"
            )
        return None

    async def get_fun_fact(
        self, mode: str, subject: str, interface_lang: str
    ) -> str | None:
        lang_instruction = f"CRITICAL: The fact MUST be in {interface_lang}."
        if mode == 'human':
            prompt = (
                f"Tell me one surprising, fun fact about the country/culture "
                f"of the {subject} language. {lang_instruction}"
            )
        else:
            prompt = (
                f"Tell me one surprising, fun fact about the history or a "
                f"feature of {subject}. {lang_instruction}"
            )

        response_str = await self._safe_generate(
            prompt, use_json_config=False, temperature=1.0
        )
        return html.unescape(response_str) if response_str else None

    async def evaluate_user_answer(
        self, original_text: str, user_translation: str,
        source_lang: str, target_lang: str
    ) -> str | None:
        prompt = (
            f'Original: "{original_text}" ({source_lang}). User translation: '
            f'"{user_translation}" ({target_lang}). Provide brief feedback in '
            f'{target_lang}.\nJSON response: {{"feedback": "..."}}'
        )
        response_str = await self._safe_generate(prompt, temperature=0.5)
        if not response_str:
            return None
        data = self._parse_json_response(response_str)
        return data.get("feedback") if data else None

    async def chat_with_ai(
        self, user_id: int, user_prompt: str,
        persona: str | None = None
    ) -> str:
        if persona is None:
            persona = "You are a helpful and friendly AI language tutor."

        chat_model = genai.GenerativeModel(
            GEMINI_MODEL,
            system_instruction=persona
        )
        
        history = await get_chat_history(user_id)
        current_chat_history = history + [{"role": "user", "parts": [{"text": user_prompt}]}]

        try:
            await add_to_chat_history(user_id, 'user', user_prompt)
            response = await chat_model.generate_content_async(current_chat_history)

            if response.candidates and response.candidates[0].content.parts:
                response_text = response.text.strip()
                await add_to_chat_history(user_id, 'model', response_text)
                return response_text

            return "Sorry, I couldn't generate a response."
        except Exception as e:
            logging.error(f"Gemini chat error for user {user_id}: {e}")
            return "An error occurred with the AI service. Please try again."