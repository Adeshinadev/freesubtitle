# freesubtitle
this is a python script ran by google cloud to collect subtitle from https://opensubtitles.com

This a script used to scrape movie titles from opensubtitle, after scraping the movie it send the title via API to https://freesubtitle-dd3fc3b3d9c1.herokuapp.com/dashboard/post-titles.

This endpoint uses the movie title to search for Movies subtitle (via API) and download it to our data base.

This Scripts is ran 3 times daily to by google scheduler.
