# fluffy-fiesta

This repository includes a Python tool to convert between iOS **Live Photos** and Android **Motion Photos**.

```
python dynamic_photo_converter.py ios2android <image.jpg> <video.mov> <output.jpg>
```

creates an Android Motion Photo from the pair of JPEG and MOV files. The script calls `ffmpeg`, so make sure it is installed.

```
python dynamic_photo_converter.py android2ios <motion_photo.jpg> <output_basename>
```

extracts the embedded video and still frame from an Android Motion Photo. The output will be `<output_basename>.jpg` and `<output_basename>.mov`.

The converter tries to preserve existing image data while injecting or removing the video portion.
