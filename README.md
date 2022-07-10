# Animated Bubble Sort

This repository contains a Python script for Blender V3 to create an animation showing how the [Bubble Sort algorithm](https://en.wikipedia.org/wiki/Bubble_sort) works on a small sample of ten values.

## Bubble Sort

Bubble Sort is a simple sorting algorithm that performs sweeps through the array to be sorted, comparing adjacent elements and swapping them if they are out of order (if the first element is greater than the second when sorting in the ascending order). If there was a swap in a sweep, the algorithm performs another sweep, and stops when there were no swaps in the last sweep. 

The algorithm has the worst case complexity of O(n^2) complexity, which means that the number of comparisons is proportional to the square of the imput array size. However, for small and for almost sorted arrays, it can give good performance.

## Blender Animation with Python

The animation script needs to be imported into a Blender project and run from the Scripting Menu. Due to occasional crashes during rendering (particularly with Cycles), I have frozen the initial block sizes (see the assignment to variable `sizes`) to be able to continue redering after restaring and reloading. However, the code should normally generate random sizes, using the commented out assignment statement above the one with fixed sizes. 

The script generates a set of blocks defined via meshes with varying heights as well as three materials (normal, comparison, and moving). Before generating these objects the script deletes the existing ones to enable multiple reruns. The same applies to the text label showing the progress.

Block movements use keyframe animation. Block colour changes and the progress text label changes however, use an update funcion (whenever advancing the frame) to update the objects directly, as I could not find a way to keyframe material changes to be visible in redering.

## Fully rendered video 

You can see the fully rendered video with an introductory character animation at https://www.youtube.com/watch?v=ESZMckWlN6A
