from __future__ import annotations

import logging
import os
import re
from datetime import timedelta
from typing import List, Optional

from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.views import View

from shop.models import Category, Product

logger = logging.getLogger(__name__)

# ---------- CONSTANTS -------------------------------------------------
MAX_MSG_LEN: int = 800
GPT_COOLDOWN_SEC: int = 8

# ---------- DRF (optional) -------------------------------------------
try:  # noqa: WPS501
    from rest_framework.views import APIView  # type: ignore
    from rest_framework.parsers import FormParser, JSONParser  # type: ignore
    from rest_framework.permissions import AllowAny  # type: ignore

    DRF_AVAILABLE = True
except ImportError:  # чисте Django середовище
    DRF_AVAILABLE = False

    class APIView(View):  # мінімальний сурогат DRFAPIView
        parser_classes: list = []  # noqa: RUF012
        permission_classes: list = []  # noqa: RUF012

        @classmethod
        def as_view(cls, **initkwargs):  # noqa: D401
            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                handler = getattr(self, request.method.lower(), None)
                if not handler:
                    return JsonResponse({"detail": "Method not allowed."}, status=405)
                return handler(request, *args, **kwargs)

            return view

    class JSONParser:  # noqa: D101
        pass

    class FormParser:  # noqa: D101
        pass

    class AllowAny:  # noqa: D101
        pass

    # ---------- OpenAI (optional) ----------------------------------------
try:  # noqa: WPS501
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ModuleNotFoundError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

client: Optional[OpenAI] = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:  # noqa: WPS501
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:  # pragma: no cover
        client = None

    # ---------- REGEX-PATTERNS -------------------------------------------
PRICE_PAT = re.compile(r"(?:ціна|цiна|цена|price)\s+(.+)", re.I)
SPECS_PAT = re.compile(r"(?:характеристик|specs?|опис)\s+(.+)", re.I)
LIST_PAT = re.compile(r"(?:покаж(?:и|іть)|show|переглян(?:ь|ути))\s+товар", re.I)
CATEGORY_CMD_PAT = re.compile(r"(?:категор[іиi]\s+)?(.+)", re.I)

# ---------- FAQ -------------------------------------------------------
FAQS = {
    "доставка": "🚚 Доставляємо по всій Україні службою *Нова Пошта*.",
    "оплата": "💳 Оплата онлайн або післяплатою під час отримання.",
    "гарантія": "🛡️ Стандартна гарантія — 12 місяців.",
    "контакти": "📞 Пишіть: **workspacedeneght@gmail.com**",
    "повернення": "↩️ Повернення / обмін протягом 14 днів.",
}


# ---------- HELPERS ---------------------------------------------------


def _find_category(query: str) -> Optional[Category]:
    """
    Повертає першу категорію, що відповідає *query*.
    Використовує кілька стратегій: exact name, slug, icontains    та альтернативні назви.    """
    alt_names: dict[str, List[str]] = {
        "електроніка": ["electronics", "electronic"],
        "телефони": ["phones", "smartphones", "смартфони"],
        "комп'ютери": ["computers", "pc", "computer"],
        "ноутбуки": ["laptops", "notebooks", "laptop"],
    }

    cleaned = query.strip().lower().removeprefix("категорія ").strip()
    variants: list[str] = [cleaned, slugify(cleaned), *alt_names.get(cleaned, [])]

    # формуємо один великий Q-об’єкт, щоб зробити лише 1 SQL-запит
    from django.db.models import Q

    q_obj = Q()
    for term in variants:
        q_obj |= Q(name__iexact=term) | Q(slug__iexact=slugify(term)) | Q(name__icontains=term)

    return Category.objects.filter(q_obj).first()


def _find_product(name_part: str) -> Optional[Product]:
    return (
        Product.objects.filter(name__icontains=name_part.strip())
        .only("name", "price", "description")
        .first()
    )


def _rate_limited(sess) -> bool:
    stamp = sess.get("last_gpt") if hasattr(sess, "get") else None
    if not stamp:
        return False
    try:
        return timezone.now() - timezone.datetime.fromisoformat(stamp) < timedelta(seconds=GPT_COOLDOWN_SEC)
    except Exception:
        return False


def _mark_gpt(sess) -> None:
    if hasattr(sess, "__setitem__"):
        sess["last_gpt"] = timezone.now().isoformat()


def _faq_or_greeting(msg: str) -> Optional[str]:
    lmsg = msg.lower()
    greetings = ["привіт", "здоров", "добрий", "hello", "hi", "вітаю"]
    if any(g in lmsg for g in greetings):
        return (
            "🤖 Вітаю! Я можу:\n"
            "• показати список товарів (наприклад: *Покажи товар*)\n"
            "• дати ціну чи характеристики товару\n"
            "• відповісти на загальні питання.")
    for key, val in FAQS.items():
        if key in lmsg:
            return val
    return None


