import uuid

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import BabyVideoTemplate, Festival,WishLog
from django.conf import settings
from django.http import JsonResponse
import os



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")




from google import genai

def generate_ai_wish(request):
    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Write a beautiful festival wish"
    )

    result = response.text

    # return your Django response here

# 🏠 Home
from django.shortcuts import render
from django.db.models import Count, Q

from django.core.paginator import Paginator
from django.db.models import Count


def home(request):

    trending_festivals = (
        Festival.objects
        .filter(is_trending=True)
        .annotate(
            wish_count=Count('wishes')
        )
        .order_by('-wish_count', 'id')[:8]
    )

    recent_wishes = (
        WishLog.objects
        .select_related('festival')
        .order_by('-created_at')[:5]
    )

    return render(
        request,
        'main_index.html',
        {
            'trending_festivals': trending_festivals,
            'recent_wishes': recent_wishes,
        }
    )


def list_festival(request):

    festivals = (
        Festival.objects
        .all()
        .order_by('date')
    )

    query = request.GET.get('q', '').strip()

    if query:

        festivals = festivals.filter(
            name__icontains=query
        )

    paginator = Paginator(
        festivals,
        8
    )

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(
        page_number
    )

    return render(
        request,
        'list_festival.html',
        {
            'page_obj': page_obj,
            'query': query,
        }
    )

# 🎯 Generate Page (IMPORTANT FIX)
# def generate_page(request, slug):
#     festival = get_object_or_404(Festival, slug=slug)
#     # Update view count
#     festival.views += 1
#     festival.save()

#     return render(request, 'generate.html', {
#         'festival': festival   # FULL OBJECT (not slug)
#     })


from django.shortcuts import render, get_object_or_404

from .models import Festival, BabyVideoTemplate


def generate_page(request, slug):

    festival = get_object_or_404(
        Festival,
        slug=slug
    )

    trending_festivals = Festival.objects.filter(
        is_trending=True
    )

    baby_templates = BabyVideoTemplate.objects.filter(
        is_active=True
    ).order_by("created_at")

    context = {
        "festival": festival,
        "trending_festivals": trending_festivals,
        "baby_templates": baby_templates,
    }

    return render(
        request,
        "generate.html",
        context
    )

# 🔗 Generate Link (IMPORTANT FIX)
from django.urls import reverse
from django.http import JsonResponse
from .models import WishLog, Festival
from django.shortcuts import get_object_or_404

# def generate_link(request):
#     if request.method == 'POST':
#         name = request.POST.get('name', 'Friend').strip()
#         festival_slug = request.POST.get('festival')

#         try:
#             # 1. Get the festival object
#             festival_obj = get_object_or_404(Festival, slug=festival_slug)

#             # 2. Log the activity for your "Recently Created" feed
#             if name and name != 'Friend':
#                 WishLog.objects.create(
#                     sender_name=name,
#                     festival=festival_obj
#                 )

#             # 3. Create the URL using 'reverse' for the 'festival_wish' path
#             # This automatically builds: /wish/holi/
#             relative_url = reverse('festival_wish', kwargs={'slug': festival_slug})
            
#             # 4. Build the full absolute URL with the name parameter
#             # Results in: https://yourdomain.com/wish/holi/?name=Rahul
#             full_url = f"{request.build_absolute_uri(relative_url)}?name={name}"

#             return JsonResponse({'link': full_url})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)

#     return JsonResponse({'error': 'Invalid request'}, status=400)





from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Festival, WishLog


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from urllib.parse import quote


