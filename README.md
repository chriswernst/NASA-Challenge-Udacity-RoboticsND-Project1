## Project 1: Search and Sample Return
###### Udacity Nanodegree
###### June 2017

[//]: # (Image References)

[image1]: ./RoboticsND-Project1/misc/rockPixels.jpg
[image2]: ./RoboticsND-Project1/misc/Rock_color_analysis.jpg
[image3]: ./RoboticsND-Project1/misc/rock_thresh.jpg
[image4]: ./RoboticsND-Project1/misc/color_map.jpg
[image5]: ./RoboticsND-Project1/misc/example_grid1.jpg
[image6]: ./RoboticsND-Project1/misc/video_screenshot.jpg

###
###
###



### Overview



###### The goal of this project is to program a rover to autonomously navigate terrain, find rock samples, and to retrieve them. The project is based on Nasa's Sample Return Contest.
###
*We operated the rover through RoverSim and carried out the majority of the operations in Python.*

###
This project will cover the three primary areas of Robotics: *Perception, Decision Making*, and *Taking Action*.
###


**Perception**: Our rover is given sight by the front mount camera. The majority of this analysis takes place in `perception.py`

**Decision Making**: We decide which actions to take by analyzing our camera and sensor data given by the rover, and testing various conditional statements. This analysis is located in `decision.py`

**Action**: We execute our actions by communicating with the rover using: `drive_rover.py`

### Notebook Analysis

Our first task of this project is to take in camera images, and transform them into a useable format. 

This will be completed in four steps:
    1. Warping: converting the front mount image to a bird's eye view perspective
    2. Thresholding: separating pixels of interest from others
    3. Mapping to Rover Coordinates: maps the warped and thresholded image in rover coordinates
    4. Mapping to World Coordinates: rotates and translates the image to account for yaw, and its location on the map

**Warping** is done by leaning on the computer vision powerhouse that is `opencv`.  All we have to do is map where our ground pixels are located so that when the warp is executed, they scale correctly. This is done by placing a grid on the ground in front of the rover camera. 
![alt text][image5]

**Thresholding** is carried out by `color_thresh()` which shows the navigable terrain. The next task is to understand how to identify rocks. Using one of the rock sample images, I performed a pixel analysis to determine the appropriate thresholds for Red, Green, and Blue pixels that create the yellow of the rock. 

![alt text][image2]

Then extracted the rock Pixel Images:

![alt text][image1]

Then I ran basic statistics on the pixels determining the range and mean of the RGB values of yellow rocks. This turned out to be:

`rgb_thresh=(130,105,50)`

I then adopted the thresholding logic from `color_thresh()` and applied it to the function `rock_thresh()`, yielding:


```
above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] < rgb_thresh[2])
```

Which generated the following:

![alt text][image3]


This same approach was then applied to obstacles by developing the function `obstacle_thresh()`. 

Putting this all together allows for us to create a warped and thresholded image to display in the lower right hand corner of the video, I created the function `color_map()`.

This function takes in an image, and segments the pixels into the categories: navigable area, obstacles, and rocks.

![alt text][image4]

I then placed this image in the lower right hand corner of the video.



**Mapping to rover coordinates** is done with the aptly named `rover_coords()` function.

```
def rover_coords(binary_img):
    binary_img = binary_img[len(binary_img)//2 : , :]
    ypos, xpos = binary_img.nonzero()
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel
```

The first line of the function is nonstandard, as I had to alter it to improve `fidelity` during autonomous navigation. It essentially truncates the area in front of the rover by half. I talk a bit more about this below.

**Mapping to world coordinates** is done by first a rotation, followed a translation. The `pix_to_world()` function combines both the rotation and translation

The video that is generated and included in the project repo in `./output/test_mapping.mp4` harnesses all four of these steps:
![alt text][image6]





### Autonomous Navigation and Mapping



`decision.py` was only slightly modified to have the rover brake when a rock was nearby. The results of this are mixed. The rover must be very close to the rock samples in order to trigger the `near sample` flag.
I also attempted a conditional steering statement, but again, I did not find much success with it.



#### Launching in Autonomous Mode







 RoverSim Settings 
`1280x800`
`Quality: Good`
`35 FPS`

### Approach, Techniquies, and How to Improve

Initially, I struggled much with the `fidelity` score--the rover wouldn't make it above 20%.  These inaccuracies are mostly caused by roll and pitch angles not being equal, or near, 0.  To remedy this, I shortened the amount the rover was looking out forward. I did this alteration in function `rover_coords()` by shortening the number of rows to half of the total length of the image, like this: 
```
binary_img = binary_img[len(binary_img)//2 : , :] 
```
This alteration immediately improved the `fidelity` score, and was consistently above 60%, `mapping` reached >80%, and usually 3-5 rocks were found and one was usually picked up.

*There are many things needed to improve this code. Some of the noteable issues are:* 


When `time==1000s` the rover eventually gets stucks beneath one of the rocks in the middle. This is usually remedied by turning to +/-15 degrees for a few seconds to 	induce a 4-wheel turn.

The rover doesn't currently drive towards rocks. This can be remedied by using a conditional statement and determining where the rocks are with `rock_angles` and `rock dist`






