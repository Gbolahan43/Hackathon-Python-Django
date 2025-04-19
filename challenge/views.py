from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import subprocess
from .utility import get_free_port
from .models import Challenge, UserChallenge
from django.core.exceptions import ObjectDoesNotExist


class DoItFast(View):

    def get(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return render(request, 'chal-not-found.html')

        user_chal = UserChallenge.objects.filter(user=request.user, challenge=chal).first()
        return render(request, 'challenge.html', {'chal': chal, 'user_chal': user_chal})

    def post(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            chal = Challenge.objects.get(name=challenge)
        except Challenge.DoesNotExist:
            return render(request, 'chal-not-found.html')

        user_chal = UserChallenge.objects.filter(user=request.user, challenge=chal).first()

        if user_chal and user_chal.is_live:
            return JsonResponse({'message': 'already running', 'status': '200', 'endpoint': f'http://localhost:{user_chal.port}'})

        port = get_free_port(8000, 8100)
        if port is None:
            return JsonResponse({'message': 'failed', 'status': '500', 'endpoint': 'None'})

        # Run the Docker container
        command = f"docker run -d -p {port}:{chal.docker_port} {chal.docker_image}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        output, _ = process.communicate()
        container_id = output.decode('utf-8').strip()

        # Update or create UserChallenge
        if user_chal:
            user_chal.container_id = container_id
            user_chal.port = port
            user_chal.is_live = True
            user_chal.save()
        else:
            user_chal = UserChallenge(
                user=request.user,
                challenge=chal,
                container_id=container_id,
                port=port,
                is_live=True
            )
            user_chal.save()

        return JsonResponse({'message': 'success', 'status': '200', 'endpoint': f'http://localhost:{port}'})

    def delete(self, request, challenge):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            chal = Challenge.objects.get(name=challenge)
            user_chal = UserChallenge.objects.get(user=request.user, challenge=chal, is_live=True)
        except (Challenge.DoesNotExist, UserChallenge.DoesNotExist):
            return JsonResponse({'message': 'failed', 'status': '500', 'error': 'Challenge or user challenge not found'})

        # Stop the Docker container
        command = f"docker stop {user_chal.container_id}"
        process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE)
        process.communicate()

        # Update the UserChallenge status
        user_chal.is_live = False
        user_chal.save()

        return JsonResponse({'message': 'success', 'status': '200'})

    def put(self, request, challenge):
        # TODO: Implement flag checking
        return JsonResponse({'message': 'not implemented', 'status': '501'})
