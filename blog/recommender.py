# This is a very simple recommender system that recommends posts based on the
# current post user is reading.

from .models import Post
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
from .context_processors import add_excerpt, add_num_comments

def next_read(post):
    current_post = Post.objects.get(id=post.id)
    posts = Post.objects.filter(is_public=True).exclude(id=current_post.id)
    
    # Our method is very simple. First we compare the bodies of the posts to
    # find the similarity between them. Then we sort the posts based on their
    # similarity and return the post with the highest similarity.
    # 
    # If no post has similarity > 0.5, we return the post with the highest
    # number of views, preferably in the same category. If there is no post in
    # the same category, we return the post with the highest number of views
    # regardless of the category.

    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([BeautifulSoup(post.body, 'html.parser').text for post in posts])
    current_vector = vectorizer.transform([current_post.body])
    similarity = cosine_similarity(current_vector, vectors).flatten()
    similarity = np.nan_to_num(similarity)
    max_similarity = np.argmax(similarity)

    if similarity[max_similarity] > 0.5:
        post = posts[max_similarity]
        post.excerpt = add_excerpt(post)
        post.num_comments = add_num_comments(post)
        return post
    else:
        posts = posts.order_by('-views')
        if posts:
            post = posts[0]
            post.excerpt = add_excerpt(post)
            post.num_comments = add_num_comments(post)
            return post
        else:
            return None
