---
id: cfe68ad40bb01c49
source: "google-auth-oauth-libraries.md"
"title: Google Authentication & OAuth Libraries"
category: google-api
skillTags: ["tool", "code"]
containmentHash: d1497c67ab9aabf4b9af
createdAt: 1786051355705
embeddingSig: "android:your:modules|compile:google:android|exclude:group:google|google:android:your|google:sign:this|group:google:android|modules:compile:google|native:google:sign|react:native:google|sign:this:exclude|this:exclude:group|your:modules:compile"
---
ct(":react-native-google-sign-in")) { // ADD this
        exclude group: "com.google.android.gms"
    } 
    ...your modules...
    compile "com.google.android.gms:play-services-auth:10.0.1" // Add this, not 9.8.0 (from instructions).
    compile "com.facebook.react:react-native:+"
}
apply plugin: "com.google.gms.google-services" // Add this after dependencies.
```