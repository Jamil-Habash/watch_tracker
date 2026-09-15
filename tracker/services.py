"""
AI Recommendation Service

Integrates:
- Groq AI (free fast inference) for generating personalized recommendations
- TMDB API (free movie/TV database) for fetching title data
"""
import os
import json
import requests
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache


# ─── Configuration ──────────────────────────────────────────────────────
GROQ_API_KEY = getattr(settings, 'GROQ_API_KEY', '') or os.environ.get('GROQ_API_KEY', '')
GROQ_API_URL = getattr(settings, 'GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
GROQ_MODEL = getattr(settings, 'GROQ_MODEL', 'llama-3.3-70b-versatile')

TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', '') or os.environ.get('TMDB_API_KEY', '')
TMDB_API_URL = getattr(settings, 'TMDB_API_URL', 'https://api.themoviedb.org/3')
TMDB_IMAGE_BASE = getattr(settings, 'TMDB_IMAGE_BASE', 'https://image.tmdb.org/t/p/w500')

CACHE_TIMEOUT = getattr(settings, 'RECOMMEND_CACHE_TIMEOUT', 300)


# ─── Helper Functions ───────────────────────────────────────────────────
def _groq_request(messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 1500) -> Optional[str]:
    """Call Groq AI API (OpenAI-compatible)."""
    if not GROQ_API_KEY:
        return None
    
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'model': GROQ_MODEL,
        'messages': messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
    }
    
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Groq API error: {e}")
        return None