def generate_link(request):

    if request.method != 'POST':

        return JsonResponse(
            {
                'error': 'Invalid request'
            },
            status=400
        )


    try:

        # -----------------------------
        # GET DATA
        # -----------------------------

        sender_name = request.POST.get(
            'sender_name',
            ''
        ).strip()


        receiver_name = request.POST.get(
            'receiver_name',
            ''
        ).strip()


        festival_slug = request.POST.get(
            'festival',
            ''
        ).strip()


        ai_message = request.POST.get(
            'ai_message',
            ''
        ).strip()


        photo = request.FILES.get(
            'photo'
        )


        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not sender_name:

            return JsonResponse(
                {
                    'error': 'Your name is required'
                },
                status=400
            )


        if not receiver_name:

            return JsonResponse(
                {
                    'error': "Friend's name is required"
                },
                status=400
            )


        if not festival_slug:

            return JsonResponse(
                {
                    'error': 'Festival is required'
                },
                status=400
            )


        if not photo:

            return JsonResponse(
                {
                    'error': "Friend's photo is required"
                },
                status=400
            )


        # -----------------------------
        # FESTIVAL
        # -----------------------------

        festival_obj = get_object_or_404(
            Festival,
            slug=festival_slug
        )


        # -----------------------------
        # CREATE WISH
        # -----------------------------

        wish = WishLog.objects.create(

            sender_name=sender_name,

            receiver_name=receiver_name,

            receiver_photo=photo,

            ai_message=ai_message,

            festival=festival_obj

        )


        # -----------------------------
        # BASE URL
        # -----------------------------

        relative_url = reverse(
            'festival_wish',
            kwargs={
                'slug': festival_slug
            }
        )


        # -----------------------------
        # ENCODE RECEIVER NAME
        # -----------------------------

        encoded_receiver =quote(receiver_name)


        # -----------------------------
        # FINAL URL
        # -----------------------------

        full_url = (
            f"{request.build_absolute_uri(relative_url)}"
            f"?wish={wish.wish_token}"
            f"&receiver={encoded_receiver}"
        )


        # -----------------------------
        # RESPONSE
        # -----------------------------

        return JsonResponse({

            'success': True,

            'link': full_url,

            'festival': festival_obj.name,

            'sender_name': sender_name,

            'receiver_name': receiver_name,

            'ai_message': ai_message

        })


    except Exception as e:

        print(
            "GENERATE LINK ERROR:",
            str(e)
        )

        return JsonResponse({

            'success': False,

            'error': str(e)

        }, status=500)


    

def festival_wish(request, slug):

    festival = get_object_or_404(
        Festival,
        slug=slug
    )

    token = request.GET.get('wish')

    wish = None

    if token:

        try:

            wish = WishLog.objects.get(
                wish_token=token,
                festival=festival
            )

        except WishLog.DoesNotExist:

            wish = None

    if wish:

        sender_name = wish.sender_name
        receiver_name = wish.receiver_name
        photo = wish.receiver_photo

    else:

        sender_name = None

        receiver_name = request.GET.get(
            'name',
            'Friend'
        )

        photo = None

    return render(
        request,
        'wishes/universal.html',
        {
            'festival': festival,
            'wish': wish,
            'sender_name': sender_name,
            'receiver_name': receiver_name,
            'photo': photo,
        }
    )


def search_festival(request):
    query = request.GET.get('q', '')

    festivals = Festival.objects.filter(name__icontains=query)[:5]

    data = []
    for f in festivals:
        data.append({
            'name': f.name,
            'slug': f.slug
        })

    return JsonResponse(data, safe=False)



import os

from google import genai
from django.http import JsonResponse



