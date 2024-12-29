import numpy as np
import json
from shapely.geometry import box as Box
from shapely.geometry import shape as Shape
from shapely.geometry import Point
from shapely.ops import transform as Shapely_transform
from pyproj import Transformer
from scipy.spatial import KDTree
from matplotlib.path import Path

from geovoronoi import voronoi_regions_from_coords

from tensorflow.keras.models import load_model
import tensorflow as tf

class DeepMEND:
    """
    DeepMEND class
    sites: list of sites in wgs84, (lat, lon)
    region: region of interest in wgs84 (geojson format)
    meter_projection: projection to use to return the coverage matrix in meters
    """

    def __init__(self, sites, region, meter_projection, model_path='DeepMEND_SDUnet_ks2_015', compute_voronoi_tessellation=True):
        self.sites = sites
        self.region = region
        
        self.meter_transform = Transformer.from_crs('epsg:4326', meter_projection).transform
        self.region_meter = Shapely_transform(self.meter_transform, self.region)

        lats, lons = zip(*self.sites)
        xs, ys = self.meter_transform(lats, lons)
        self.sites_meter = list(zip(xs, ys))
        self.kdtree = KDTree(self.sites_meter)

        self.model = load_model(model_path, custom_objects={'tf': tf})

        self.compute_voronoi_flag = compute_voronoi_tessellation
        if self.compute_voronoi_flag:
            self.voronoi_cells = self.compute_voronoi_cells()

        self.number_cells = 600
        self.spatial_resolution = 100
        self.number_neighbors = 5


    def get_area_of_interest(self, site_index):
        x, y = self.sites_meter[site_index]
        left_x = (x - (self.number_cells//2)*self.spatial_resolution)//self.spatial_resolution * self.spatial_resolution
        bottom_y = (y - (self.number_cells//2)*self.spatial_resolution)//self.spatial_resolution * self.spatial_resolution
        return left_x, bottom_y

    def discrete_shape(self, shape_meter, left_x, bottom_y):
        # matrix dims
        x, y = np.meshgrid(np.arange(self.number_cells), np.arange(self.number_cells)) # make a canvas with coordinates
        x, y = x.flatten(), y.flatten()
        points = np.vstack((y, x)).T 

        
        # polygon discrete
        if shape_meter.type == 'Polygon':
            xs, ys = shape_meter.exterior.xy
            xs = np.array(xs)
            ys = np.array(ys)

            xs_discrete_matrix = (xs - left_x)//self.spatial_resolution
            ys_discrete_matrix = (ys - bottom_y)//self.spatial_resolution

            p = Path(list(zip(ys_discrete_matrix, xs_discrete_matrix))) # make a polygon
            grid = p.contains_points(points)
            matrix = grid.reshape((self.number_cells, self.number_cells))
            matrix = 1*np.array(matrix)
            return matrix
        
        if shape_meter.type == 'MultiPolygon':
            matrix = np.zeros((self.number_cells, self.number_cells))
            for shape_meter_polygon in shape_meter:
                xs, ys = shape_meter_polygon.exterior.xy
                xs = np.array(xs)
                ys = np.array(ys)

                xs_discrete_matrix = (xs - left_x)//self.spatial_resolution
                ys_discrete_matrix = (ys - bottom_y)//self.spatial_resolution

                p = Path(list(zip(ys_discrete_matrix, xs_discrete_matrix))) # make a polygon
                grid = p.contains_points(points)
                matrix_ = grid.reshape((self.number_cells, self.number_cells))
                matrix_ = 1*np.array(matrix_)
                matrix += matrix_
            # in case of overlapping
            matrix[matrix >= 1] = 1
            return matrix
        
        raise ValueError(f'Not supported shape type {shape_meter.type}')
    
    def compute_mask(self, left_x, bottom_y):
        matrix_shape = Box(left_x, bottom_y, left_x+self.number_cells*self.spatial_resolution, bottom_y+self.number_cells*self.spatial_resolution)
        intersection_shape = matrix_shape.intersection(self.region_meter)
        matrix_mask = self.discrete_shape(intersection_shape, left_x, bottom_y)
        
        return matrix_mask
    
    def compute_distance_matrix(self, site_index, mask):

        bs_coord_x, bs_coord_y = self.sites_meter[site_index]
        bs_coord = np.array([bs_coord_x, bs_coord_y])

        left_x, bottom_y = self.get_area_of_interest(site_index)

        distance_matrix = np.zeros((4, mask.shape[0], mask.shape[1]))

        n_row = mask.shape[0]
        ys = [bottom_y + i * self.spatial_resolution for i in range(n_row)]
        xs = [left_x + i * self.spatial_resolution for i in range(n_row)]

        for y_index, y in enumerate(ys):
            for x_index, x in enumerate(xs):

                l = np.array([x, y])

                bs_distance_to_l = np.sqrt(((l - bs_coord)**2).sum())
                # avoid having zero values (sea is zero)
                bs_distance_to_l += 1

                closer_neighbords_distances_to_l, _ = self.kdtree.query(l, self.number_neighbors)
                closer_neighbords_distances_to_l = np.array(closer_neighbords_distances_to_l)
                # avoid having zero values (sea is zero)
                closer_neighbords_distances_to_l += 1

                mean_closer_neighbords_distances_to_l = np.mean(closer_neighbords_distances_to_l)
                
                values = [bs_distance_to_l] + list(closer_neighbords_distances_to_l[0:2]) + [mean_closer_neighbords_distances_to_l]
                values = np.array(values)
                
                distance_matrix[:, y_index, x_index] = values

        # distance_matrix_0 is distance to bs without taking into account the mask
        distance_matrix_0 = distance_matrix[0]
        distance_matrix = distance_matrix[1:] * mask
        
        # Exp transform
        distance_matrix = 1 - np.exp(-distance_matrix/(distance_matrix_0))

        # changes of dims
        distance_matrix_ = np.zeros((distance_matrix.shape[1], distance_matrix.shape[2], distance_matrix.shape[0]))
        for i in range(distance_matrix.shape[0]):
            distance_matrix_[:, :, i] = distance_matrix[i]
        distance_matrix = distance_matrix_

        return distance_matrix
    
    def predict(self, distance_matrix, mask):
        model_input = np.array([distance_matrix])
        prediction = self.model.predict(model_input)
        prediction = prediction[0]
        prediction = np.squeeze(prediction)

        prediction[prediction <= 0] = 1e-9
        prediction = 10**(-1 / prediction )
        prediction *= mask
        prediction /= prediction.sum()

        return prediction
    
    def get_all(self, site_index):
        site = self.sites[site_index]
        left_x, bottom_y = self.get_area_of_interest(site_index)
        mask = self.compute_mask(left_x, bottom_y)
        distance_matrix = self.compute_distance_matrix(site_index, mask)
        prediction = self.predict(distance_matrix, mask)

        return distance_matrix, prediction, mask

    def get_prediction(self, site_index):
        _, prediction, mask,  = self.get_all(site_index)

        return prediction, mask
    
    def compute_voronoi_cells(self):
        if not self.compute_voronoi_flag:
            raise Exception('Voronoi cells not computed')

        region_polys, region_pts = voronoi_regions_from_coords(self.sites, self.region)

        # Check that the Voronoi polygons are valid
        if len(self.sites) != len(region_pts):
            # show a sample of the points that were assigned to more than one polygon
            print(list(filter(lambda k_v: len(k_v[1]) > 1, region_pts.items()))[0:10])
            raise Exception('Number of sites and assignments do not match')

        voronoi_cells = [None for i in range(len(self.sites))]
        for voronoi_index, pts_index,  in region_pts.items():
            pts_index = pts_index[0] # only one point per polygon
            voronoi_cells[pts_index] = region_polys[voronoi_index]

        for index, voronoi_cell in enumerate(voronoi_cells):
            if voronoi_cell.type == 'MultiPolygon':
                lat, lon = self.sites[index]
                for polygon in voronoi_cell:
                    if Point(lat, lon).within(polygon):
                        break
                voronoi_cells[index] = polygon

        return voronoi_cells
    

    def get_voronoi(self, site_index):

        if not self.compute_voronoi_flag:
            raise ValueError('compute_voronoi_tessellation argument is False')

        left_x, bottom_y = self.get_area_of_interest(site_index)
        voronoi_cell = self.voronoi_cells[site_index]
        voronoi_cell_meter = Shapely_transform(self.meter_transform, voronoi_cell)
        voronoi_cell_matrix = self.discrete_shape(voronoi_cell_meter, left_x, bottom_y)
        return voronoi_cell_matrix