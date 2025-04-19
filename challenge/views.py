from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge
# Create your views here.


class DoItFast(View):
    def get(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, 'create-chal.html')

        try:
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            return render(request, 'create-chal.html', {'chal': chal, 'user_chal': user_chal})
        except:
            return render(request, 'create-chal.html', {'chal': chal, 'user_chal': None})

    # def get(self, request, challenge):
    #     if not request.user.is_authenticated:
    #         return redirect('login')
       
    #     try:
    #         chal = Challenge.objects.get(name=challenge)
    #         # Challenge exists, proceed as normal
    #         try:
    #             user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
    #             return render(request, 'challenge.html', {'chal': chal, 'user_chal': user_chal})
    #         except UserChallenge.DoesNotExist:
    #             return render(request, 'challenge.html', {'chal': chal, 'user_chal': None})
    #     except Challenge.DoesNotExist:
    #         # If challenge doesn't exist, render the challenge.html template 
    #         # with a flag indicating the challenge doesn't exist
    #         return render(request, 'challenge.html', {'chal': None, 'challenge_name': challenge})

    # def get(self, request, challenge):
    #     if not request.user.is_authenticated:
    #         return redirect('login')
       
    #     try:
    #         chal = Challenge.objects.get(name=challenge)
    #         # Challenge exists, check if user has attempted it
    #         try:
    #             user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
    #             # Determine if buttons should be shown in specific states
    #             button_state = 'stop' if user_chal.is_live else 'start'
    #             return render(request, 'challenge.html', {
    #                 'chal': chal, 
    #                 'user_chal': user_chal,
    #                 'button_state': button_state
    #             })
    #         except UserChallenge.DoesNotExist:
    #             return render(request, 'challenge.html', {
    #                 'chal': chal, 
    #                 'user_chal': None,
    #                 'button_state': 'start'
    #             })
    #     except Challenge.DoesNotExist:
    #         # Log that the challenge doesn't exist
    #         print(f"Challenge not found: {challenge}")
    #         # Return a more user-friendly error page
    #         return render(request, 'chal-not-found.html', {'challenge_name': challenge})
    
    def post(self, request, challenge):
        user_chall_exists = False
        if not request.user.is_authenticated:
            return redirect('login')
        
        try: # checking the existance of challenge
            chal = Challenge.objects.get(name=challenge)
        except Exception as e:
            return render(request, 'chal-not-found.html')

        try: # checking if he attempted it before or not, if yes then check if the container is live or not
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
            if user_chal.is_live:
                return JsonResponse({'message':'already running', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})
            user_chall_exists = True
        except:
            pass

        port = get_free_port(8000, 8100)
        if port == None:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})
        
        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        container_id = output.decode('utf-8').strip()
        
        if user_chall_exists:
            # TODO : reuse the container instead of creaing the new one
            user_chal.container_id = container_id
            user_chal.port = port
            user_chal.is_live = True
            user_chal.save()
        else:
            user_chal = UserChallenge(user=request.user, challenge=chal, container_id=container_id, port=port)
            user_chal.save()
        # save the output in database for stoping the container 
        return JsonResponse({'message': 'success', 'status': '200', 'endpoint': f'http://localhost:{port}'})



    def delete(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')
    
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        except Exception as e:
            return JsonResponse({'message': 'failed', 'status': '500'})

        user_chal.is_live = False
        user_chal.save()
        command = f"docker stop {user_chal.container_id}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, error = process.communicate()
        return JsonResponse({'message': 'success', 'status': '200'})
    
    # def put(self, request, challange):
    #     #TODO : implement flag checking
    #     return "not implemented"
    def put(self, request, challenge):  # Fixed parameter name
        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
        
            
            return JsonResponse({'message': 'Flag submission not yet implemented', 'status': '501'})
        except Challenge.DoesNotExist:
            return JsonResponse({'message': 'Challenge not found', 'status': '404'})
        except UserChallenge.DoesNotExist:
            return JsonResponse({'message': 'User challenge not found', 'status': '404'})



# class DoItFast(View):
#     def get(self, request, challenge):
#         if not request.user.is_authenticated:
#             return redirect('login')
       
#         try:
#             chal = Challenge.objects.get(name=challenge)
#             # Challenge exists, check if user has attempted it
#             try:
#                 user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
#                 # Determine if buttons should be shown in specific states
#                 button_state = 'stop' if user_chal.is_live else 'start'
#                 return render(request, 'challenge.html', {
#                     'chal': chal, 
#                     'user_chal': user_chal,
#                     'button_state': button_state
#                 })
#             except UserChallenge.DoesNotExist:
#                 return render(request, 'challenge.html', {
#                     'chal': chal, 
#                     'user_chal': None,
#                     'button_state': 'start'
#                 })
#         except Challenge.DoesNotExist:
#             # Log that the challenge doesn't exist
#             print(f"Challenge not found: {challenge}")
#             # Return a more user-friendly error page
#             return render(request, 'chal-not-found.html', {'challenge_name': challenge})
   
#     def post(self, request, challenge):
#         if not request.user.is_authenticated:
#             return redirect('login')
       
#         try:
#             chal = Challenge.objects.get(name=challenge)
#         except Challenge.DoesNotExist:
#             return JsonResponse({'message': 'Challenge not found', 'status': '404'})
            
#         # Check if user has an existing challenge
#         try:
#             user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
#             if user_chal.is_live:
#                 return JsonResponse({
#                     'message': 'already running', 
#                     'status': '200', 
#                     'endpoint': f'http://localhost:{user_chal.port}'
#                 })
#             user_chal_exists = True
#         except UserChallenge.DoesNotExist:
#             user_chal_exists = False
            
#         # Get a free port
#         port = get_free_port(chal.start_port, chal.end_port)
#         if port is None:
#             return JsonResponse({'message': 'No free ports available', 'status': '500', 'endpoint': 'None'})
       
#         # Start the docker container
#         try:
#             command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
#             process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             output, error = process.communicate()
            
#             if process.returncode != 0:
#                 return JsonResponse({'message': 'Docker error', 'status': '500', 'endpoint': 'None'})
                
#             container_id = output.decode('utf-8').strip()
#         except Exception as e:
#             return JsonResponse({'message': f'Error: {str(e)}', 'status': '500', 'endpoint': 'None'})
       
#         # Update or create the user challenge
#         if user_chal_exists:
#             user_chal.container_id = container_id
#             user_chal.port = port
#             user_chal.is_live = True
#             user_chal.save()
#         else:
#             user_chal = UserChallenge(
#                 user=request.user, 
#                 challenge=chal, 
#                 container_id=container_id, 
#                 port=port,
#                 is_live=True
#             )
#             user_chal.save()
            
#         return JsonResponse({
#             'message': 'success', 
#             'status': '200', 
#             'endpoint': f'http://localhost:{port}'
#         })
        
#     def delete(self, request, challenge):
#         if not request.user.is_authenticated:
#             return redirect('login')
   
#         try:
#             chal = Challenge.objects.get(name=challenge)
#             user_chal = UserChallenge.objects.get(user=request.user, challenge=chal)
#         except Challenge.DoesNotExist:
#             return JsonResponse({'message': 'Challenge not found', 'status': '404'})
#         except UserChallenge.DoesNotExist:
#             return JsonResponse({'message': 'User has not started this challenge', 'status': '404'})
            
#         try:
#             # Stop the container
#             command = f"docker stop {user_chal.container_id}"
#             process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
#             output, error = process.communicate()
            
#             # Update the user challenge
#             user_chal.is_live = False
#             user_chal.save()
            
#             return JsonResponse({'message': 'success', 'status': '200'})
#         except Exception as e:
#             return JsonResponse({'message': f'Error: {str(e)}', 'status': '500'})
   
#     def put(self, request, challenge):  # Fixed parameter name from 'challange' to 'challenge'
#         # TODO : implement flag checking
#         return JsonResponse({'message': 'not implemented', 'status': '501'})


