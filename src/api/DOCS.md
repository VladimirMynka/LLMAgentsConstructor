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
`GET /api/groups/{group_id}` - Get full group info
`GET /api/groups/{group_id}/owner` - Get group owner
`POST /api/groups/{group_id}/leave` - Leave group
`GET /api/groups/{group_id}/members` - Get group members
`GET /api/groups/{group_id}/members/{user_id}` - Get group member info
`PATCH /api/groups/{group_id}/members/{user_id}` - Update group member info
`DELETE /api/groups/{group_id}/members/{user_id}` - Delete group member
`POST /api/groups/{group_id}/members` - Add group member
`GET /api/groups/{group_id}/graphs` - Get group graphs
`PATCH /api/groups/{group_id}` - Update group info
`DELETE /api/groups/{group_id}` - Delete group
