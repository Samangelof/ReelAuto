# check_fetcher.py
import os
import django


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.base')

django.setup()


from apps.core.services.reels_fetcher import ReelsFetcher
from datetime import date


fetcher = ReelsFetcher()

results = fetcher.fetch_by_hashtag(
    hashtag="travel",
    min_views=0,
    min_likes=0,
    min_comments=0,
    date_from=None,
    date_to=None,
    limit=5
)

for r in results:
    print("==============")
    for k, v in r.items():
        print(f"{k}: {v}")