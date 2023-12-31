# AllSky AI Module

|             |                      |
|-------------|----------------------|
| **Status**  | Experimental         |
| **Level**   | Beginner             |
| **Runs In** | Day time, Night time |

This module allows for AllSky to classify the current sky conditions based on Machine Learning.
More info can be found at [allskyai.com](https://www.allskyai.com) I try to keep this free for everyone as long as my server can handle it!

The module contains the following options

| Setting     | Description                                                                   |
|-------------|-------------------------------------------------------------------------------|
| Camera Type | RGB or MONO                                                                   |
| Auto Update | Automatically download new version if exists                                  |
| Contribute  | Submit an image every 10 min to improve the general model for everyone        |
| AllSkyAI    | Input your account details to be able to build a custom model for your AllSky |

## Accessible Variables

```json
{ 'AI_CLASSIFICATION': 'heavy_clouds', 
  'AI_CONFIDENCE': 99.693,
  'AI_INFERENCE': 0.219,
  'AI_UTC': 1693768336}
}
```

### Release info
### V.1.0.4
* BRG to RGB while reading from `s.image`

### V.1.0.3
* Fixed Header data when uploading image
* If an invalid version of the `version.txt` is present, download the content again

### V.1.0.2
* Fixed online/server version check for downloading models
* If no model exists, don't write any data to extraData

### V.1.0.1
* Added contribute ability. If this is checked you can anonymously submit an image every 10 min to help improve the general model for everyone.
* Connect you AllSkyAI account. If you have a registered account you can upload and classify you images to build a custom model to your AllSky. This model will be downloaded and updated automatically once trained.

### V.1.0.0
* Trained on ~31.000 curated images
