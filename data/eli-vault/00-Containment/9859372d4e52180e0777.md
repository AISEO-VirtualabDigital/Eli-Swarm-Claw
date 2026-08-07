---
id: d8d0e3d31aea6a6d
source: "google-api-client-libraries.md"
"title: Google API Client Libraries — Reference"
category: google-api
skillTags: ["tool", "code"]
containmentHash: 9859372d4e52180e0777
createdAt: 1786051355693
embeddingSig: "3213900:blog:details|auth:your:const|blog:details:blogger|blogger:blogs:params|blogger:version:auth|blogid:3213900:blog|blogs:params:console|const:params:blogid|details:blogger:blogs|params:blogid:3213900|version:auth:your|your:const:params"
---
blogger({
  version: 'v3',
  auth: 'YOUR API KEY'
});
const params = {
  blogId: '3213900'
};

// get the blog details
blogger.blogs.get(params, (err, res) => {
  if (err) {
    console.error(err);
    throw err;
  }
  console.log(`The
---
## LindaLawton/Google-Dotnet-Samples ⭐247

**URL**: https://github.com/LindaLawton/Google-Dotnet-Samples
**Language**: N/A