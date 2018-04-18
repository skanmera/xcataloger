#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import glob
import shutil
import argparse
from PIL import Image, ImageDraw, ImageFont
import re


class ImageFileInfo:
    def __init__(self, path, width, height):
        self.path = path
        self.width = width
        self.height = height

    def equal_size(self, width, height):
        return self.width == width and self.height == height


def load_images(directory):
    for image in glob.glob(os.path.join(directory, '*.png')):
        with Image.open(image) as i:
            width, height = i.size
            yield ImageFileInfo(image, width, height)


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


def unique_path(path):
    directory = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))
    ext = '.{}'.format(ext) if ext else ''
    i = 1
    while os.path.exists(path):
        path = os.path.join(directory, '{}({}){}'.format(name, i, ext))
        i += 1
    return path


def clear_image_assets(directory, contents):
    for image in contents['images']:
        filename = image.get('filename')
        if not filename:
            continue
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        os.remove(path)
        print('Removed "{}"'.format(path))


def output_contents_json(contents, output_path):
    images = []
    result = {'images': images, 'info': contents['info']}
    keys = contents['images'][0].keys()
    for image_config in contents['images']:
        write_config = {}
        for key in keys:
            if key in image_config.keys():
                write_config[key] = image_config[key]
        images.append(write_config)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)


def build_file_name(config, format_string):
    if 'width' not in config.keys():
        config['width'] = get_width(config)
    if 'height' not in config.keys():
        config['height'] = get_height(config)
    keys = re.findall(r'<(.+?)>', format_string)
    for key in keys:
        format_string = format_string.replace('<{}>'.format(key), str(config.get(key)) or '')
    return format_string


def draw_logo(image, logo, color):
    draw = ImageDraw.Draw(image)
    iw, ih = image.size
    image_size = iw if iw > ih else ih
    font_size = 1
    while True:
        font = ImageFont.truetype(os.path.join('fonts', 'arial.ttf'), font_size)
        tw, th = draw.textsize(logo, font)
        max_size = tw if tw > th else th
        if max_size < image_size * 0.3:
            font_size += 1
        else:
            break
    draw.text(((iw - tw) / 2, (ih - th) / 2), logo, font=font, fill=color)


def to_color(color_string):
    try:
        return tuple(int(c) for c in color_string.split(','))
    except Exception as e:
        print('[Error] Invalid color format.')
        raise e


def get_width(config):
    size = config.get('size')
    return int(float(size.split('x')[0]) * float(config.get('scale').replace('x', ''))) if size else config.get('width')


def get_height(config):
    size = config.get('size')
    return int(float(size.split('x')[1]) * float(config.get('scale').replace('x', ''))) if size else config.get('height')


def __make(option):
    configurations = load_json(os.path.join(option.config))
    output_dir = unique_path(os.path.join(option.output or '', 'images'))
    os.makedirs(output_dir)
    background_color = to_color(option.color) if option.color else (255, 255, 255)
    logo_color = to_color(option.logo_color) if option.logo_color else (0, 0, 0)
    for k, v in configurations.items():
        width = get_width(v)
        height = get_height(v)
        image = Image.new('RGB', (width, height), background_color)
        if option.logo:
            draw_logo(image, option.logo, logo_color)
        path = os.path.join(output_dir, '{}x{}.png'.format(width, height))
        with open(path, 'wb') as f:
            image.save(f, 'PNG', optimize=True)
            print('Made "{}"'.format(path))


