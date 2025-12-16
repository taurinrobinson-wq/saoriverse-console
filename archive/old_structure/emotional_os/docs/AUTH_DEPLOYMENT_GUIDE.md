# Authentication System Deployment Guide

## Overview
This guide walks through deploying the complete user authentication system for Emotional OS, ensuring individual conversation privacy and data isolation while maintaining the 2.65s response performance.

## Deployment Steps

### 1. Database Setup

1. **Open Supabase SQL Editor**
   - Go to your Supabase project dashboard
   - Navigate to SQL Editor

2. **Run Database Schema**
   ```sql
   -- Execute the entire database_schema.sql file
   -- This creates users table, adds user_id columns, sets up RLS policies
   ```

3. **Verify Tables Created**
   - Check that `users` table exists
   - Verify indexes are created
   - Confirm RLS policies are enabled

### 2. Deploy Authentication Edge Function

1. **Navigate to Edge Functions**
   ```bash
   cd your-supabase-project/supabase/functions
   ```

2. **Create auth-manager directory**
   ```bash
   mkdir auth-manager
   ```

3. **Copy auth_edge_function.ts**
   ```bash
   # Copy the auth_edge_function.ts content to:
   # supabase/functions/auth-manager/index.ts
   ```

4. **Deploy the function**
   ```bash
   supabase functions deploy auth-manager
   ```

### 3. Deploy Authenticated Processing Edge Function

1. **Create authenticated-saori directory**
   ```bash
   mkdir authenticated-saori
   ```

2. **Copy authenticated_edge_function.ts**
   ```bash
   # Copy the authenticated_edge_function.ts content to:
   # supabase/functions/authenticated-saori/index.ts
   ```

3. **Deploy the function**
   ```bash
   supabase functions deploy authenticated-saori
   ```

### 4. Update Streamlit Application

1. **Replace main UI file**
   ```bash
   # Backup current emotional_os_ui.py (ARCHIVED)
   cp emotional_os_ui.py (ARCHIVED) emotional_os_ui_backup.py

   # Replace with authenticated version
   cp authenticated_emotional_os_ui.py emotional_os_ui.py (ARCHIVED)
   ```

2. **Update Streamlit secrets**
   ```toml
   # Add to .streamlit/secrets.toml
   [supabase]
   url = "your-supabase-url"
   key = "your-supabase-anon-key"
   auth_function_url = "https://your-project.supabase.co/functions/v1/auth-manager"
   saori_function_url = "https://your-project.supabase.co/functions/v1/authenticated-saori"
   ```

### 5. Test Authentication Flow

1. **Test Registration**
   - Open Streamlit app
   - Navigate to registration tab
   - Create test user account
   - Verify user appears in database

2. **Test Login**
   - Log in with test credentials
   - Verify session is created
   - Check conversation isolation

3. **Test Data Isolation**
   - Create conversations as User A
   - Log out and log in as User B
   - Verify User B cannot see User A's data

### 6. Performance Validation

1. **Response Time Check**
   ```bash
   # Test authenticated endpoint response time
   curl -w "@curl-format.txt" -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer USER_SESSION_TOKEN" \
     -d '{"message": "Test message", "user_id": "USER_UUID"}' \
     https://your-project.supabase.co/functions/v1/authenticated-saori
   ```

2. **Expected Performance**
   - Response time: ~2.65s (same as optimized version)
   - Memory usage: Similar to non-authenticated version
   - User isolation: Complete separation of data

## Configuration Details

### Environment Variables

```env

# Required for edge functions
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-key
```




### Supabase Function URLs

```
Authentication: https://your-project.supabase.co/functions/v1/auth-manager
Processing: https://your-project.supabase.co/functions/v1/authenticated-saori
```




### Security Headers

```typescript
// Required CORS headers for Streamlit integration
'Access-Control-Allow-Origin': '*'
'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE'
```




## Security Features

### Password Security
- **PBKDF2 Hashing**: 100,000 iterations with random salt
- **Salt Storage**: Unique salt per user stored separately
- **Session Management**: 480-minute timeout with automatic renewal

### Data Isolation
- **Row Level Security**: Database-enforced user data separation
- **User-specific Caches**: Isolated processing memory
- **Private Learning**: Individual vocabulary building per user

### Rate Limiting
- **Login Attempts**: 5 attempts per 15-minute window
- **Session Validation**: Token-based authentication
- **Automatic Lockout**: Temporary account suspension

## Migration Strategy

### From Anonymous to Authenticated

1. **Backup Existing Data**
   ```sql
   -- Export current anonymous data
   SELECT * FROM emotional_tags WHERE user_id IS NULL;
   SELECT * FROM glyphs WHERE user_id IS NULL;
   ```

2. **Preserve Global Data**
   - Keep global emotional tags (user_id = NULL)
   - Maintain shared glyph definitions
   - Preserve system learning patterns

3. **User Data Migration**
   ```sql
   -- Option: Assign existing data to admin user
   UPDATE glyphs SET user_id = 'admin-uuid' WHERE user_id IS NULL;
   UPDATE glyph_logs SET user_id = 'admin-uuid' WHERE user_id IS NULL;
   ```

## Troubleshooting

### Common Issues

1. **Function Deployment Fails**
   ```bash
   # Check function logs
   supabase functions logs auth-manager
   supabase functions logs authenticated-saori
   ```

2. **Database Permission Errors**
   ```sql
   -- Verify RLS policies
   SELECT * FROM pg_policies WHERE tablename = 'users';
   ```

3. **Session Authentication Issues**
   - Check JWT token format
   - Verify user_id in session
   - Confirm function CORS settings

### Performance Monitoring

1. **Response Time Tracking**
   ```javascript
   // Add timing logs to edge functions
   const startTime = Date.now();
   // ... processing ...
   console.log(`Response time: ${Date.now() - startTime}ms`);
   ```

2. **Memory Usage**
   ```javascript
   // Monitor cache sizes
   console.log(`Cache entries: ${Object.keys(cache).length}`);
   ```

## Post-Deployment Checklist

- [ ] Database schema deployed successfully
- [ ] Users table created with proper indexes
- [ ] RLS policies enabled and tested
- [ ] Auth edge function deployed and responsive
- [ ] Authenticated processing function deployed
- [ ] Streamlit app updated to authenticated version
- [ ] User registration working
- [ ] Login/logout functionality tested
- [ ] Data isolation verified between users
- [ ] Response times maintained at ~2.65s
- [ ] Session management working properly
- [ ] Rate limiting functioning correctly
- [ ] Privacy settings accessible to users
- [ ] Data export feature operational

## Next Steps

1. **User Onboarding**: Create user guide for registration/login
2. **Admin Dashboard**: Build admin interface for user management
3. **Analytics**: Add user engagement and system performance tracking
4. **Mobile Support**: Optimize authentication for mobile devices
5. **Social Features**: Consider user-to-user interaction features (optional)

Your authentication system is now ready for deployment! This maintains the 2.65s performance while adding complete user privacy and data isolation.
