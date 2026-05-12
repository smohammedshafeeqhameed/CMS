import json
import os
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.conf import settings
try:
    from openai import OpenAI
    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except ImportError:
    client = None

class LandingPageView(TemplateView):
    template_name = 'core/landing.html'

class CollegeChatbotView(View):
    def post(self, request):
        try:
            print("text")
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            # Load college data
            data_file = os.path.join(settings.BASE_DIR, 'college_data.json')
            with open(data_file, 'r', encoding='utf-8') as f:
                college_info = json.load(f)
            
            # Format context for AI
            context = "Information about Holy Grace Academy of Engineering:\n"
            for qna in college_info.get('Sheet1', []):
                if qna.get('QUESTIONS') and qna.get('ANSWER'):
                    context += f"Q: {qna['QUESTIONS']}\nA: {qna['ANSWER']}\n\n"
            
            system_prompt = f"""
            You are a helpful and polite virtual assistant for Holy Grace Academy of Engineering. 
            Use ONLY the following context to answer the user's questions. 
            If the answer is not in the context, politely state that you only have information about the college's basic details and suggest them to contact the college office.
            
            Context:
            {context}
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=250
            )
            
            ai_message = response.choices[0].message.content
            return JsonResponse({'status': 'success', 'message': ai_message})
            
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
