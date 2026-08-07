---
id: a1ffc5ff5a80f66d
source: "google-workspace-api-tools.md"
"title: Google Workspace & Productivity API Tools"
category: google-api
skillTags: []
containmentHash: f4b9c34020e70bf59e31
createdAt: 1786051356911
embeddingSig: "create:credentials:once|create:file:server|credentials:once:that|environment:variables:google|file:server:following|following:environment:variables|google:workspace:guides|guides:create:credentials|once:that:create|server:following:environment|that:create:file|workspace:guides:create"
---
google.com/workspace/guides/create-credentials).\
Once you do that, create the file `server/.env`, and set the following environment variables:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

You also need to add the following **Authorized Redirect URI** to your OAuth 2.0 client in the [Google Cloud Console](https://console.cloud.google.com) based