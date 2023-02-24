# lab_task2_map
This module provides user with info about nearest places of film shooting
## How to run
You can use given information from locations.list which has approximately 20000 of movies of different years
### Parametrs
* Year of film you want to find
* Latitude of pilot point
* Longtude of pilot point
* Path to data
```
>>> python main.py 2011 41.802982, -77.856145 locations.list
```
Given comand will save file with name "Map_Movies.html".
You can also notice lines which connect our pilot point and film shooting places
This indicates how far is this points awsy from pilot point
* green - < 300
* 300 <= orange < 700
* red >= 700

![image](https://user-images.githubusercontent.com/116755445/221261919-fbfabc97-78e1-44b5-b3a6-71820dbae8ae.png)
![image](https://user-images.githubusercontent.com/116755445/221263348-04b15eb5-68ad-4249-b38f-c1c6055ba086.png)

