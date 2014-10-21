# Projects Geometry

Here is the process that was used to generate the project information for VTransparency 

##VPINS view

The resulting view was a combination of:
  - zppmsProjectNumberInformation from warehouse
  - ArtemisActivities from warehouse
  - vw_map_Projects from datamart

This view now sits on GDB Asset as VPINS_Projects.  To process this data a python script was used to complete the following:

1. Move the view into a SDE table
2. add field to add location type

WORKING------------

3. create a table for LRM segment begin
4. create a table for LRM segment end
5. join beg and end to get segments in ETE
6. locate features along routes to map segments
7. locate features along route to map points
8. locate XY for points with a northing easting
9. Merge the resulting full point layer
10. join the table to the full points
11. join the table to the full segments

Its going to be awesome when it is done...
