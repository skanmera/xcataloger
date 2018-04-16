#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import json
import glob
import shutil
import argparse
from PIL import Image


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


def clear_image_assets(directory, current_config):
    for config in current_config['images']:
        filename = config.get('filename')
        if not filename:
            continue
        path = os.path.join(directory, filename)
        if not os.path.isfile(path):
            continue
        os.remove(path)
        print 'Removed {}'.format(path)


def output_json(configurations, output_path):
    images = []
    result = {'images': images, 'info': configurations['info']}
    keys = ['extent', 'idiom', 'filename', 'subtype', 'minimum-system-version', 'orientation', 'scale']
    for config in configurations['images']:
        image = {}
        for key in keys:
            if key in config.keys():
                image[key] = config[key]
        images.append(image)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)


def set_images(option):
    configurations = load_json(os.path.join(option.config))
    content_js_path = os.path.join(option.image_assets, 'Contents.json')
    requirements = load_json(content_js_path)
    clear_image_assets(option.image_assets, requirements)
    images = list(load_images(option.src_dir))
    for requirement in requirements['images']:
        keys = [k for k in requirement.keys() if k != 'filename']
        configs = {ck: cv for ck, cv in configurations.items() if all([cv.get(k) == requirement[k] for k in keys])}
        if not configs:
            continue
        config = configs.popitem()
        for image in images:
            if image.equal_size(config[1]['width'], config[1]['height']):
                requirement['filename'] = os.path.basename(image.path)
                shutil.copy2(image.path, option.image_assets)
                print 'Set "{}" to "{}"'.format(image.path, config[0])
    output_json(requirements, content_js_path)


def unique_path(path):
    directory = os.path.dirname(path)
    name, ext = os.path.splitext(os.path.basename(path))
    ext = '.{}'.format(ext) if ext else ''
    i = 1
    while os.path.exists(path):
        path = os.path.join(directory, '{}({}){}'.format(name, i, ext))
        i += 1
    return path


def make(option):
    configurations = load_json(os.path.join(option.config))
    output_dir = unique_path(os.path.join(option.output or '', 'LaunchImages'))
    os.makedirs(output_dir)
    for k, v in configurations.items():
        image = Image.new('RGBA', (v['width'], v['height']))
        path = os.path.join(output_dir, '{}.png'.format(k.replace('\\', '').replace('"', ''))).replace(' ', '_')
        with open(path, 'wb') as f:
            image.save(f, 'PNG', optimize=True)


def parser_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    make_command_parser = subparsers.add_parser('make')
    make_command_parser.add_argument('-c', '--config', required=True)
    make_command_parser.add_argument('-o', '--output')

    set_command_parser = subparsers.add_parser('set')
    set_command_parser.add_argument('-s', '--src-dir', required=True)
    set_command_parser.add_argument('-i', '--image-assets', required=True)
    set_command_parser.add_argument('-c', '--config', required=True)

    return parser.parse_args()


def main():
    args = parser_args()
    if args.command == 'make':
        make(args)
    elif args.command == 'set':
        set_images(args)


if __name__ == '__main__':
    main()