def generate_ai_wish(request):

    if request.method != 'POST':
        return JsonResponse(
            {
                'error': 'Invalid request'
            },
            status=400
        )

    try:

        sender_name = request.POST.get(
            'sender_name',
            ''
        ).strip()

        receiver_name = request.POST.get(
            'receiver_name',
            ''
        ).strip()

        festival_slug = request.POST.get(
            'festival',
            ''
        ).strip()

        style = request.POST.get(
            'style',
            'emotional'
        ).strip()

        language = request.POST.get(
            'language',
            'hinglish'
        ).strip()


        # -----------------------------
        # VALIDATION
        # -----------------------------

        if not sender_name:

            return JsonResponse(
                {
                    'error': 'Your name is required'
                },
                status=400
            )


        if not receiver_name:

            return JsonResponse(
                {
                    'error': "Friend's name is required"
                },
                status=400
            )


        if not festival_slug:

            return JsonResponse(
                {
                    'error': 'Festival is required'
                },
                status=400
            )


        # -----------------------------
        # GET FESTIVAL
        # -----------------------------

        festival = get_object_or_404(
            Festival,
            slug=festival_slug
        )


        # -----------------------------
        # LANGUAGE
        # -----------------------------

        language_map = {

            'hinglish':
                'Hindi mixed naturally with English',

            'hindi':
                'Hindi in Devanagari script',

            'marathi':
                'Marathi in Devanagari script',

            'english':
                'English'

        }

        language_instruction = language_map.get(
            language,
            'Hindi mixed naturally with English'
        )


        # -----------------------------
        # STYLE
        # -----------------------------

        style_map = {

            'emotional':
                'heart-touching and emotional',

            'funny':
                'funny and playful',

            'friendship':
                'warm and focused on friendship',

            'family':
                'loving and family-oriented',

            'romantic':
                'sweet and romantic',

            'traditional':
                'traditional and respectful',

            'professional':
                'professional and elegant'

        }

        style_instruction = style_map.get(
            style,
            'warm and emotional'
        )


        # -----------------------------
        # GEMINI PROMPT
        # -----------------------------

        prompt = f"""
Create a beautiful personalized Indian festival greeting.

Festival:
{festival.name}

Festival heading:
{festival.heading}

Sender:
{sender_name}

Receiver:
{receiver_name}

Style:
{style_instruction}

Language:
{language_instruction}

Requirements:

1. Address the receiver by their name.
2. Mention the festival naturally.
3. Make the message personal.
4. Make it warm and beautiful.
5. Use suitable Indian festival emojis.
6. Keep it suitable for sharing on WhatsApp.
7. Maximum 80-100 words.
8. Do not mention AI.
9. Do not use hashtags.
10. Do not put quotation marks around the message.
11. Do not write the sender name as a signature.
"""


        # -----------------------------
        # GEMINI CLIENT
        # -----------------------------

        client = genai.Client(
            api_key=os.environ.get(
                "GEMINI_API_KEY"
            )
        )


        # -----------------------------
        # GENERATE
        # -----------------------------

        response = client.models.generate_content(

            model = "gemini-3.6-flash",

            contents=prompt

        )


        ai_message = response.text.strip()


        return JsonResponse({

            'success': True,

            'wish': ai_message

        })


    except Exception as e:

        return JsonResponse({

            'success': False,

            'error': str(e)

        }, status=500)




        import os

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from google import genai

from .models import Festival, WishLog


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)


# =========================================================
# GENERATE AI WISH
# =========================================================

