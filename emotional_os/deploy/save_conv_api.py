from fastapi import APIRouter, Request, HTTPException
import os
import requests
import json
import tomllib

router = APIRouter()


def _load_service_role_key():
    # Prefer environment variable
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SERVICE_ROLE_KEY')
    if key:
        return key
    # Try loading from .streamlit/secrets.toml if present
    try:
        p = os.path.join(os.getcwd(), '.streamlit', 'secrets.toml')
        if os.path.exists(p):
            with open(p, 'rb') as fh:
                data = tomllib.load(fh)
                sup = data.get('supabase', {})
                return sup.get('service_role_key') or sup.get('service_role') or sup.get('service_role_key')
    except Exception:
        pass
    return None


@router.post('/api/save_conversation')
async def save_conversation(request: Request):
    body = await request.json()
    auth_header = request.headers.get('Authorization', '')

    # Validate session token using FirstPersonAuth if available
    try:
        from emotional_os.deploy.fastapi_app import FirstPersonAuth, SUPABASE_URL
    except Exception:
        raise HTTPException(status_code=500, detail='Server misconfiguration')

    token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header
    validation = FirstPersonAuth.validate_session_token(token)
    if not validation.get('valid'):
        raise HTTPException(status_code=401, detail='Invalid session')

    user_id = validation.get('data', {}).get('user_id') or body.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail='Missing user_id')

    service_key = _load_service_role_key()
    if not service_key:
        raise HTTPException(status_code=503, detail='Supabase service role key not configured on server')

    supabase_url = os.environ.get('SUPABASE_URL')
    if not supabase_url:
        # Try to import from fastapi_app
        try:
            supabase_url = SUPABASE_URL
        except Exception:
            pass
    if not supabase_url:
        raise HTTPException(status_code=500, detail='Supabase URL not configured')

    # Build payload and upsert
    conv = {
        'conversation_id': body.get('conversation_id'),
        'user_id': user_id,
        'title': body.get('title'),
        'messages': body.get('messages') or [],
        'metadata': body.get('metadata') or {}
    }

    url = supabase_url.rstrip('/') + '/rest/v1/conversations'
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }
    try:
        r = requests.post(url, headers=headers, json=[conv], timeout=10)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f'Failed to reach Supabase: {e}')

    if r.status_code not in (200, 201, 204):
        raise HTTPException(status_code=502, detail=f'Supabase responded: {r.status_code} {r.text}')

    return {'success': True}
