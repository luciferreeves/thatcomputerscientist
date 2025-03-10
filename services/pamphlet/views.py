from django.http import HttpResponse
import os
import random
from collections import deque
import threading


class ImageRotator:
    def __init__(self):
        self.image_queues = {}
        self.lock = threading.Lock()

    def get_random_image(self, style):
        with self.lock:
            # Initialize or refresh queue if empty
            if style not in self.image_queues or not self.image_queues[style]:
                path = f"static/images/fakeads/{style}"
                files = [f for f in os.listdir(path) if f.endswith(".gif")]
                random.shuffle(files)
                self.image_queues[style] = deque(files)

            # Get next image and rotate to end of queue
            image = self.image_queues[style].popleft()
            self.image_queues[style].append(image)
            return image


rotator = ImageRotator()


def new_pamphlet(request):
    """Main view function to serve pamphlets."""
    style = request.GET.get("style", "banner")
    seed = request.GET.get("seed", "")

    if style not in ["banner", "big", "button"]:
        style = "banner"

    if style == "button":
        style = "buttons"  # One-off correction for migration of folder

    path = f"static/images/fakeads/{style}"

    try:
        files = [f for f in os.listdir(path) if f.endswith(".gif")]
        if not files:
            return HttpResponse(status=404)

        random.seed(seed)
        chosen_file = random.choice(files)
        random.seed()

        file_path = os.path.join(path, chosen_file)

        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/gif")
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

    except Exception as e:
        print(f"Error while serving pamphlet: {str(e)}")
        return HttpResponse(status=404)