def _tmdb_request(endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
    """Call TMDB API."""
    if not TMDB_API_KEY:
        return None
    
    if params is None:
        params = {}
    params['api_key'] = TMDB_API_KEY
    params['language'] = 'en-US'
    
    try:
        resp = requests.get(f"{TMDB_API_URL}{endpoint}", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"TMDB API error: {e}")
        return None


# ─── TMDB Search Functions ──────────────────────────────────────────────
def search_movies(query: str, page: int = 1) -> List[Dict]:
    """Search for movies on TMDB."""
    cache_key = f"tmdb_movie_search:{query}:{page}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    data = _tmdb_request('/search/movie', {'query': query, 'page': page, 'include_adult': False})
    if not data or not data.get('results'):
        return []
    
    results = []
    for item in data['results'][:10]:
        results.append({
            'id': item['id'],
            'title': item.get('title') or item.get('name'),
            'year': (item.get('release_date') or '')[:4] if item.get('release_date') else None,
            'overview': item.get('overview', ''),
            'rating': item.get('vote_average'),
            'poster': f"{TMDB_IMAGE_BASE}{item['poster_path']}" if item.get('poster_path') else None,
            'type': 'movie',
            'imdb_id': item.get('imdb_id') or get_imdb_id('movie', item['id']),
        })
    
    cache.set(cache_key, results, CACHE_TIMEOUT)
    return results


def search_tv(query: str, page: int = 1) -> List[Dict]:
    """Search for TV shows on TMDB."""
    cache_key = f"tmdb_tv_search:{query}:{page}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    data = _tmdb_request('/search/tv', {'query': query, 'page': page, 'include_adult': False})
    if not data or not data.get('results'):
        return []
    
    results = []
    for item in data['results'][:10]:
        results.append({
            'id': item['id'],
            'title': item.get('name'),
            'year': (item.get('first_air_date') or '')[:4] if item.get('first_air_date') else None,
            'overview': item.get('overview', ''),
            'rating': item.get('vote_average'),
            'poster': f"{TMDB_IMAGE_BASE}{item['poster_path']}" if item.get('poster_path') else None,
            'type': 'tv',
            'imdb_id': item.get('imdb_id') or get_imdb_id('tv', item['id']),
        })
    
    cache.set(cache_key, results, CACHE_TIMEOUT)
    return results


def get_imdb_id(media_type: str, tmdb_id: int) -> Optional[str]:
    """Fetch IMDb ID for a title via TMDB external_ids."""
    cache_key = f"imdb_id:{media_type}:{tmdb_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    endpoint = f'/{media_type}/{tmdb_id}/external_ids'
    data = _tmdb_request(endpoint)
    if data and data.get('imdb_id'):
        cache.set(cache_key, data['imdb_id'], CACHE_TIMEOUT * 10)
        return data['imdb_id']
    return None


def get_trending(media_type: str = 'all', time_window: str = 'week') -> List[Dict]:
    """Get trending movies/TV from TMDB."""
    cache_key = f"tmdb_trending:{media_type}:{time_window}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    data = _tmdb_request(f'/trending/{media_type}/{time_window}')
    if not data or not data.get('results'):
        return []
    
    results = []
    for item in data['results'][:15]:
        mtype = item.get('media_type', media_type)
        if mtype not in ('movie', 'tv'):
            continue
        
        results.append({
            'id': item['id'],
            'title': item.get('title') or item.get('name'),
            'year': (item.get('release_date') or item.get('first_air_date') or '')[:4],
            'overview': item.get('overview', ''),
            'rating': item.get('vote_average'),
            'poster': f"{TMDB_IMAGE_BASE}{item['poster_path']}" if item.get('poster_path') else None,
            'type': mtype,
            'imdb_id': item.get('imdb_id') or get_imdb_id(mtype, item['id']),
        })
    
    cache.set(cache_key, results, CACHE_TIMEOUT)
    return results


def get_movie_details(tmdb_id: int) -> Optional[Dict]:
    """Get detailed movie info from TMDB."""
    cache_key = f"tmdb_movie_details:{tmdb_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    data = _tmdb_request(f'/movie/{tmdb_id}', {'append_to_response': 'credits,videos,external_ids'})
    if data:
        cache.set(cache_key, data, CACHE_TIMEOUT * 10)
    return data


def get_tv_details(tmdb_id: int) -> Optional[Dict]:
    """Get detailed TV show info from TMDB."""
    cache_key = f"tmdb_tv_details:{tmdb_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    data = _tmdb_request(f'/tv/{tmdb_id}', {'append_to_response': 'credits,videos,external_ids'})
    if data:
        cache.set(cache_key, data, CACHE_TIMEOUT * 10)
    return data


# ─── AI Recommendation Functions ────────────────────────────────────────
def build_user_profile(entries: List[Dict]) -> str:
    """Build a text summary of user's watch history for the AI."""
    if not entries:
        return "User has no watch history yet."
    
    by_type = {'movie': [], 'tv': [], 'anime': []}
    for e in entries:
        by_type[e['type']].append(e)
    
    parts = []
    for mtype, items in by_type.items():
        if not items:
            continue
        type_name = {'movie': 'Movies', 'tv': 'TV Series', 'anime': 'Anime'}[mtype]
        parts.append(f"\n{type_name} ({len(items)}):")
        
        # Top rated
        rated = sorted([i for i in items if i.get('rating')], key=lambda x: x['rating'], reverse=True)[:5]
        if rated:
            parts.append("  Favorites: " + ", ".join(f"{i['title']} ({i['year']}) ★{i['rating']}" for i in rated))
        
        # Recently watched
        recent = sorted([i for i in items if i.get('dateWatched')], key=lambda x: x['dateWatched'], reverse=True)[:5]
        if recent:
            parts.append("  Recent: " + ", ".join(f"{i['title']} ({i['year']})" for i in recent))
        
        # Status breakdown
        statuses = {}
        for i in items:
            statuses[i['status']] = statuses.get(i['status'], 0) + 1
        parts.append("  Status: " + ", ".join(f"{k}: {v}" for k, v in statuses.items()))
    
    return "\n".join(parts)


def build_recommendation_prompt(user_message: str, user_profile: str) -> List[Dict[str, str]]:
    """Build the system + user prompt for Grok."""
    system_prompt = """You are a knowledgeable TV & movie recommendation assistant. 
You have access to a movie/TV database (TMDB) and the user's watch history.

Your task: Generate 5-8 personalized recommendations based on the user's request and their watch history.

For EACH recommendation, you MUST provide:
- Title
- Year
- Type (movie/tv)
- Brief reason (1-2 sentences) why it matches their request
- Genre tags (2-3)

Return ONLY valid JSON in this exact format:
{
  "recommendations": [
    {"title": "...", "year": 2023, "type": "movie", "reason": "...", "genres": ["Sci-Fi", "Thriller"]},
    ...
  ],
  "message": "A brief conversational response to the user."
}

Rules:
- Prioritize titles the user hasn't watched (check their history)
- Match the user's mood/request (genre, tone, similar vibes)
- Include mix of popular and hidden gems
- If user asks for something specific (e.g., "80s sci-fi"), filter accordingly
- Keep reasons personal and specific to their history"""
    
    user_prompt = f"""User's watch history:
{user_profile}

User's request: "{user_message}"

Generate personalized recommendations as JSON."""
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def enrich_recommendations_with_tmdb(ai_recs: List[Dict]) -> List[Dict]:
    """Enrich AI recommendations with TMDB data (posters, ratings, IMDb IDs)."""
    enriched = []
    
    for rec in ai_recs:
        query = f"{rec['title']} {rec['year'] or ''}"
        search_func = search_tv if rec.get('type') == 'tv' else search_movies
        results = search_func(query)
        
        match = None
        for r in results:
            if r['title'].lower() == rec['title'].lower() and (not rec.get('year') or r['year'] == str(rec['year'])):
                match = r
                break
        
        if not match and results:
            match = results[0]
        
        if match:
            enriched.append({
                'title': match['title'],
                'year': match['year'],
                'type': match['type'],
                'reason': rec.get('reason', ''),
                'genres': rec.get('genres', []),
                'rating': match.get('rating'),
                'overview': match.get('overview', ''),
                'poster': match.get('poster'),
                'imdb_id': match.get('imdb_id'),
                'tmdb_id': match['id'],
            })
        else:
            # Fallback: keep AI data without TMDB enrichment
            enriched.append({
                'title': rec['title'],
                'year': rec.get('year'),
                'type': rec.get('type', 'movie'),
                'reason': rec.get('reason', ''),
                'genres': rec.get('genres', []),
                'rating': None,
                'overview': '',
                'poster': None,
                'imdb_id': None,
                'tmdb_id': None,
            })
    
    return enriched


def get_ai_recommendations(user_message: str, user_entries: List[Dict]) -> Dict[str, Any]:
    """
    Main function: Get AI-powered recommendations for the user.
    Returns dict with 'recommendations' list and 'message' string.
    """
    user_profile = build_user_profile(user_entries)
    messages = build_recommendation_prompt(user_message, user_profile)
    
    ai_response = _groq_request(messages, temperature=0.8, max_tokens=2000)
    if not ai_response:
        return {
            'recommendations': [],
            'message': "I couldn't connect to the AI service. Please check your API configuration.",
            'error': 'groq_unavailable'
        }
    
    try:
        # Extract JSON from response (AI might wrap in code blocks)
        json_str = ai_response
        if '```json' in json_str:
            json_str = json_str.split('```json')[1].split('```')[0]
        elif '```' in json_str:
            json_str = json_str.split('```')[1].split('```')[0]
        
        parsed = json.loads(json_str.strip())
        ai_recs = parsed.get('recommendations', [])
        ai_message = parsed.get('message', 'Here are some recommendations for you!')
        
        # Enrich with TMDB data
        enriched = enrich_recommendations_with_tmdb(ai_recs)
        
        return {
            'recommendations': enriched,
            'message': ai_message,
        }
    except json.JSONDecodeError as e:
        print(f"Failed to parse AI response: {e}")
        print(f"Raw response: {ai_response}")
        return {
            'recommendations': [],
            'message': "I had trouble parsing the recommendations. Please try again.",
            'error': 'parse_error'
        }


def get_fallback_recommendations(user_entries: List[Dict], limit: int = 8) -> List[Dict]:
    """Fallback: Get trending titles when AI is unavailable."""
    trending = get_trending('all', 'week')
    
    # Filter out already watched
    watched_titles = {e['title'].lower() for e in user_entries}
    filtered = [t for t in trending if t['title'].lower() not in watched_titles]
    
    return filtered[:limit]