# API Documentation

## Auth
- [X] `POST /api/auth/login` - Login user and get auth token
- [X] `POST /api/auth/logout` - Logout user and invalidate auth token
- [X] `POST /api/auth/register` - Register user

## User
- [X] `GET /api/users/me` - Get user info
- [X] `PATCH /api/users/me` - Update user info
- [X] `PATCH /api/users/me/password` - Update user password
- [X] `GET /api/users/search` - Search users by login
- [X] `GET /api/users/{user_id}` - Get user info
- [X] `GET /api/users/{user_id}/groups` - Get user groups

## Group
- [X] `POST /api/groups/create` - Create group
- [X] `GET /api/groups/{group_id}` - Get full group info
- [X] `PATCH /api/groups/{group_id}` - Update group info
- [X] `DELETE /api/groups/{group_id}` - Delete group
- [X] `GET /api/groups/{group_id}/owner` - Get group owner
- [X] `GET /api/groups/{group_id}/graphs` - Get group graphs
- [ ] `POST /api/groups/{group_id}/graphs` - Add group graph
- [ ] `GET /api/groups/{group_id}/providers` - Get group providers
- [ ] `POST /api/groups/{group_id}/providers` - Add group provider
- [ ] `GET /api/groups/{group_id}/prompts` - Get group prompts
- [ ] `POST /api/groups/{group_id}/prompts` - Add group prompt

### Members
- [X] `GET /api/groups/{group_id}/members` - Get group members
- [X] `POST /api/groups/{group_id}/members` - Add group member
- [X] `POST /api/groups/{group_id}/members/leave` - Leave group
- [X] `GET /api/groups/{group_id}/members/{user_id}` - Get group member info
- [X] `PATCH /api/groups/{group_id}/members/{user_id}` - Update group member info
- [X] `DELETE /api/groups/{group_id}/members/{user_id}` - Delete group member

## Providers
- [X] `POST /api/providers` - Add provider
- [X] `GET /api/providers` - Get all providers available for current user
- [X] `GET /api/providers/{provider_id}` - Get provider info
- [X] `PUT /api/providers/{provider_id}` - Update provider
- [X] `DELETE /api/providers/{provider_id}` - Delete provider

## Prompts
- [ ] `POST /api/prompts` - Add prompt
- [ ] `GET /api/prompts` - Get all prompts
- [ ] `GET /api/prompts/{prompt_id}` - Get prompt info
- [ ] `DELETE /api/prompts/{prompt_id}` - Delete prompt
- [ ] `PUT /api/prompts/{prompt_id}` - Update prompt
