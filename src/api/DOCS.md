# API Documentation

## User
`POST /api/users/login` - Login user and get auth token
`POST /api/users/logout` - Logout user and invalidate auth token
`POST /api/users/register` - Register user
`GET /api/users/me` - Get user info
`PATCH /api/users/me` - Update user info
`PATCH /api/users/me/password` - Update user password
`GET /api/users/search` - Search users by login
`GET /api/users/{user_id}` - Get user info
`GET /api/users/{user_id}/groups` - Get user groups

## Group
`POST /api/groups/create` - Create group
`GET /api/groups` - Get all groups 
`GET /api/groups/{group_id}` - Get full group info
``
