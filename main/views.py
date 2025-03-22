from django.shortcuts import render,redirect
from django.views.generic import TemplateView,View,CreateView
from .disease_prediction import *
from django.http import JsonResponse
from groq import Groq
import json
from social_core.exceptions import AuthCanceled
from django.contrib.auth import logout
from django.contrib.auth import logout as auth_logout,authenticate,login
from .models import *
from django.urls import reverse_lazy
from .forms import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class CustomLogoutView(View):
    def get(self, request):
        logout(request)  # Log out the user
        response = redirect('/')  # Redirect to home or login page
        response.delete_cookie('sessionid')  # Delete session cookie
        response.delete_cookie('csrftoken')  # Delete CSRF token if applicable
        return response

def custom_social_auth_exception_middleware(request, exception):
    if isinstance(exception, AuthCanceled):
        return redirect('login')
    return render(request, 'error.html', {'error': str(exception)})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        log_form=LogForm(data=request.POST)
        if log_form.is_valid():  
            email=log_form.cleaned_data.get('email')
            password=log_form.cleaned_data.get('password')
            user=authenticate(request,email=email,password=password)
            print(user)
            if user: 
                login(request,user)
                return redirect('home')
            else:
                return render(request,'login.html',{"form":log_form})
        else:
            return render(request,'login.html',{"form":log_form}) 
    return render(request, 'login.html')

import re

class Home(TemplateView):
    template_name='home.html'

class SchemeView(TemplateView):
    template_name='schemes.html'

class ChatbotView(View):
    def get(self, request):
        return render(request, "chatbot.html")
    
    def post(self, request): 
        try:
            body = json.loads(request.body)
            user_input = body.get('userInput')
            language = body.get('language', 'english')  # Default to English if not specified
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON format."})
    
        if not user_input:  # If user_input is None or empty
            print("no input")
            return JsonResponse({"error": "No user input provided."})  
        
        print("User Input:", user_input)
        print("Selected Language:", language)
        
        # Detect language if not specified (optional enhancement)
        if language == 'auto':
            language = detect_language(user_input)
        
        # Multi-language static responses
        static_responses = get_static_responses(language)
        
        lower_input = user_input.lower().strip()
        if lower_input in static_responses:
            print(static_responses[lower_input])
            return JsonResponse({'response': [static_responses[lower_input]]})
        
        try:
            print(f"Processing via GROQ in {language}")
            data = get_groq_response(user_input, language)
            treatment_list = data.split('\n')
            return JsonResponse({'response': treatment_list})
        except Exception as e:
            return JsonResponse({"error": f"Failed to get GROQ response: {str(e)}"})

def detect_language(text):
    """
    Simple language detection based on script and common words
    For production, consider using a proper language detection library like langdetect
    """
    # Simple language detection logic
    malayalam_pattern = re.compile(r'[\u0D00-\u0D7F]')
    tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    
    if malayalam_pattern.search(text):
        return 'malayalam'
    elif tamil_pattern.search(text):
        return 'tamil'
    elif hindi_pattern.search(text):
        return 'hindi'
    else:
        return 'english'  # Default to English

