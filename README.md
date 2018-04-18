# xcataloger
CLI tool for Images.xcassets

![](https://github.com/skanmera/media/blob/master/xcataloger/screenshot.png)

# Description
___`xcataloger`___ is CLI tool for creating AppIcons/LaunchImages and registering them to Images.xcassets.

# Install

### Clone

```
$ git clone https://github.com/skanmera/xcataloger.git
```

### Dependencies

```
$ cd xcataloger
$ pip install pillow
```

# Usage

## Make

___Make command make dummy images.___

```
usage: xcataloger.py make [-h] -c CONFIG [-o OUTPUT] [-C COLOR] [-l LOGO]
                          [--logo-color LOGO_COLOR]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify json from /config/xc[Xcode Version]/
  -o OUTPUT, --output OUTPUT
                        output directory.
                        default: ./images/
  -C COLOR, --color COLOR
                        specify color with format R,G,B ex: --color=255,255,255
  -l LOGO, --logo LOGO  draw logo on center of image
  --logo-color LOGO_COLOR
                        specify color of logo with format R,G,B
                        ex: --logo-color=0,0,0
```

### example:
```
$ python xcataloger.py make --config=config/xc9.3/ios-launch-image.json --color=0,0,255 -logo=SAMPLE --logo-color=255,255,255
```

## Convert

___Convert command convert to each size image from source image.___

```
usage: xcataloger.py convert [-h] -s SRC -c CONFIG [-O ORIENTATION]
                             [-r ROTATE] [-o OUTPUT] [-i]

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     specify source image
  -c CONFIG, --config CONFIG
                        specify json from /config/xc[Xcode Version]/
  -O ORIENTATION, --orientation ORIENTATION
                        specify src image orientation
                        ex: --orientation=landscape
                        default: portrait
  -r ROTATE, --rotate ROTATE
                        specify rotation
                        require: --orientation
                        ex: --rotate=left or --rotate==right
                        default: None
  -o OUTPUT, --output OUTPUT
                        output directory.
                        default: ./images/
  -i, --ignore-aspect-ratio
                        ignore aspect ratio
```

### example:
```
$ python xcataloger.py convert --src=source.png --config=config/xc9.3/ios-launch-image.json
```

## Register

___Register command copy images to Images.xcassets(AppIcons.appiconset/LaunchImage.launchimage) from source directory and overwrite 'filename' in Contents.json.___

```
usage: xcataloger.py register [-h] -s SRC_DIR -i IMAGE_ASSETS -c CONFIG [-n]
                              [-f FORMAT] [-k]

optional arguments:
  -h, --help            show this help message and exit
  -s SRC_DIR, --src-dir SRC_DIR
                        specify directory contains images to register to Images.xcassets
  -i IMAGE_ASSETS, --image-assets IMAGE_ASSETS
                        specify directory contains "Contents.json"
  -c CONFIG, --config CONFIG
                        specify json from /config/xc[Xcode Version]/
  -n, --no-rename       copy and register to Images.xcassets without rename
  -f FORMAT, --format FORMAT
                        specify file name format
                        ex: --format=<idiom>_<orientation>_<width>x<height>.png
                            --> iphone_portrait_640x960.png
                        available: idiom, orientation, subtype, minimum-system-version,, extent, scale, width, height
  -k, --keep            keep old files

```

### example:
```
$ python xcataloger.py register --src-dir=source --image-assets=path/to/Images.xcassets/LaunchImage.launchimage --config=config/xc9.3/ios-launch-image.json
```

# License
[MIT](https://github.com/skanmera/xcataloger/blob/master/LICENSE)