def generate_ai_wish(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request method."
            },
            status=400
        )


    try:

        sender_name = request.POST.get(
            "sender_name",
            ""
        ).strip()

        receiver_name = request.POST.get(
            "receiver_name",
            ""
        ).strip()

        festival_slug = request.POST.get(
            "festival",
            ""
        ).strip()

        style = request.POST.get(
            "style",
            "Heart Touching"
        ).strip()

        language = request.POST.get(
            "language",
            "Hindi"
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not sender_name:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Sender name is required."
                },
                status=400
            )


        if not receiver_name:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Receiver name is required."
                },
                status=400
            )


        if not festival_slug:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Festival is required."
                },
                status=400
            )


        # -------------------------------------------------
        # GET FESTIVAL
        # -------------------------------------------------

        festival = get_object_or_404(
            Festival,
            slug=festival_slug
        )


        # -------------------------------------------------
        # GEMINI PROMPT
        # -------------------------------------------------

        prompt = f"""
Create a beautiful personalized {festival.name} festival
wish.

Sender name: {sender_name}
Receiver name: {receiver_name}
Festival: {festival.name}
Wish style: {style}
Language: {language}

Requirements:

1. Address the receiver by their name.
2. Mention the festival naturally.
3. Make the wish emotional, warm and beautiful.
4. Write it as a personal message from the sender.
5. Do not mention AI, Gemini or prompt.
6. Do not use markdown.
7. Use suitable emojis.
8. Keep it around 50-100 words.
9. Do not put the message inside quotation marks.

Generate only the final wish message.
"""


        # -------------------------------------------------
        # GEMINI
        # -------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        ai_message = (
            response.text.strip()
            if response.text
            else ""
        )


        if not ai_message:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Gemini returned an empty message."
                },
                status=500
            )


        # -------------------------------------------------
        # RETURN AI MESSAGE
        # -------------------------------------------------

        return JsonResponse(
            {
                "success": True,
                "wish": ai_message
            }
        )


    except Exception as e:

        print(
            "GEMINI ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )


# =========================================================
# GENERATE WISH LINK
# =========================================================

def generate_link(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "success": False,
                "error": "Invalid request."
            },
            status=400
        )


    try:

        # -------------------------------------------------
        # GET DATA
        # -------------------------------------------------

        sender_name = request.POST.get(
            "sender_name",
            ""
        ).strip()

        receiver_name = request.POST.get(
            "receiver_name",
            ""
        ).strip()

        festival_slug = request.POST.get(
            "festival",
            ""
        ).strip()

        ai_message = request.POST.get(
            "ai_message",
            ""
        ).strip()

        photo = request.FILES.get(
            "photo"
        )


        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print("==============================")
        print("SENDER:", sender_name)
        print("RECEIVER:", receiver_name)
        print("AI MESSAGE:", ai_message)
        print("PHOTO:", photo)
        print("==============================")


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not sender_name:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Your name is required."
                },
                status=400
            )


        if not receiver_name:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Friend's name is required."
                },
                status=400
            )


        if not festival_slug:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Festival is required."
                },
                status=400
            )


        if not photo:

            return JsonResponse(
                {
                    "success": False,
                    "error": "Friend's photo is required."
                },
                status=400
            )


        # -------------------------------------------------
        # FESTIVAL
        # -------------------------------------------------

        festival = get_object_or_404(
            Festival,
            slug=festival_slug
        )


        # -------------------------------------------------
        # CREATE WISH
        # -------------------------------------------------

        wish = WishLog.objects.create(

            sender_name=sender_name,

            receiver_name=receiver_name,

            receiver_photo=photo,

            ai_message=ai_message,

            festival=festival

        )


        # -------------------------------------------------
        # CREATE URL
        # -------------------------------------------------

        relative_url = reverse(
            "festival_wish",
            kwargs={
                "slug": festival_slug
            }
        )


        full_url = (
            f"{request.build_absolute_uri(relative_url)}"
            f"?wish={wish.wish_token}"
        )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return JsonResponse(
            {
                "success": True,

                "link": full_url,

                "festival": festival.name,

                "sender_name": sender_name,

                "receiver_name": receiver_name,

                "ai_message": ai_message
            }
        )


    except Exception as e:

        print(
            "GENERATE LINK ERROR:",
            str(e)
        )

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )


# =========================================================
# UNIVERSAL FESTIVAL WISH PAGE
# =========================================================

def festival_wish(request, slug):

    festival = get_object_or_404(
        Festival,
        slug=slug
    )


    token = request.GET.get(
        "wish"
    )


    wish = None


    # -----------------------------------------------------
    # FIND WISH
    # -----------------------------------------------------

    if token:

        try:

            wish = WishLog.objects.get(
                wish_token=token,
                festival=festival
            )

        except WishLog.DoesNotExist:

            wish = None


    # -----------------------------------------------------
    # WISH FOUND
    # -----------------------------------------------------

    if wish:

        sender_name = wish.sender_name

        receiver_name = wish.receiver_name

        photo = wish.receiver_photo

        ai_message = (
            wish.ai_message
            or ""
        )


    # -----------------------------------------------------
    # NORMAL FESTIVAL PAGE
    # -----------------------------------------------------

    else:

        sender_name = None

        receiver_name = request.GET.get(
            "receiver",
            "Friend"
        )

        photo = None

        ai_message = ""


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render(
        request,
        "wishes/universal.html",
        {
            "festival": festival,

            "wish": wish,

            "sender_name": sender_name,

            "receiver_name": receiver_name,

            "photo": photo,

            "ai_message": ai_message,
        }
    )