def crop(image, width, height):
    iw, ih = image.size
    return image.crop(((iw - width) // 2,
                       (ih - height) // 2,
                       (iw + width) // 2,
                       (ih + height) // 2))


def __convert(option):
    configurations = load_json(os.path.join(option.config))
    output_dir = unique_path(os.path.join(option.output or '', 'images'))
    os.makedirs(output_dir)
    with Image.open(option.src, 'r') as src:
        for k, v in configurations.items():
            width = get_width(v)
            height = get_height(v)
            max_size = width if width > height else height
            copy = src.copy()
            if option.rotate and option.orientation:
                if v['orientation'] != option.orientation:
                    if option.rotate == 'left':
                        copy = copy.rotate(90, expand=True)
                    elif option.rotate == 'right':
                        copy = copy.rotate(-90, expand=True)
            copy.thumbnail((max_size, max_size), Image.ANTIALIAS)
            converted = copy.resize((width, height)) if option.ignore_aspect_ratio else crop(copy, width, height)
            path = os.path.join(output_dir, '{}x{}.png'.format(width, height))
            converted.save(path, 'PNG', optimize=True)
            print('Converted "{}"'.format(path))


def __set(option):
    # Load /config/xc[Xcode Version]/[app-icons|launch-images].json """
    configs = load_json(os.path.join(option.config))

    # Load Contents.json
    contents_json_path = os.path.join(option.image_assets, 'Contents.json')
    contents = load_json(contents_json_path)

    if not option.keep:
        clear_image_assets(option.image_assets, contents)

    images = list(load_images(option.src_dir))
    for image_config in contents['images']:
        keys = [k for k in image_config.keys() if k != 'filename']
        matches = {ck: cv for ck, cv in configs.items() if all([cv.get(k) == image_config[k] for k in keys])}
        if not matches:
            raise Exception('{} is not found.'.format(image_config))
        config = matches.popitem()
        for image in images:
            if image.equal_size(get_width(config[1]), get_height(config[1])):

                filename = os.path.basename(image.path)
                if not option.no_rename:
                    if option.format:
                        filename = build_file_name(config[1], option.format)
                    else:
                        filename = '{}.png'.format(config[0].replace('\\', '').replace('"', '').replace(' ', '_'))

                output_path = os.path.join(option.image_assets, filename)
                shutil.copy(image.path, output_path)
                image_config['filename'] = filename
                print('Set "{}" to "{}"'.format(image.path, output_path))

    output_contents_json(contents, contents_json_path)


def __add_make_command(subparsers):
    make_command_parser = subparsers.add_parser('make')
    make_command_parser.formatter_class = argparse.RawTextHelpFormatter
    make_command_parser.add_argument('-c', '--config',
                                     required=True,
                                     help='specify json from /config/xc[Xcode Version]/\n')
    make_command_parser.add_argument('-o', '--output',
                                     help='output directory.\n'
                                          'default: ./images/\n')
    make_command_parser.add_argument('-C', '--color',
                                     help='specify color with format R,G,B'
                                          ' ex: --color=255,255,255\n')
    make_command_parser.add_argument('-l', '--logo',
                                     help='draw logo on center of image\n')
    make_command_parser.add_argument('--logo-color',
                                     help='specify color of logo with format R,G,B\n'
                                          'ex: --logo-color=0,0,0\n')


def __add_convert_command(subparsers):
    make_command_parser = subparsers.add_parser('convert')
    make_command_parser.formatter_class = argparse.RawTextHelpFormatter
    make_command_parser.add_argument('-s', '--src',
                                     required=True,
                                     help='specify source image\n')
    make_command_parser.add_argument('-c', '--config',
                                     required=True,
                                     help='specify json from /config/xc[Xcode Version]/\n')
    make_command_parser.add_argument('-O', '--orientation',
                                     help='specify src image orientation\n'
                                          'ex: --orientation=landscape\n'
                                          'default: portrait\n')
    make_command_parser.add_argument('-r', '--rotate',
                                     help='specify rotation\n'
                                          'require: --orientation\n'
                                          'ex: --rotate=left or --rotate==right\n'
                                          'default: None\n')
    make_command_parser.add_argument('-o', '--output',
                                     help='output directory.\n'
                                          'default: ./images/\n')
    make_command_parser.add_argument('-i', '--ignore-aspect-ratio',
                                     action='store_true',
                                     default=False,
                                     help='ignore aspect ratio')


def __add_set_command(subparsers):
    set_command_parser = subparsers.add_parser('set')
    set_command_parser.formatter_class = argparse.RawTextHelpFormatter
    set_command_parser.add_argument('-s', '--src-dir',
                                    required=True,
                                    help='specify directory contains images to set\n')
    set_command_parser.add_argument('-i', '--image-assets',
                                    required=True,
                                    help='specify app-icons/launch-images directory contains "Contents.json"\n')
    set_command_parser.add_argument('-c', '--config',
                                    required=True,
                                    help='specify json from /config/xc[Xcode Version]/\n')
    set_command_parser.add_argument('-n', '--no-rename',
                                    action='store_true',
                                    default=False,
                                    help='copy to ImageAssets and set to "Contents.json" without rename\n')
    set_command_parser.add_argument('-f', '--format',
                                    help='specify file name format\n'
                                         'ex: --format=<idiom>_<orientation>_<width>x<height>.png\n'
                                         '    --> iphone_portrait_640x960.png\n'
                                         'available: idiom, orientation, subtype, minimum-system-version,'
                                         ', extent, scale, width, height\n')
    set_command_parser.add_argument('-k', '--keep',
                                    action='store_true',
                                    default=False,
                                    help='keep old files\n')


def __parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    __add_make_command(subparsers)
    __add_convert_command(subparsers)
    __add_set_command(subparsers)
    return parser.parse_args()


def main():
    args = __parse_args()
    if args.command == 'make':
        __make(args)
    elif args.command == 'convert':
        __convert(args)
    elif args.command == 'set':
        __set(args)


if __name__ == '__main__':
    main()
