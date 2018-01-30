#ConTrack
Theoretical ArcPy Application to Plan and Coordinate Convoys between NGOs in South Sudan, based off World Food Program Road Access
Constraint Data. In order to function properly, the Workspace Environment should be reset to the filepath of the zip-file contents.

This code was the result of a final project conducted over a semester for a class entitled "Coding for Geospatial
Applications." The Python code was motivated by my brother-in-laws work in South Sudan where he reviewed and coordinated trips 
planned by NGO fieldworkers. He would base his routes and safety approvals on visual analysis of static World Food Program (WFP)
Access Constraint Maps.

This code takes the inputs of "Origin Place," "Destination Place," which are based off OSM place names, and "Travel Window"  to plot
a route that only uses roads labeled as safe and navigable by the WFP. The code-set also includes a function to integrate the latest
WFP dataset, which can be requested (with varying degrees of success). The final product is creates a map of the route based off 
shapefiles of WFP maps. The code is designed to provide tables that show  information on the route (ex: paved vs unpaved) as well as 
other planned NGO trips in the same travel window. This is to encourage convoy coordination between the NGOs for improved safety and 
effeciency.

Though this code is somewhat basic in that it needs very specific inputs (ex: spelling of place names), and the information it 
provides, it represents an initial idea and is very much a work in progress. Feedback or improvements are welcome.
