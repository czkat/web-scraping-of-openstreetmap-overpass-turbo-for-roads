#!/usr/bin/env python
# coding: utf-8

# ## Convert json file to geojson format
# 
# Author: Huang Xiaojing  
# Version: 1.0

# ### Import library
import argparse
import sys
import json
import os
import osgeo.osr as osr
import gdal
import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description=
    """Convert JSON format to GeoJSON format (support LineString only).
       Type of 'way' is converted, and types of 'node' and 'relation' are ignored.
       Plot features of polyline.""")
    parser.add_argument('input_json', metavar='input_json', type=str, 
                        help='input json file in geographic coordinate')
    parser.add_argument('output_geojson', metavar='output_geojson', type=str, help='output geojson in same coordinate')
    parser.add_argument('--plot', dest='plot', action='store_true', help='to plot the polylines')
    parser.add_argument('--no-plot', dest='plot', action='store_false', help='default')
    parser.set_defaults(feature=False)    
#     parser.add_argument('-plot', metavar='N', type=int, default=False,
#                         help='to plot the polylines (default:False)')

    args = parser.parse_args()
    
    return args

def convert_json_to_geojson(input_json, output_geojson):
    """
    Convert JSON format to GeoJSON format (support LineString only). 
    Type of 'way' is converted, and types of 'node' and 'relation' are ignored.
    Display features of type polyline for viewing.
    Args:
        input_json: input JSON file
        output_geojson: output GeoJSON file
    """
    
    with open(input_json) as f:
        gj = json.load(f)
        
    ### new geojson created from json
    gj1 = {}
    gj1['type'] = 'FeatureCollection'
    gj1['generator'] = gj['generator']
    gj1['copyright'] = gj['osm3s']['copyright']
    gj1['timestamp'] = gj['osm3s']['timestamp_osm_base']
    gj1['features'] = []

    for i, f in enumerate(gj['elements']):

        if f['type'] == 'way':
            pixels = []
            for p in f['geometry']:
                pixels.append([p['lon'], p['lat']])
            f1 = {}
            f1['type'] = 'Feature'
            f1['properties'] = f['tags']
            f1['bbox'] = [f['bounds']['minlon'], f['bounds']['minlat'], f['bounds']['maxlon'], f['bounds']['maxlat']]
            f1['geometry'] = {'type': 'LineString',
              'coordinates': pixels}
            f1['id'] = f['type'] + '/' + str(f['id'])
            gj1['features'].append(f1)
        else: # f['type'] == 'node' or 'relation
            continue

    # write geojson to new file
    with open(output_geojson, 'w') as f:
        # method 1: f.write(json.dumps(gj))
        json.dump(gj1, f, indent = 2)


def display_polylines(features, data=None, xlim=None, ylim=None, scaled=False):
    """
    Display features of type polyline overlaid with image data.
    Args:
        features: features of json
        xlim: axis xlim, [x0, x1]
        ylim: axis ylim, [y0, y1]
        data: numpy arrays of HWC or HW
        scaled: False (default), True for equal scale"""
    
    fig = plt.figure(figsize=(16, 16))
    ax = plt.gca() 

    if data is not None:
        plt.imshow(data)
        
    for feature in features:
        if feature['geometry']['type'] == 'LineString':
            coords = feature['geometry']['coordinates']
            # print(coords)
            columns = list(zip(*coords))
            x = columns[0]
            y = columns[1]
            ax.plot(x,y)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    if scaled:
        ax.axis('scaled')
    plt.show()
        

def main():
    args = parse_args()
    print(args)
    convert_json_to_geojson(args.input_json, args.output_geojson)
    print('saved: ', args.output_geojson)
    
    with open(args.output_geojson) as f:
        gj = json.load(f)
    
    if args.plot == True:
        display_polylines(gj['features'], scaled=True)
        

if __name__ == "__main__":
    main()

### test sample
### python convert_json_to_geojson.py './ChuZheng/sea_211.json' './ChuZheng/sea_211.geojson' --plot
### or
### python convert_json_to_geojson.py './ChuZheng/sea_211.json' './ChuZheng/sea_211.geojson'