from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone

from .models import Festival


def festival_calendar(request):

    festivals = Festival.objects.all().order_by('date')

    return render(
        request,
        'wishes/calendar.html',
        {
            'festivals': festivals,
        }
    )


def generate_link_page(request, slug):

    festival = get_object_or_404(
        Festival,
        slug=slug
    )

    return render(
        request,
        'wishes/generate_link.html',
        {
            'festival': festival
        }
    )





from django.shortcuts import render


def about(request):

    return render(request,"wishes/about.html")


def contact(request):

    return render(
        request,
        "wishes/contact.html"
    )


def privacy_policy(request):

    return render(
        request,
        "wishes/privacy_policy.html"
    )


def terms(request):

    return render(
        request,
        "wishes/terms.html"
    )


def disclaimer(request):

    return render(
        request,
        "wishes/disclaimer.html"
    )




from django.db.models import F
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Festival, WishLog


def festival_wish(request, slug):

    print("====================================")
    print("FESTIVAL WISH VIEW CALLED")
    print("SLUG:", slug)
    print("QUERY STRING:", request.GET)
    print("====================================")

    # -----------------------------------------------------
    # GET FESTIVAL
    # -----------------------------------------------------

    festival = get_object_or_404(
        Festival,
        slug=slug
    )


    # -----------------------------------------------------
    # GET WISH TOKEN
    # -----------------------------------------------------

    token = request.GET.get("wish")

    print("WISH TOKEN:", token)


    wish = None


    # -----------------------------------------------------
    # FIND WISH
    # -----------------------------------------------------

    if token:

        try:

            wish = WishLog.objects.get(
                wish_token=token,
                festival=festival
            )

            print("WISH FOUND:", wish.id)
            print("CURRENT VIEWS:", wish.views)

        except WishLog.DoesNotExist:

            print("WISH NOT FOUND")

            return render(
                request,
                "wishes/link_invalid.html",
                {
                    "festival": festival
                }
            )


    # -----------------------------------------------------
    # EXPIRATION CHECK
    # -----------------------------------------------------

    if wish:

        if (
            wish.expires_at
            and
            wish.expires_at < timezone.now()
        ):

            return render(
                request,
                "wishes/link_expired.html",
                {
                    "festival": festival,
                    "wish": wish
                }
            )


    # -----------------------------------------------------
    # ACTIVE CHECK
    # -----------------------------------------------------

    if wish and not wish.is_active:

        return render(
            request,
            "wishes/link_inactive.html",
            {
                "festival": festival,
                "wish": wish
            }
        )


    # =====================================================
    # ⭐ INCREASE VIEW COUNT
    # =====================================================

    if wish:

        WishLog.objects.filter(
            id=wish.id
        ).update(
            views=F("views") + 1
        )

        print("VIEW COUNT INCREASED")


    # -----------------------------------------------------
    # DATA
    # -----------------------------------------------------

    receiver_name = (
        wish.receiver_name
        if wish
        else "Friend"
    )

    sender_name = (
        wish.sender_name
        if wish
        else ""
    )

    photo = (
        wish.receiver_photo
        if wish
        else None
    )


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render(
        request,
        "wishes/universal.html",
        {
            "festival": festival,
            "wish": wish,
            "receiver_name": receiver_name,
            "name": receiver_name,
            "sender_name": sender_name,
            "photo": photo,
        }
    )


