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
- [X] `POST /api/groups/` - Create group
- [X] `GET /api/groups/` - Get all groups of current user
- [X] `GET /api/groups/{group_id}` - Get full group info
- [X] `PATCH /api/groups/{group_id}` - Update group info
- [X] `DELETE /api/groups/{group_id}` - Delete group
- [X] `GET /api/groups/{group_id}/owner` - Get group owner

### Graphs
- [X] `GET /api/groups/{group_id}/graphs` - Get group graphs
- [X] `POST /api/groups/{group_id}/graphs` - Add group graph

### Providers
- [X] `GET /api/groups/{group_id}/providers` - Get group providers
- [X] `POST /api/groups/{group_id}/providers` - Add group provider

### Prompts
- [X] `GET /api/groups/{group_id}/prompts` - Get group prompts
- [X] `POST /api/groups/{group_id}/prompts` - Add group prompt

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
- [X] `POST /api/providers/{provider_id}/test_connection` - Test connection to provider

### Models
- [X] `POST /api/providers/{provider_id}/models` - Add model to provider
- [X] `GET /api/providers/{provider_id}/models` - Get all models of provider
- [X] `GET /api/providers/{provider_id}/models/{model_id}` - Get model info
- [X] `PUT /api/providers/{provider_id}/models/{model_id}` - Update model
- [X] `DELETE /api/providers/{provider_id}/models/{model_id}` - Delete model from provider

### Provider tokens
- [X] `PUT /api/providers/{provider_id}/tokens` - Add or update provider token
- [X] `DELETE /api/providers/{provider_id}/tokens` - Delete provider token

## Prompts
- [X] `POST /api/prompts` - Add prompt
- [X] `GET /api/prompts` - Get all prompts
- [X] `GET /api/prompts/{prompt_id}` - Get prompt info
- [X] `DELETE /api/prompts/{prompt_id}` - Delete prompt
- [X] `PUT /api/prompts/{prompt_id}` - Update prompt

## Graphs
- [X] `POST /api/graphs` - Add graph
- [X] `GET /api/graphs` - Get all graphs
- [X] `GET /api/graphs/{graph_id}` - Get graph info
- [X] `DELETE /api/graphs/{graph_id}` - Delete graph
- [X] `PUT /api/graphs/{graph_id}` - Update graph

### Agents
- [X] `GET /api/graphs/{graph_id}/agents` - Get all agents of graph
- [X] `POST /api/graphs/{graph_id}/agents/hard_code` - Add hard-coded agent to graph
- [X] `POST /api/graphs/{graph_id}/agents/ai` - Add AI agent to graph
- [X] `POST /api/graphs/{graph_id}/agents/chat` - Add chat agent to graph
- [X] `POST /api/graphs/{graph_id}/agents/critic` - Add critic agent to graph
- [X] `GET /api/graphs/{graph_id}/agents/{agent_id}` - Get agent info
- [X] `DELETE /api/graphs/{graph_id}/agents/{agent_id}` - Delete agent from graph
- [X] `PUT /api/graphs/{graph_id}/agents/{agent_id}` - Update agent

### Nodes
- [X] `GET /api/graphs/{graph_id}/nodes` - Get all nodes of graph
- [X] `GET /api/graphs/{graph_id}/nodes/{node_id}` - Get node info
- [X] `PUT /api/graphs/{graph_id}/nodes/{node_id}` - Update node coordinates


### Settings
- [X] `GET /api/graphs/{graph_id}/available_settings` - Get all available settings in current context