def get_static_responses(language):
    """
    Returns static responses based on selected language
    """
    responses = {
        'english': {
            "hi": "Hello! How can I assist you today?",
            "hello": "Hi there! How can I help you?",
            "how are you": "I'm just a chatbot, but I'm doing great! How about you?",
            "bye": "Goodbye! Take care.",
            "whats up": "Not much, just here to help you. How can I assist you today?",
        },
        'malayalam': {
            "hi": "ഹലോ! ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?",
            "hello": "നമസ്കാരം! ഞാൻ നിങ്ങളെ സഹായിക്കാൻ ഇവിടെ ഉണ്ട്.",
            "how are you": "ഞാൻ ഒരു ചാറ്റ്ബോട്ട് മാത്രമാണ്, പക്ഷേ എനിക്ക് സുഖമാണ്! നിങ്ങൾക്ക് എങ്ങനെയുണ്ട്?",
            "bye": "വിട! സ്വസ്ഥമായി ഇരിക്കുക.",
            "whats up": "ഒന്നുമില്ല, ഞാൻ നിങ്ങളെ സഹായിക്കാൻ ഇവിടെ ഉണ്ട്. ഇന്ന് ഞാൻ എങ്ങനെ സഹായിക്കണം?",
        },
        'tamil': {
            "hi": "வணக்கம்! நான் உங்களுக்கு எப்படி உதவலாம்?",
            "hello": "ஹலோ! நான் உங்களுக்கு என்ன செய்யலாம்?",
            "how are you": "நான் வெறும் சாட்போட் தான், ஆனால் நான் நன்றாக இருக்கிறேன்! நீங்கள் எப்படி இருக்கிறீர்கள்?",
            "bye": "குட்பை! கவனமாக இருங்கள்.",
            "whats up": "ஒன்றுமில்லை, நான் உங்களுக்கு உதவ இங்கே இருக்கிறேன். இன்று எப்படி உதவலாம்?",
        },
        'hindi': {
            "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?",
            "hello": "हैलो! मैं आपकी सहायता के लिए यहाँ हूँ।",
            "how are you": "मैं सिर्फ एक चैटबॉट हूँ, लेकिन मैं अच्छा हूँ! आप कैसे हैं?",
            "bye": "अलविदा! अपना ख्याल रखें।",
            "whats up": "कुछ खास नहीं, मैं आपकी सहायता के लिए यहाँ हूँ। आज मैं आपकी कैसे मदद कर सकता हूँ?",
        }
    }

    
    return responses.get(language, responses['english'])

def get_groq_response(user_input, language='english'):
    """
    Communicate with the GROQ chatbot to get a response based on user input and language.
    """
    print(f"Getting GROQ response for: {user_input} in {language}")
    
    # Prepare system message based on language
    system_messages = {
        'english': "You are a helpful assistant . Respond in English.",
        'malayalam': "You are a helpful assistant . Respond in Malayalam.",
        'tamil': "You are a helpful assistant . Respond in Tamil.",
        'hindi': "You are a helpful assistant . Respond in Hindi."
    }
    
    system_message = system_messages.get(language, system_messages['english'])
    
    client = Groq(
        api_key="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",
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": user_input,
            }
        ],
        model="llama3-8b-8192",
        stream=False,
    )

    response = chat_completion.choices[0].message.content
    response = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', response)
    return response


from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.storage import default_storage

model_path = tf.keras.models.load_model(".\crop\main\Wheat.keras", compile=False, safe_mode=False)

UPLOAD_FOLDER = os.path.join(settings.MEDIA_ROOT, 'uploaded_images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class PredictionView(View):
    def get(self, request):
        return render(request, "disease_prediction.html")
    def post(self, request):
        image = request.FILES.get('image')  
        if not image:
            return render(request, "disease_prediction.html", {'error': 'Please upload an image.'})
        image_path = os.path.join(UPLOAD_FOLDER, image.name)
        with default_storage.open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        # Save the uploaded image to the database (History model assumed to be set up for this)
        predictions = History.objects.create(
            user=request.user,
            image=image,
        )
        img = preprocess_image(image_path)

        prediction = model_path.predict(img)
        predicted_class = class_labels[np.argmax(prediction)]
        
        # Preprocess the image and make prediction
        # test_image = load_and_prep_image(image, img_shape=224)
        cat = predicted_class
        
        # Get treatment recommendations based on the predicted class
        treatment = get_groq_response(f"{cat} treatment recommendations")
        treatment_list = treatment.split('\n')
        
        # Return the response to the template
        return render(request, "disease_prediction.html", {
            'response': cat,
            'treat': treatment_list,
            "uploaded_image_url": predictions.image.url,
        })


class RegView(CreateView):
    form_class=Reg
    template_name="signup.html"
    model=CustUser
    success_url=reverse_lazy("login")  