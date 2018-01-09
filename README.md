# ConTrack_South_Sudan
ArcPy Application to Plan and Coordinate Convoy Routes in South Sudan, based off World Food Program Road Access Constraint Data

This code was the result of a final project conducted over part of a semester for a class entitled "Coding for Geospatial Applications." 
The Python code was motivated by my brother-in-laws work in South Sudan where he reviewed and coordinated trips planned by NGO field
workers. He would base his routes and safety approvals on visual analysis of static World Food Program (WFP) Access Constraint Maps.

This code takes the inputs of "Origin City" and "Destination City," which are based off OSM place names, to plot a route that only uses
roads labeled as safe and navigable by the WFP, and creates a map of the route based off shapefiles of WFP maps.
The code is also designed to provide tables that show some information on the route (paved vs unpaved) and shows if there are other NGOs
planning similar trips within the same time window. This would allow these organizations to coordinate their convoys for greater efficiency.

Though this code is somewhat limited in its working environment, and would have to be adapted (i.e.: setting workspace, etc.) it represents
my first major attempt at coding an application. Feedback or improvements are welcome.