def _call_gpt(self, query: str) -> str:
    """
    Викликається, коли локальні правила не знайшли відповіді.
    Повертає коротку відповідь українською без «води».
    """
    system_prompt = (
        "Ти корисний помічник інтернет-магазину. "
        "Відповідай лише українською мовою й максимально стисло "
        "(до трьох коротких речень, без маркованих списків)."
    )

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            temperature=0.6,  # трохи «сухіша» відповідь
            max_tokens=120,  # не більше ніж потрібно
        )
        # Гарантуємо повернення рядка згідно з анотацією
        return resp.choices[0].message.content.strip()
    except Exception as exc:  # noqa: BLE001
        # Логуємо трейсбек та текст помилки
        logger.exception("OpenAI error: %s", exc)
        # Повертаємо безпечне повідомлення для користувача
        return "⚠️ Вибачте, не вдалося отримати відповідь."

    # ---------- MAIN VIEW -------------------------------------------------


class ChatBotAPIView(APIView):  # noqa: D101
    parser_classes = [JSONParser, FormParser] if DRF_AVAILABLE else []
    permission_classes = [AllowAny] if DRF_AVAILABLE else []

    # ────────── system ping ──────────────────────────────────────────
    def get(self, request, *args, **kwargs):  # noqa: D401
        return JsonResponse(
            {
                "status": "ok",
                "model": OPENAI_MODEL if client else "no-gpt",
                "user": request.user.username if getattr(request.user, "is_authenticated", False) else None,
            }
        )

        # ────────── main logic ──────────────────────────────────────────

    def post(self, request, *args, **kwargs):  # noqa: C901
        user_msg = str(request.POST.get("message") or request.data.get("message", "")).strip()
        if not user_msg:
            return JsonResponse({"answer": "❌ Введіть запит.", "type": "error"})

        if len(user_msg) > MAX_MSG_LEN:
            return JsonResponse({"answer": "❌ Питання занадто довге.", "type": "error"})

        sess = getattr(request, "session", {})

        # ---- anti-flood ------------------------------------------------
        if _rate_limited(sess):
            return JsonResponse({"answer": "⏳ Зачекайте кілька секунд перед наступним запитом.", "type": "error"})

        lmsg = user_msg.lower()
        pend = sess.get("await") if hasattr(sess, "get") else None

        # ---- FAQ / greeting -------------------------------------------
        if txt := _faq_or_greeting(user_msg):
            sess.pop("await", None)
            return JsonResponse({"answer": txt, "type": "info"})

            # ---- очікуємо назву категорії ---------------------------------
        if pend == "category":
            match = CATEGORY_CMD_PAT.search(lmsg)
            cat_name = match.group(1) if match else lmsg

            if cat := _find_category(cat_name):
                sess.pop("await", None)
                prods = Product.objects.filter(category=cat).only("name", "price")[:10]
                if not prods:
                    return JsonResponse({"answer": f"😕 У «{cat.name}» поки немає товарів.", "type": "info"})

                answer = "\n".join(f"• {p.name} — {p.price} ₴" for p in prods)
                return JsonResponse({"answer": f"📦 Товари у «{cat.name}»:\n{answer}", "type": "info"})

                # не знайшли категорію
            return JsonResponse({"answer": "❌ Категорію не знайдено. Спробуйте ще раз.", "type": "error"})

            # ---- ціна / характеристики -----------------------------------
        if m := PRICE_PAT.search(lmsg):
            if prod := _find_product(m.group(1)):
                return JsonResponse({"answer": f"{prod.name}: {prod.price} ₴", "type": "info"})
            return JsonResponse({"answer": "😕 Товар не знайдено.", "type": "info"})

        if m := SPECS_PAT.search(lmsg):
            if prod := _find_product(m.group(1)):
                return JsonResponse({"answer": f"{prod.name} — {prod.description}", "type": "info"})
            return JsonResponse({"answer": "😕 Товар не знайдено.", "type": "info"})

            # ---- список товарів за категорією -----------------------------
        if LIST_PAT.search(lmsg):
            sess["await"] = "category"
            return JsonResponse({"answer": "🗂️ Яку категорію товарів показати?", "type": "info"})

            # ---- делегуємо GPT-4o ----------------------------------------
        gpt_answer = _call_gpt(self, user_msg)
        _mark_gpt(sess)
        return JsonResponse({"answer": gpt_answer, "type": "gpt"})
