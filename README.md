# DeepMEND: Reliable and Scalable Network Metadata Geolocation from Base Station Positions

DeepMEND relies on the same input as traditional Voronoi decompositions, but provides a richer and more accurate rendering of where users are located. For more details, please refer to our paper 'DeepMEND: Reliable and Scalable Network Metadata Geolocation from Base Station Positions' published in IEEE Communications Society Conference on Sensor and Ad Hoc Communications and Networks (SECON) 2024 Conference proceeding.
The author version is available at [https://dspace.networks.imdea.org/handle/20.500.12761/1868](https://dspace.networks.imdea.org/handle/20.500.12761/1868).

Metadata geolocation, i.e., mapping information collected at a cellular Base Station (BS) to the geographical area it covers, is a central operation in the production of statistics from mobile network measurements. This task requires modeling the probability that a device attached to a BS is at a specific location, and is presently addressed with simplistic approximations based on Voronoi tessellations. As we show, Voronoi cells exhibit poor accuracy compared to real-world geolocation data, which can, in turn, reduce the reliability of research results. We propose a new approach for data-driven metadata geolocation based on a teacher-student paradigm that combines probabilistic inference and deep learning. Our DeepMEND model: (i) only needs BS positions as input, exactly like Voronoi tessellations; (ii) pro-duces geolocation maps that are 56% and 33% more accurate than legacy Voronoi and their state-of-the-art VoronoiBoost calibration, respectively; and, (iii) generates geolocation data for thousands of BSs in minutes. We assess its accuracy against real-world multi-city geolocation data of 5, 947 BSs provided by a network operator, and demonstrate the impact of its enhanced metadata geolocation on two applications use cases.

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

Our framework lets any researcher immediately and substantially improve the spatial mapping of mobile network metadata, and is aptly named **DeepMEND**.

The following figure shows some predictions of DeepMEND.
The left column shows real-word diffusion data, the middle column the Voronoi tessellation, and the right column shows the DeepMEND approach.

<img style='float:right' src="images/maps/colorbar.png" width="25%" height="100%"/>
<br>

| Operator coverage | Voronoi | DeepMEND |
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
git clone https://github.com/nds-group/DeepMEND.git
# go to the DeepMEND folder
cd DeepMEND
# install the requirements
pip install -r requirements.txt

# unzip the model
unzip DeepMEND_SDUnet_ks2_015.zip
```

First is need to import the DeepMEND class from the DeepMEND.py file:

```python
# we are developing a python library, 
# in the meantime we need to add the DeepMEND folder to the python path
#import sys
#sys.path.append('<path_to_DeepMEND_folder>')

from DeepMEND import DeepMEND
```

DeepMEND use the same input as a standard voronoi tesselation,

* **site**: set of points, i.e: base stations locations (latitude, longitude)
* **region**: the region of interest, i.e: France, Paris 
* **meter_projection**: the projection of the region, i.e: [epsg:2154](https://epsg.io/2154)
* **model_path**: the path to the model to use for the spatial diffusion estimation.
* **compute_voronoi_tessellation**: flag to compute the voronoi tessellation or not.

```python
deepMEND = DeepMEND(sites, 
                        france_region, 
                        'epsg:2154', 
                        model_path='DeepMEND_SDUnet_ks2_015',
                        compute_voronoi_tessellation = True)
```

The main method of the DeepMEND class is **get_prediction**, which return the spatial diffusion estimation and the voronoi tessellation.

```python
prediction, _ = deepMEND.get_prediction(site_index)
```

Also, the DeepMEND class has two methods to access the voronoi tessellation **get_voronoi**, and **get_all** to get all the distance matrices, the prediction and the mask of area where the prediction is not available (i.e: outside the region of interest, sea, etc).

```python
voronoi_cell_matrix = deepMEND.get_voronoi(site_index)
distance_matrix, prediction, mask = deepMEND.get_all(site_index)
```

A fully working example is provided in the `How_to.ipynb` python notebook.