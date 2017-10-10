
# This script is going to logically walk through the image transformation process

# The functions will be defined in their logical order,
# then executed in their logical order in perception_step():
    
    # Begin with a front mount camera image
    # That image is then warped to be seen from above with perspect_transform()
    # That warped image is then thresholded for one of the three:
        # Navigable using color_thresh()
        # Obstacles using obstacle_thresh()
        # Rocks using rock_thresh()
    # The output image should be a binary, warped image, which is mapped to 
        # rover coordinates using rover_coords
    # Pix to world then takes this two string array and converts it world coordinates
        # by doing a rotation followed by a translation
    

import numpy as np
import cv2


# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

# This will show us the navigable space
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


# This will show us the obstacles
def obstacle_thresh(img, rgb_thresh=(130,130,130)):
    
    # this function is intended to sort out the obstacles and unnavigable
    # and color these white, while leaving the rest of the space in
    # black pixels.
    # You can alter the threshold to include rocks or not
    
    obstacle_area = np.zeros_like(img[:,:,0])

    below_thresh = (img[:,:,0] < rgb_thresh[0]) \
                    & (img[:,:,1] < rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    
    obstacle_area[below_thresh]=1
    # sets all of the 'trues' to 1
    
    # returns a binary image
    return obstacle_area


# This will show us the rocks
def rock_thresh(img, rgb_thresh=(130,105,50)):
    
    # this function is designed to return a 2 row array only showing the 
    # locations for the rock pixels
    rock_area = np.zeros_like(img[:,:,0])

    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                    & (img[:,:,1] > rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    
    rock_area[above_thresh]=1
    # sets all of the 'trues' to 1
    
    # returns a binary image
    return rock_area


# This will convert to rover coordinates and truncate values too far
# from the rover camera(in an effort to not skew the world map with bad data)
def rover_coords(binary_img):
    # Identify nonzero pixels
    
    binary_img = binary_img[len(binary_img)//2 : , :]

    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel



# Define a function to apply a rotation to pixel positions
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated



# Define a function to perform a translation
def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated



# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles



# This is used to create the threshed video showing obstacles and navigable space
def color_map(img):
    
    # The following functions will attempt to paint:
    #    - the navigable areas blue
    #    - the obstacles red
    #    - the rocks green 


        # NAVIGABLE AREA
    
    
    area = np.zeros_like(img)
    
    rgb_thresh=(160,160,160)

    bluearea=((img[:,:,0] > rgb_thresh[0]) \
             & (img[:,:,1] > rgb_thresh[1]) \
               & (img[:,:,2] > rgb_thresh[2]))
    
    
    area[bluearea]=255
        
    bluecol = area[:,:,[2]]
        

    
        # OBSTACLES
    
    area = np.zeros_like(img)

    rgb_thresh=(160,160,160)

    redarea = (img[:,:,0] < rgb_thresh[0]) \
                    & (img[:,:,1] < rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    

    area[redarea]=255
        
    redcol = area[:,:,[0]]
                 
    
    
        # ROCKS
            
    area = np.zeros_like(img)
    
    rgb_thresh=(130,105,50)
    
    # this function is designed to paint the rock pixels green, while leaving
    # the others black
    # remains in rgb
    
    greenarea = (img[:,:,0] > rgb_thresh[0]) \
                    & (img[:,:,1] > rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    
     
    area[greenarea]=255
        
    greencol = area[:,:,[1]]  
    
    
    
    # Combine all columns into one
    area = np.concatenate((redcol, greencol, bluecol), axis=2)
    
    return area



# I dont believe this function is used
def navigable(img, rgb_thresh=(160,160,160)):
    
    # this function is intended to sort out the navigable
    # space from the rest of the area and return a 2 row array of navigable
    # pixels
    
    navigable_area = np.zeros_like(img[:,:,0])

    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                    & (img[:,:,1] > rgb_thresh[1]) \
                    & (img[:,:,2] > rgb_thresh[2])
                    
    navigable_area[above_thresh]=1
    # sets all of the 'trues' to 1
    
    navigablePixels = np.nonzero(navigable_area)
    # this should be a rows, by n columns wide. The first row will be the 
    # row number(Y), and the second row will be the column number
    
                
                
    navigable_x_pixels = navigablePixels[1]
    
    navigable_y_pixels = navigablePixels[0]

    return navigable_x_pixels, navigable_y_pixels            


# I dont believe this function is used
def obstacles(img, rgb_thresh=(160,160,160)):
    
    # this function is intended to sort out the obstacles and unnavigable
    # space from the rest of the area and return a 2 row array of unnavigable
    # pixels
    
    obstacle_area = np.zeros_like(img[:,:,0])

    above_thresh = (img[:,:,0] < rgb_thresh[0]) \
                    & (img[:,:,1] < rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    
    obstacle_area[above_thresh]=1
    # sets all of the 'trues' to 1
    
    obstaclePixels = np.nonzero(obstacle_area)
    # this should be a rows, by n columns wide. The first row will be the 
    # row number(Y), and the second row will be the column number
    
                
                
    obstacle_x_pixels = obstaclePixels[1]
    
    obstacle_y_pixels = obstaclePixels[0]

    return obstacle_x_pixels, obstacle_y_pixels  

    
# I dont believe this function is used
def rock_pixels(img, rgb_thresh=(130,105,50)):
    
    # this function is designed to return a 2 row array only showing the 
    # locations for the rock pixels
    rock_area = np.zeros_like(img[:,:,0])

    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                    & (img[:,:,1] > rgb_thresh[1]) \
                    & (img[:,:,2] < rgb_thresh[2])
                    
    rock_area[above_thresh]=1
    # sets all of the 'trues' to 1
    
    rockPixels = np.nonzero(rock_area)
    # this should be a rows, by n columns wide. The first row will be the 
    # row number(Y), and the second row will be the column number
    
                
    rock_x_pixels = rockPixels[1]
    
    rock_y_pixels = rockPixels[0]

    return rock_x_pixels, rock_y_pixels






# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img
        
    # Some constants:
    img = Rover.img
    x_position = Rover.pos[0]
    y_position = Rover.pos[1]
    yaw = Rover.yaw
    
    
    # Prepare for the image warping
    scale = 10
    world_size = 200
    # to a grid where each 10x10 pixel square represents 1 square meter
    # The destination box will be 2*dst_size on each side
    dst_size = 5 
    # Set a bottom offset to account for the fact that the bottom of the image 
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    
    # 1) Define source and destination points for perspective transform
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[img.shape[1]/2 - dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - bottom_offset],
                  [img.shape[1]/2 + dst_size, img.shape[0] - 2*dst_size - bottom_offset], 
                  [img.shape[1]/2 - dst_size, img.shape[0] - 2*dst_size - bottom_offset],
                  ])
    

    
    # Threshold for navigable terrain
    
    #1) Start with a Regular Image: Rover.img

    #2) Warp the image using perspect_transform(img)
    warped = perspect_transform(img, source, destination)
    
    #3) Threshold the image using color_thresh(warped_img)
    threshed = color_thresh(warped)
    
    #4) Convert to Rover coords with rover_coords(binary_warped_img)
    x_pixel, y_pixel = rover_coords(threshed)
    
    #5) Map to world coords using rotate_pix() and translate_pix() or, simply, pix_to_world
    x_pix_world, y_pix_world = pix_to_world(x_pixel, y_pixel, x_position, y_position, yaw, world_size, scale)
    
    dist, angles = to_polar_coords(x_pixel, y_pixel)




    # Threshold for obstacles
    
    #1) Start with a Regular Image: img
    
    #2) Warp the image using perspect_transform(img):
        # already done above: warped
    
    #3) Threshold the image using obstacle_thresh(warped_img)
    obs_threshed = obstacle_thresh(warped)
    
    #4) Convert to Rover coords with rover_coords(binary_warped_img)
    x_obs_pixel, y_obs_pixel = rover_coords(obs_threshed)
    
    #5) Map to world coords using pix_to_world -- which does the rotation and translation
    x_obs_pix_world, y_obs_pix_world = pix_to_world(x_obs_pixel, y_obs_pixel, x_position, y_position, yaw, world_size, scale)
    
    
    
    
    # Threshold for rocks
    
    #1) Start with a Regular Image: img
    
    #2) Warp the image using perspect_transform(img):
        # already done above: warped
    
    #3) Threshold the image using rock_thresh(warped_img)
    rock_threshed = rock_thresh(warped)
    
    #4) Convert to Rover coords with rover_coords(binary_warped_img)
    x_rock_pixel, y_rock_pixel = rover_coords(rock_threshed)
    
    #5) Map to world coords using pix_to_world -- which does the rotation and translation
    x_rock_pix_world, y_rock_pix_world = pix_to_world(x_rock_pixel, y_rock_pixel, x_position, y_position, yaw, world_size, scale)

    # convert to polar coordinates for steering in decision.py
    rock_dist, rock_angles = to_polar_coords(x_rock_pixel, y_rock_pixel)

   
    
    # 6) Update worldmap (to be displayed on right side of screen)
    
    
    Rover.worldmap[y_pix_world, x_pix_world, 2] += 255
    
    Rover.worldmap[y_obs_pix_world, x_obs_pix_world, 0] += 3
        
    Rover.worldmap[y_rock_pix_world, x_rock_pix_world,  1] += 255
                 
                 
                  
                 
    ###### Thresholding, Rotation, Translation is now complete ######
    
        
    
    warped_color = perspect_transform(color_map(img), source, destination)

    # Update Rover.vision_image (this will be displayed on left side of screen)
    
    Rover.vision_image = warped_color



    # Update Rover pixel distances and angles
    Rover.nav_dists = dist
    Rover.nav_angles = angles
    
    Rover.rock_dists = rock_dist
    Rover.rock_angles = rock_angles
    
    
    return Rover

    
   
    

    
    

    
    











