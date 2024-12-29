# Simplifier: Reliable and Scalable Spatial Diffusion of Mobile Network Metadata from Base Station Locations

The mapping of metadata collected at cellular Base Stations (BSs) to the geographical area they cover is a cardinal operation for a wide range of studies across many scientific disciplines. The task requires modeling the spatial diffusion of each BS, i.e., the probability that a device associated with the BS is at a specific location. While precise spatial diffusion data can be estimated from elaborate processing of comprehensive information about the Radio Access Network (RAN) deployment, researchers tend to have access to meager data about the RAN, often limited to the sole location of the BSs. This makes simplistic approximations based on Voronoi tessellation the de-facto standard approach for diffusion modeling in most of the literature relying on mobile network metadata.

Some of the studies that rely on Voronoi tessellation includes:

* [Second-level Digital Divide: A Longitudinal Study of Mobile Traffic Consumption Imbalance in France.](https://dl.acm.org/doi/10.1145/3485447.3512125)
* [News or social media? Socio-economic divide of mobile service consumption.](https://royalsocietypublishing.org/doi/10.1098/rsif.2021.0350)
* [Impact of Later-Stages COVID-19 Response Measures on Spatiotemporal Mobile Service Usage.](https://ieeexplore.ieee.org/document/9796888/)
* [Jane Jacobs in the Sky: Predicting Urban Vitality with Open Satellite Data.](https://dl.acm.org/doi/10.1145/3449257)
* [On the estimation of spatial density from mobile network operator data.](https://ieeexplore.ieee.org/document/9647984)
* [COVID-19 Flow-Maps an open geographic information system on COVID-19 and human mobility for Spain.](https://www.nature.com/articles/s41597-021-01093-5)
* [Detecting Areas of Potential High Prevalence of Chagas in Argentina.](https://dl.acm.org/doi/10.1145/3308560.3316485)
* [Inferring dynamic origin-destination flows by transport mode using mobile phone data.](https://www.sciencedirect.com/science/article/abs/pii/S0968090X18310519)
* [Joint spatial and temporal classification of mobile traffic demands.](https://ieeexplore.ieee.org/document/8057089/)
* [The Death and Life of Great Italian Cities: A Mobile Phone Data Perspective.](https://arxiv.org/abs/1603.04012)
* [Linking Users Across Domains with Location Data: Theory and Validation.](https://dl.acm.org/doi/abs/10.1145/2872427.2883002)
* [Understanding individual human mobility patterns.](https://www.nature.com/articles/nature06958)

In fact, and as we show in our work, **Voronoi cells exhibit poor accuracy when compared to real-word diffusion data**, and their use can curb the reliability of research results. 
Motivated by this observation, we propose a new approach to data-driven coverage modelling based on a teacher-student paradigm that combines probabilistic inference and deep learning. 
Our solution is 
* Expedient, as it solely relies on BS positions exactly like legacy Voronoi tessellation, 
* Credible, as it yields a 51% improvement in the coverage quality over Voronoi,
* Scalable, as it can produce coverage data for thousands of BSs in minutes. 

Our framework lets any researcher immediately and substantially improve the spatial mapping of mobile network metadata, and is aptly named **Simplifier**.

The following figure shows some predictions of Simplifier.
The left column shows real-word diffusion data, the middle column the Voronoi tessellation, and the right column shows the Simplifier approach.

<img style='float:right' src="images/maps/colorbar.png" width="25%" height="100%"/>
<br>

| Operator coverage | Voronoi | Simplifier |
|:-----------------:|:-------:|:------------:|
| <img src="images/maps/2284_p_l_t.png" width="100%" height="100%"/> | <img src="images/maps/2284_voronoi.png" width="100%" height="100%"/> | <img src="images/maps/2284_nn_best_bacelli.png" width="100%" height="100%"/>|
| <img src="images/maps/4610_p_l_t.png" width="100%" height="100%"/> | <img src="images/maps/4610_voronoi.png" width="100%" height="100%"/> | <img src="images/maps/4610_nn_best_bacelli.png" width="100%" height="100%"/>|
| <img src="images/maps/7862_p_l_t.png" width="100%" height="100%"/> | <img src="images/maps/7862_voronoi.png" width="100%" height="100%"/> | <img src="images/maps/7862_nn_best_bacelli.png" width="100%" height="100%"/>|
| <img src="images/maps/10010_p_l_t.png" width="100%" height="100%"/> | <img src="images/maps/10010_voronoi.png" width="100%" height="100%"/> | <img src="images/maps/10010_nn_best_bacelli.png" width="100%" height="100%"/>|
| <img src="images/maps/10177_p_l_t.png" width="100%" height="100%"/> | <img src="images/maps/10177_voronoi.png" width="100%" height="100%"/> | <img src="images/maps/10177_nn_best_bacelli.png" width="100%" height="100%"/>|

## Installation and Usage

Clone this repository and install the requirements:

```bash
# clone the repository
git clone https://github.com/nds-group/simplifier.git
# go to the simplifier folder
cd simplifier
# install the requirements
pip install -r requirements.txt

# unzip the model
unzip Simplifier_SDUnet_ks2_015.zip
```

First is need to import the Simplifier class from the simplifier.py file:

```python
# we are developing a python library, 
# in the meantime we need to add the simplifier folder to the python path
#import sys
#sys.path.append('<path_to_simplifier_folder>')

from simplifier import Simplifier
```

Simplifier use the same input as a standard voronoi tesselation,

* **site**: set of points, i.e: base stations locations (latitude, longitude)
* **region**: the region of interest, i.e: France, Paris 
* **meter_projection**: the projection of the region, i.e: [epsg:2154](https://epsg.io/2154)
* **model_path**: the path to the model to use for the spatial diffusion estimation.
* **compute_voronoi_tessellation**: flag to compute the voronoi tessellation or not.

```python
simplifier = Simplifier(sites, 
                        france_region, 
                        'epsg:2154', 
                        model_path='Simplifier_SDUnet_ks2_015',
                        compute_voronoi_tessellation = True)
```

The main method of the simplifier class is **get_prediction**, which return the spatial diffusion estimation and the voronoi tessellation.

```python
prediction, _ = simplifier.get_prediction(site_index)
```

Also, the simplifier class has two methods to access the voronoi tessellation **get_voronoi**, and **get_all** to get all the distance matrices, the prediction and the mask of area where the prediction is not available (i.e: outside the region of interest, sea, etc).

```python
voronoi_cell_matrix = simplifier.get_voronoi(site_index)
distance_matrix, prediction, mask = simplifier.get_all(site_index)
```
